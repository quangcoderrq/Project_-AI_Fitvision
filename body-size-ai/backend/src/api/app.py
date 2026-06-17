"""
FastAPI Application
Main API endpoints for body size prediction.
"""
from datetime import datetime

import os
import sys
import secrets
from typing import List, Optional
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Add project root and local lib to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(project_root, 'lib'))
sys.path.insert(0, project_root)

from src.database import get_db, engine, Base, migrate_db
from src.models import db_models
from src.models.db_models import User, APIToken, PredictionLog
from src.utils.auth import get_password_hash, verify_password, create_access_token, get_current_user

from src.api.schemas import (
    PredictionRequest, 
    PredictionResponse,
    BrandsResponse,
    BrandInfo,
    HealthResponse,
    ErrorResponse,
    Measurements,
    MatchDetail,
    GarmentSizeResult,
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UserProfileResponse,
    SubscriptionRequest,
    FeedbackRequest,
    PredictionLogResponse
)
from src.models.predict import BodyPredictor
from src.sizing.size_mapper import SizeMapper
from src.utils.config import Config
from src.utils.image_utils import ImageUtils
from src.preprocessing.image_preprocessor import ImagePreprocessor
from src.preprocessing.image_validator import ImageValidator


# Global instances
predictor: BodyPredictor = None
size_mapper: SizeMapper = None
image_preprocessor: ImagePreprocessor = None
image_validator: ImageValidator = None


def get_user_from_request(
    db: Session = Depends(get_db),
    x_api_token: Optional[str] = Header(None, alias="X-API-Token"),
    current_user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    """Get user from request headers (either JWT auth or custom API token header)."""
    if current_user:
        return current_user
        
    if x_api_token:
        # Check special guest token
        if x_api_token == "fv_demo_guest_key":
            guest_user = db.query(User).filter(User.email == "guest@fitvision.ai").first()
            if not guest_user:
                # Seed guest user if not exists
                guest_user = User(
                    email="guest@fitvision.ai",
                    hashed_password=get_password_hash("guest_pwd_9988"),
                    active_plan="Free"
                )
                db.add(guest_user)
                db.commit()
                db.refresh(guest_user)
                
                guest_token = APIToken(
                    user_id=guest_user.id,
                    token="fv_demo_guest_key",
                    is_active=True
                )
                db.add(guest_token)
                db.commit()
            return guest_user
            
        # Check database for custom API Token
        db_token = db.query(APIToken).filter(
            APIToken.token == x_api_token, 
            APIToken.is_active == True
        ).first()
        if db_token:
            return db_token.user
            
    return None


def require_authorized_user(
    db: Session = Depends(get_db),
    x_api_token: Optional[str] = Header(None, alias="X-API-Token"),
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Dependency to enforce valid API Token or user JWT session."""
    user = get_user_from_request(db, x_api_token, current_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Valid X-API-Token or JWT Bearer authorization is required."
        )
    return user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global predictor, size_mapper, image_preprocessor, image_validator
    
    # Startup
    print("Starting Body Size AI API...")
    
    # Ensure database tables are created and migrated
    Base.metadata.create_all(bind=engine)
    migrate_db()
    
    # Ensure guest account is seeded
    db = next(get_db())
    guest_user = db.query(User).filter(User.email == "guest@fitvision.ai").first()
    if not guest_user:
        guest_user = User(
            email="guest@fitvision.ai",
            hashed_password=get_password_hash("guest_pwd_9988"),
            active_plan="Free"
        )
        db.add(guest_user)
        db.commit()
        db.refresh(guest_user)
        
        guest_token = APIToken(
            user_id=guest_user.id,
            token="fv_demo_guest_key",
            is_active=True
        )
        db.add(guest_token)
        db.commit()
        print("Default Guest user seeded successfully!")
    else:
        # Make sure guest has guest token
        guest_token = db.query(APIToken).filter(APIToken.token == "fv_demo_guest_key").first()
        if not guest_token:
            guest_token = APIToken(
                user_id=guest_user.id,
                token="fv_demo_guest_key",
                is_active=True
            )
            db.add(guest_token)
            db.commit()
            
    db.close()
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Initialize components
    image_preprocessor = ImagePreprocessor()
    image_validator = ImageValidator()
    
    # Initialize size mapper
    size_chart_path = Config.SIZE_CHART_PATH
    if os.path.exists(size_chart_path):
        size_mapper = SizeMapper(size_chart_path)
    else:
        size_mapper = SizeMapper()
    
    # Initialize predictor
    if Config.is_model_available():
        predictor = BodyPredictor(
        model_path=Config.MODEL_PATH,
        scaler_path=Config.SCALER_PATH,
        shirt_model_path=Config.MODEL_SHIRT_PATH,
        shirt_scaler_path=Config.SCALER_SHIRT_PATH,
        pants_model_path=Config.MODEL_PANTS_PATH,
        pants_scaler_path=Config.SCALER_PANTS_PATH,
        )
        print("Model loaded successfully!")
    else:
        predictor = BodyPredictor()
        print("Warning: Model not found. Train the model first.")
        print(f"Expected model path: {Config.MODEL_PATH}")
    
    print("API ready!")
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if predictor:
        predictor.close()


# Create FastAPI app
app = FastAPI(
    title="Body Size AI",
    description="AI-powered body size recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get frontend directory path (Vite production build folder)
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    'frontend-react',
    'dist'
)

# Ensure the frontend build directories exist at startup so StaticFiles mounting doesn't crash.
# These will be populated when the React app is built.
os.makedirs(os.path.join(FRONTEND_DIR, 'assets'), exist_ok=True)

# Mount static files for assets (Vite compiles all CSS/JS inside assets/)
app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, 'assets')), name="assets")

# Mount public assets if they exist (Vite copies public files like favicon/icons to the dist root)
# We can also mount the root directory as a static mount but with low priority.
# To keep it simple, we serve favicon.svg and icons.svg directly or mount them if they are requested.
@app.get("/favicon.svg", response_class=FileResponse)
async def favicon():
    path = os.path.join(FRONTEND_DIR, 'favicon.svg')
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"status": "error", "message": "Favicon not found"})

@app.get("/icons.svg", response_class=FileResponse)
async def icons():
    path = os.path.join(FRONTEND_DIR, 'icons.svg')
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse({"status": "error", "message": "Icons not found"})


@app.get("/", response_class=FileResponse)
async def root():
    """Serve React E-Commerce Demo."""
    index_path = os.path.join(FRONTEND_DIR, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({
        "status": "error", 
        "message": "Frontend build files not found. Please run 'npm run build' inside 'frontend-react' directory first."
    })


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=predictor is not None and predictor.is_ready(),
        version="1.0.0"
    )


@app.get("/brands", response_model=BrandsResponse)
async def get_brands():
    """Get available brands."""
    brands = []
    
    for brand_name in size_mapper.get_available_brands():
        regions = size_mapper.brand_rules.get_available_regions(brand_name)
        default_region = 'asia' if 'asia' in regions else (regions[0] if regions else 'asia')
        
        shirt_chart_m = size_mapper.brand_rules.get_size_chart(brand_name, default_region, 'male', 'shirt')
        shirt_chart_f = size_mapper.brand_rules.get_size_chart(brand_name, default_region, 'female', 'shirt')
        
        sizes_male = list(shirt_chart_m.keys()) if shirt_chart_m else []
        sizes_female = list(shirt_chart_f.keys()) if shirt_chart_f else []
        
        available_genders = []
        if sizes_male:
            available_genders.append('male')
        if sizes_female:
            available_genders.append('female')
        
        all_sizes = list(set(sizes_male + sizes_female))
        # Sort sizes
        size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
        all_sizes.sort(key=lambda x: size_order.index(x) if x in size_order else 999)
        
        garment_types = size_mapper.brand_rules.get_garment_types(brand_name, default_region, 'male')
        
        brands.append(BrandInfo(
            name=brand_name,
            available_regions=regions,
            available_genders=available_genders,
            sizes=all_sizes,
            garment_types=garment_types
        ))
    
    return BrandsResponse(
        brands=brands,
        default_brand=Config.DEFAULT_BRAND
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_size(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    authorized_user: User = Depends(require_authorized_user)
):
    """
    Predict clothing size from image and measurements.
    
    - **image**: Base64 encoded full-body image
    - **height**: Height in centimeters (100-250)
    - **weight**: Weight in kilograms (30-300)
    - **gender**: 'male' or 'female'
    - **brand**: Brand name (default: 'generic')
    """
    global predictor, size_mapper, image_preprocessor, image_validator
    
    # Check if model is loaded
    if not predictor or not predictor.is_ready():
        return PredictionResponse(
            success=False,
            error="Model not loaded. Please train the model first.",
            confidence=0.0
        )
    
    try:
        # Decode image
        image = ImageUtils.from_base64(request.image)
        if image is None:
            return PredictionResponse(
                success=False,
                error="Failed to decode image. Please provide a valid base64 image.",
                confidence=0.0
            )
        
        # Validate image
        is_valid, errors, warnings = image_validator.validate_array(image)
        if not is_valid:
            return PredictionResponse(
        success=False,
        error=f"Invalid image: {', '.join(errors)}",
        confidence=0.0
    )

        image = image_validator.resize_if_needed(image)
        processed_image = image_preprocessor.preprocess(image)
        
        # Predict body measurements
        result = predictor.predict_from_image(
            processed_image,
            height_cm=request.height,
            weight_kg=request.weight,
            gender=request.gender,
            image_type=request.image_type,
            ignore_baggy_warning=request.ignore_baggy_warning
        )
        
        if not result['success']:
            return PredictionResponse(
                success=False,
                error=result.get('error', 'Prediction failed'),
                confidence=0.0
            )
        
        # Map to size (overall - backward compatible)
        size_result = size_mapper.map_size(
            measurements=result['measurements'] if result.get('measurements') else {},
            gender=request.gender,
            brand=request.brand,
            region=request.region
        )
        
        # Map to detailed sizes (shirt + pants)
        detailed_result = size_mapper.map_size_detailed(
            measurements=result['measurements'] if result.get('measurements') else {},
            gender=request.gender,
            brand=request.brand,
            region=request.region
        )
        
        # Build match details
        match_details = {}
        for measure, detail in size_result.get('match_details', {}).items():
            match_details[measure] = MatchDetail(
                value=detail['value'],
                range=detail['range'],
                status=detail['status'],
                score=detail['score']
            )
        
        # Build shirt size result
        shirt_data = detailed_result.get('shirt', {})
        shirt_match = {}
        for m, d in shirt_data.get('match_details', {}).items():
            shirt_match[m] = MatchDetail(value=d['value'], range=d['range'], status=d['status'], score=d['score'])
        shirt_size = GarmentSizeResult(
            recommended_size=shirt_data.get('recommended_size'),
            confidence=shirt_data.get('confidence', 0),
            alternative_sizes=shirt_data.get('alternative_sizes', []),
            match_details=shirt_match,
            reason=shirt_data.get('reason', '')
        )
        
        # Build pants size result
        pants_data = detailed_result.get('pants', {})
        pants_match = {}
        for m, d in pants_data.get('match_details', {}).items():
            pants_match[m] = MatchDetail(value=d['value'], range=d['range'], status=d['status'], score=d['score'])
        pants_size = GarmentSizeResult(
            recommended_size=pants_data.get('recommended_size'),
            confidence=pants_data.get('confidence', 0),
            alternative_sizes=pants_data.get('alternative_sizes', []),
            match_details=pants_match,
            reason=pants_data.get('reason', '')
        )
        
        pred_size = size_result['recommended_size'] if result.get('measurements') else None
        confidence = min(result['confidence'], size_result['confidence']) if result.get('measurements') else 0.0
        
        # Log prediction to database
        log_id = None
        measurements = result.get("measurements") or {}

        if pred_size:
            log_entry = PredictionLog(
                user_id=authorized_user.id,

                height=request.height,
                weight=request.weight,
                gender=request.gender,
                brand=request.brand,
                region=request.region,
                garment_type=request.garment_type,

                predicted_size=pred_size,
                shirt_size=shirt_size.recommended_size if shirt_size else None,
                pants_size=pants_size.recommended_size if pants_size else None,
                confidence=confidence,
                pose_quality=result.get("pose_quality"),
                
                model_version="v1.0",
                prediction_source="production",
                is_training_sample=False,

                chest=measurements.get("chest"),
                waist=measurements.get("waist"),
                hip=measurements.get("hip"),
                shoulder_width_cm=measurements.get("shoulder_width_cm"),
                back_length=measurements.get("back_length"),
                inseam=measurements.get("inseam"),
                thigh_circumference=measurements.get("thigh_circumference"),
                neck_circumference=measurements.get("neck_circumference"),
                arm_circumference=measurements.get("arm_circumference"),
            )

            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            log_id = log_entry.id
            
        return PredictionResponse(
            success=True,
            prediction_log_id=log_id,
            pose_quality=result.get("pose_quality"),
            require_user_confirmation=result.get('require_user_confirmation', False),
            baggy_clothes_detected=result.get('baggy_clothes_detected', False),
            warning_message=result.get('warning_message'),
            predicted_size=pred_size,
            confidence=confidence,
            shirt_size=shirt_size if result.get('measurements') else None,
            pants_size=pants_size if result.get('measurements') else None,
            measurements=Measurements(**result['measurements']) if result.get('measurements') else None,
            alternative_sizes=size_result['alternative_sizes'] if result.get('measurements') else [],
            match_details=match_details if result.get('measurements') else {},
            brand=request.brand,
            gender=request.gender,
            bmi=result.get('bmi'),
            error=None
        )
        
    except Exception as e:
        return PredictionResponse(
            success=False,
            error=f"Prediction error: {str(e)}",
            confidence=0.0
        )


@app.post("/predict/upload", response_model=PredictionResponse)
async def predict_size_upload(
    image: UploadFile = File(...),
    height: float = Form(..., ge=100, le=250),
    weight: float = Form(..., ge=30, le=300),
    gender: str = Form(default="male"),
    brand: str = Form(default="generic"),
    region: str = Form(default="asia"),
    image_type: str = Form(default="full"),
    ignore_baggy_warning: bool = Form(default=False),
    db: Session = Depends(get_db),
    authorized_user: User = Depends(require_authorized_user)
):
    """
    Predict clothing size from uploaded image file.
    
    Alternative to /predict that accepts file upload instead of base64.
    """
    global predictor
    
    # Check if model is loaded
    if not predictor or not predictor.is_ready():
        return PredictionResponse(
            success=False,
            error="Model not loaded. Please train the model first.",
            confidence=0.0
        )
    
    try:
        # Read image file
        contents = await image.read()
        image_array = ImageUtils.from_bytes(contents)
        
        if image_array is None:
            return PredictionResponse(
                success=False,
                error="Failed to read image file",
                confidence=0.0
            )
        
        # Validate
        is_valid, errors, _ = image_validator.validate_array(image_array)
        if not is_valid:
            return PredictionResponse(
                success=False,
                error=f"Invalid image: {', '.join(errors)}",
                confidence=0.0
            )
        
        # Resize small images before preprocessing
        image_array = image_validator.resize_if_needed(image_array)

        # Preprocess
        processed = image_preprocessor.preprocess(image_array)
        
        # Predict
        result = predictor.predict_from_image(
            processed,
            height_cm=height,
            weight_kg=weight,
            gender=gender.lower(),
            image_type=image_type,
            ignore_baggy_warning=ignore_baggy_warning
        )
        
        if not result['success']:
            return PredictionResponse(
                success=False,
                error=result.get('error', 'Prediction failed'),
                confidence=0.0
            )
        
        # Map to size (overall - backward compatible)
        size_result = size_mapper.map_size(
            measurements=result['measurements'] if result.get('measurements') else {},
            gender=gender.lower(),
            brand=brand.lower(),
            region=region.lower()
        )
        
        # Map to detailed sizes (shirt + pants)
        detailed_result = size_mapper.map_size_detailed(
            measurements=result['measurements'] if result.get('measurements') else {},
            gender=gender.lower(),
            brand=brand.lower(),
            region=region.lower()
        )
        
        # Build match details
        match_details = {}
        for measure, detail in size_result.get('match_details', {}).items():
            match_details[measure] = MatchDetail(
                value=detail['value'],
                range=detail['range'],
                status=detail['status'],
                score=detail['score']
            )
            
        # Build shirt size result
        shirt_data = detailed_result.get('shirt', {})
        shirt_match = {}
        for m, d in shirt_data.get('match_details', {}).items():
            shirt_match[m] = MatchDetail(value=d['value'], range=d['range'], status=d['status'], score=d['score'])
        shirt_size = GarmentSizeResult(
            recommended_size=shirt_data.get('recommended_size'),
            confidence=shirt_data.get('confidence', 0),
            alternative_sizes=shirt_data.get('alternative_sizes', []),
            match_details=shirt_match,
            reason=shirt_data.get('reason', '')
        )
        
        # Build pants size result
        pants_data = detailed_result.get('pants', {})
        pants_match = {}
        for m, d in pants_data.get('match_details', {}).items():
            pants_match[m] = MatchDetail(value=d['value'], range=d['range'], status=d['status'], score=d['score'])
        pants_size = GarmentSizeResult(
            recommended_size=pants_data.get('recommended_size'),
            confidence=pants_data.get('confidence', 0),
            alternative_sizes=pants_data.get('alternative_sizes', []),
            match_details=pants_match,
            reason=pants_data.get('reason', '')
        )
        
        pred_size = size_result['recommended_size'] if result.get('measurements') else None
        confidence = min(result['confidence'], size_result['confidence']) if result.get('measurements') else 0.0
        
        # Log prediction to database
        if pred_size:
            log_entry = PredictionLog(
                user_id=authorized_user.id,
                height=height,
                weight=weight,
                gender=gender.lower(),
                brand=brand.lower(),
                predicted_size=pred_size,
                confidence=confidence
            )
            db.add(log_entry)
            db.commit()
            
        return PredictionResponse(
            success=True,
            require_user_confirmation=result.get('require_user_confirmation', False),
            baggy_clothes_detected=result.get('baggy_clothes_detected', False),
            warning_message=result.get('warning_message'),
            predicted_size=pred_size,
            confidence=confidence,
            shirt_size=shirt_size if result.get('measurements') else None,
            pants_size=pants_size if result.get('measurements') else None,
            measurements=Measurements(**result['measurements']) if result.get('measurements') else None,
            alternative_sizes=size_result['alternative_sizes'] if result.get('measurements') else [],
            match_details=match_details if result.get('measurements') else {},
            brand=brand.lower(),
            gender=gender.lower(),
            bmi=result.get('bmi'),
            error=None
        )
        
    except Exception as e:
        return PredictionResponse(
            success=False,
            error=f"Prediction error: {str(e)}",
            confidence=0.0
        )


# ==========================================
# AUTHENTICATION & ACCOUNT ENDPOINTS
# ==========================================

@app.post("/api/auth/register", response_model=AuthResponse)
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng bởi một tài khoản khác."
        )
    
    # Create new user
    hashed_pwd = get_password_hash(request.password)
    new_user = User(
        full_name=request.full_name,
        email=request.email,
        hashed_password=hashed_pwd,
        active_plan="Free"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate API Token
    api_token_val = "fv_live_" + secrets.token_hex(12)
    api_token = APIToken(
        user_id=new_user.id,
        token=api_token_val,
        is_active=True
    )
    db.add(api_token)
    db.commit()
    
    # Create Access Token
    access_token = create_access_token(data={"sub": new_user.email})
    return AuthResponse(
        access_token=access_token,
        full_name=new_user.full_name,
        email=new_user.email,
        active_plan=new_user.active_plan,
        api_token=api_token_val
    )


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác."
        )
        
    # Get active token
    api_token_record = db.query(APIToken).filter(
        APIToken.user_id == user.id, 
        APIToken.is_active == True
    ).first()
    
    api_token_val = api_token_record.token if api_token_record else ""
    if not api_token_val:
        # Generate token if missing
        api_token_val = "fv_live_" + secrets.token_hex(12)
        api_token = APIToken(
            user_id=user.id,
            token=api_token_val,
            is_active=True
        )
        db.add(api_token)
        db.commit()
        
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(
        access_token=access_token,
        full_name=user.full_name,
        email=user.email,
        active_plan=user.active_plan,
        api_token=api_token_val
    )


@app.get("/api/auth/me", response_model=UserProfileResponse)
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    api_token_record = db.query(APIToken).filter(
        APIToken.user_id == current_user.id, 
        APIToken.is_active == True
    ).first()
    api_token_val = api_token_record.token if api_token_record else ""
    
    return UserProfileResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        active_plan=current_user.active_plan,
        api_token=api_token_val
    )


@app.post("/api/auth/regenerate-token", response_model=UserProfileResponse)
async def regenerate_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    # Deactivate current tokens
    db.query(APIToken).filter(APIToken.user_id == current_user.id).update({"is_active": False})
    
    # Generate new one
    api_token_val = "fv_live_" + secrets.token_hex(12)
    api_token = APIToken(
        user_id=current_user.id,
        token=api_token_val,
        is_active=True
    )
    db.add(api_token)
    db.commit()
    
    return UserProfileResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        active_plan=current_user.active_plan,
        api_token=api_token_val
    )


@app.post("/api/auth/subscribe", response_model=UserProfileResponse)
async def subscribe(request: SubscriptionRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    current_user.active_plan = request.plan_name
    db.commit()
    
    # Ensure there is an active API token
    api_token_record = db.query(APIToken).filter(
        APIToken.user_id == current_user.id, 
        APIToken.is_active == True
    ).first()
    api_token_val = api_token_record.token if api_token_record else ""
    if not api_token_val:
        api_token_val = "fv_live_" + secrets.token_hex(12)
        api_token = APIToken(
            user_id=current_user.id,
            token=api_token_val,
            is_active=True
        )
        db.add(api_token)
        db.commit()
        
    return UserProfileResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        active_plan=current_user.active_plan,
        api_token=api_token_val
    )


# ==========================================
# ANALYTICS & LOGGING ENDPOINTS
# ==========================================

@app.get("/api/analytics/logs", response_model=List[PredictionLogResponse])
async def get_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    # Get user logs sorted by creation date descending
    logs = db.query(PredictionLog).filter(
        PredictionLog.user_id == current_user.id
    ).order_by(PredictionLog.created_at.desc()).limit(100).all()
    
    result_logs = []
    for log in logs:
        result_logs.append(PredictionLogResponse(
            id=log.id,
            height=log.height,
            weight=log.weight,
            gender=log.gender,
            brand=log.brand,
            predicted_size=log.predicted_size or "N/A",
            confidence=log.confidence,
            created_at=log.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ))
        
    return result_logs


@app.get("/api/analytics/stats")
async def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        
    # Count database logs
    total_calls = db.query(PredictionLog).filter(PredictionLog.user_id == current_user.id).count()
    
    # Check plan limit metrics
    if current_user.active_plan == "Free":
        return {
            "total_calls": total_calls,
            "cvr_increase": 0.0,
            "returns_reduction": 0.0,
            "api_success_rate": 100.0 if total_calls > 0 else 0.0,
            "monthly_limit": 100,
            "monthly_usage_percentage": min(100.0, (total_calls / 100.0) * 100.0) if total_calls > 0 else 0.0
        }
    else:
        limit = 2000 if current_user.active_plan == "Starter" else (10000 if current_user.active_plan == "Professional" else 1000000)
        percentage = min(100.0, (total_calls / limit) * 100.0) if limit > 0 else 0.0
        
        return {
            "total_calls": total_calls,
            "cvr_increase": 18.4,
            "returns_reduction": 32.1,
            "api_success_rate": 99.8,
            "monthly_limit": limit,
            "monthly_usage_percentage": percentage
        }

@app.post("/api/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db),
    authorized_user: User = Depends(require_authorized_user)
):
    log = db.query(PredictionLog).filter(
        PredictionLog.id == request.prediction_log_id,
        PredictionLog.user_id == authorized_user.id
    ).first()

    if not log:
        raise HTTPException(
            status_code=404,
            detail="Prediction log not found"
        )

    log.selected_shirt_size = request.selected_shirt_size
    log.selected_pants_size = request.selected_pants_size

    log.shirt_feedback = request.shirt_feedback
    log.pants_feedback = request.pants_feedback

    log.overall_feedback = request.overall_feedback
    log.issue_area = request.issue_area
    log.feedback_note = request.feedback_note
    log.returned_or_exchanged = request.returned_or_exchanged
    log.feedback_created_at = datetime.utcnow()

    score_map = {
    "fit": 5,
    "loose": 3,
    "tight": 3,
    "wrong": 1,
}

    log.feedback_score = score_map.get(request.overall_feedback, 0)
    log.is_training_sample = request.overall_feedback in ["fit", "tight", "loose", "wrong"]
    
    db.commit()

    return {
        "success": True,
        "message": "Feedback saved successfully"
    }
# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )
