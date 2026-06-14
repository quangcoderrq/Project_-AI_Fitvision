"""
API Schemas Module
Pydantic models for request/response validation.
Extended with detailed shirt/pants sizing.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class PredictionRequest(BaseModel):
    """Request model for size prediction."""
    
    image: str = Field(
        ..., 
        description="Base64 encoded image"
    )
    height: float = Field(
        ..., 
        ge=100, 
        le=250,
        description="Height in centimeters (100-250)"
    )
    weight: float = Field(
        ..., 
        ge=30, 
        le=300,
        description="Weight in kilograms (30-300)"
    )
    gender: str = Field(
        default="male",
        description="Gender: 'male' or 'female'"
    )
    brand: str = Field(
        default="generic",
        description="Brand name for size chart"
    )
    region: str = Field(
        default="asia",
        description="Region/Standard for size chart (e.g., asia, us, eu)"
    )
    image_type: str = Field(
        default="full",
        description="Type of image: 'full', 'upper', or 'lower'"
    )
    ignore_baggy_warning: bool = Field(
        default=False,
        description="If true, ignores baggy clothes warning and proceeds with prediction"
    )
    
    @validator('gender')
    def validate_gender(cls, v):
        if v.lower() not in ['male', 'female']:
            raise ValueError("Gender must be 'male' or 'female'")
        return v.lower()
    
    @validator('brand')
    def validate_brand(cls, v):
        return v.lower()
        
    @validator('region')
    def validate_region(cls, v):
        return v.lower()
        
    @validator('image_type')
    def validate_image_type(cls, v):
        if v.lower() not in ['full', 'upper', 'lower']:
            raise ValueError("image_type must be 'full', 'upper', or 'lower'")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "image": "base64_encoded_image_string",
                "height": 170,
                "weight": 65,
                "gender": "male",
                "brand": "uniqlo",
                "region": "asia",
                "image_type": "full",
                "ignore_baggy_warning": False
            }
        }


class Measurements(BaseModel):
    """Body measurements — expanded to 9 measurements."""
    
    chest: float = Field(..., description="Chest circumference in cm")
    waist: float = Field(..., description="Waist circumference in cm")
    hip: float = Field(..., description="Hip circumference in cm")
    shoulder_width_cm: float = Field(default=0, description="Shoulder width in cm")
    back_length: float = Field(default=0, description="Back length in cm")
    inseam: float = Field(default=0, description="Inseam length in cm")
    thigh_circumference: float = Field(default=0, description="Thigh circumference in cm")
    neck_circumference: float = Field(default=0, description="Neck circumference in cm")
    arm_circumference: float = Field(default=0, description="Arm circumference in cm")


class MatchDetail(BaseModel):
    """Details about how a measurement matches a size range."""
    
    value: float
    range: List[float]
    status: str  # 'fit', 'tight', 'loose'
    score: float


class GarmentSizeResult(BaseModel):
    """Size recommendation for a specific garment type (shirt or pants)."""
    
    recommended_size: Optional[str] = Field(None, description="Recommended size")
    confidence: float = Field(0.0, description="Confidence score (0-1)")
    alternative_sizes: List[str] = Field(default=[], description="Alternative size options")
    match_details: Dict[str, MatchDetail] = Field(default={}, description="Measurement match details")
    reason: str = Field(default="", description="Reason for recommendation in Vietnamese")


class PredictionResponse(BaseModel):
    """Response model for size prediction — with shirt/pants separation."""
    
    success: bool = Field(..., description="Whether prediction was successful")
    
    # User Confirmation Flow
    require_user_confirmation: bool = Field(False, description="If true, frontend should ask user to confirm before proceeding")
    baggy_clothes_detected: bool = Field(False, description="Whether baggy clothes were detected")
    warning_message: Optional[str] = Field(None, description="Warning message to show user")
    
    # Overall size (backward compatible)
    predicted_size: Optional[str] = Field(None, description="Recommended overall size")
    confidence: float = Field(0.0, description="Overall confidence score (0-1)")
    
    # Detailed sizing (NEW)
    shirt_size: Optional[GarmentSizeResult] = Field(None, description="Shirt size recommendation")
    pants_size: Optional[GarmentSizeResult] = Field(None, description="Pants size recommendation")
    
    # Measurements
    measurements: Optional[Measurements] = Field(
        None, 
        description="Predicted body measurements (9 values)"
    )
    alternative_sizes: List[str] = Field(
        default=[], 
        description="Alternative size options"
    )
    match_details: Dict[str, MatchDetail] = Field(
        default={},
        description="How measurements match size ranges"
    )
    brand: str = Field(default="generic", description="Brand used")
    gender: str = Field(default="male", description="Gender")
    bmi: Optional[float] = Field(None, description="Calculated BMI")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "require_user_confirmation": False,
                "baggy_clothes_detected": False,
                "warning_message": None,
                "predicted_size": "M",
                "confidence": 0.85,
                "shirt_size": {
                    "recommended_size": "M",
                    "confidence": 0.87,
                    "alternative_sizes": ["S", "L"],
                    "match_details": {},
                    "reason": "Size M cho áo: Vừa vặn ở ngực, vai"
                },
                "pants_size": {
                    "recommended_size": "L",
                    "confidence": 0.82,
                    "alternative_sizes": ["M", "XL"],
                    "match_details": {},
                    "reason": "Size L cho quần: Vừa vặn ở eo, hông"
                },
                "measurements": {
                    "chest": 96, "waist": 78, "hip": 94,
                    "shoulder_width_cm": 44, "back_length": 47,
                    "inseam": 78, "thigh_circumference": 56,
                    "neck_circumference": 38, "arm_circumference": 32
                },
                "alternative_sizes": ["S", "L"],
                "brand": "uniqlo",
                "gender": "male",
                "bmi": 22.5,
                "error": None
            }
        }


class BrandInfo(BaseModel):
    """Information about a brand."""
    
    name: str
    available_regions: List[str]
    available_genders: List[str]
    sizes: List[str]
    garment_types: List[str] = Field(default=['shirt', 'pants'], description="Available garment types")


class BrandsResponse(BaseModel):
    """Response for brands endpoint."""
    
    brands: List[BrandInfo]
    default_brand: str


class HealthResponse(BaseModel):
    """Response for health check endpoint."""
    
    status: str
    model_loaded: bool
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = False
    error: str
    detail: Optional[str] = None
