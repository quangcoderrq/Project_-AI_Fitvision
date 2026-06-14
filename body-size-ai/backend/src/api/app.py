"""
FastAPI Application
Main API endpoints for body size prediction.
"""

import os
import sys
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Add project root and local lib to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(project_root, 'lib'))
sys.path.insert(0, project_root)

from src.api.schemas import (
    PredictionRequest, 
    PredictionResponse,
    BrandsResponse,
    BrandInfo,
    HealthResponse,
    ErrorResponse,
    Measurements,
    MatchDetail,
    GarmentSizeResult
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global predictor, size_mapper, image_preprocessor, image_validator
    
    # Startup
    print("Starting Body Size AI API...")
    
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
            scaler_path=Config.SCALER_PATH
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
async def predict_size(request: PredictionRequest):
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
        
        # Preprocess image
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
        
        return PredictionResponse(
            success=True,
            require_user_confirmation=result.get('require_user_confirmation', False),
            baggy_clothes_detected=result.get('baggy_clothes_detected', False),
            warning_message=result.get('warning_message'),
            predicted_size=size_result['recommended_size'] if result.get('measurements') else None,
            confidence=min(result['confidence'], size_result['confidence']) if result.get('measurements') else 0.0,
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
    ignore_baggy_warning: bool = Form(default=False)
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
        
        return PredictionResponse(
            success=True,
            require_user_confirmation=result.get('require_user_confirmation', False),
            baggy_clothes_detected=result.get('baggy_clothes_detected', False),
            warning_message=result.get('warning_message'),
            predicted_size=size_result['recommended_size'] if result.get('measurements') else None,
            confidence=min(result['confidence'], size_result['confidence']) if result.get('measurements') else 0.0,
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
