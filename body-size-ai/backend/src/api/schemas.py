"""
API Schemas Module
Pydantic models for request/response validation.
"""

from typing import Dict, List, Optional
import re

from pydantic import BaseModel, Field, field_validator, validator


class PredictionRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    height: float = Field(..., ge=100, le=250)
    weight: float = Field(..., ge=30, le=300)
    gender: str = Field(default="male")
    brand: str = Field(default="generic")
    region: str = Field(default="asia")
    image_type: str = Field(default="full")
    garment_type: str = Field(default="both")
    ignore_baggy_warning: bool = Field(default=False)

    @validator("gender")
    def validate_gender(cls, v):
        if v.lower() not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")
        return v.lower()

    @validator("brand")
    def validate_brand(cls, v):
        return v.lower()

    @validator("region")
    def validate_region(cls, v):
        return v.lower()

    @validator("image_type")
    def validate_image_type(cls, v):
        if v.lower() not in ["full", "upper", "lower"]:
            raise ValueError("image_type must be 'full', 'upper', or 'lower'")
        return v.lower()

    @validator("garment_type")
    def validate_garment_type(cls, v):
        if v.lower() not in ["both", "shirt", "pants"]:
            raise ValueError("garment_type must be 'both', 'shirt', or 'pants'")
        return v.lower()


class Measurements(BaseModel):
    chest: float
    waist: float
    hip: float
    shoulder_width_cm: float = 0
    back_length: float = 0
    inseam: float = 0
    thigh_circumference: float = 0
    neck_circumference: float = 0
    arm_circumference: float = 0


class MatchDetail(BaseModel):
    value: float
    range: List[float]
    status: str
    score: float


class GarmentSizeResult(BaseModel):
    recommended_size: Optional[str] = None
    confidence: float = 0.0
    alternative_sizes: List[str] = []
    match_details: Dict[str, MatchDetail] = {}
    reason: str = ""


class PredictionResponse(BaseModel):
    success: bool
    prediction_log_id: Optional[int] = None

    require_user_confirmation: bool = False
    baggy_clothes_detected: bool = False
    warning_message: Optional[str] = None

    predicted_size: Optional[str] = None
    confidence: float = 0.0
    pose_quality: Optional[float] = None

    shirt_size: Optional[GarmentSizeResult] = None
    pants_size: Optional[GarmentSizeResult] = None

    measurements: Optional[Measurements] = None
    alternative_sizes: List[str] = []
    match_details: Dict[str, MatchDetail] = {}

    brand: str = "generic"
    gender: str = "male"
    bmi: Optional[float] = None
    error: Optional[str] = None


class FeedbackRequest(BaseModel):
    prediction_log_id: int

    selected_shirt_size: Optional[str] = None
    selected_pants_size: Optional[str] = None

    shirt_feedback: Optional[str] = None
    pants_feedback: Optional[str] = None

    overall_feedback: str = Field(..., description="fit, tight, loose, wrong")
    issue_area: Optional[str] = None
    feedback_note: Optional[str] = None
    returned_or_exchanged: bool = False


class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str
    password: str = Field(..., min_length=6)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError("Họ và tên không được để trống")
        return name

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email = v.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise ValueError("Email không hợp lệ")
        return email


class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    full_name: Optional[str] = None
    email: str
    active_plan: str
    api_token: str


class UserProfileResponse(BaseModel):
    full_name: Optional[str] = None
    email: str
    active_plan: str
    api_token: str


class SubscriptionRequest(BaseModel):
    plan_name: str


class PredictionLogResponse(BaseModel):
    id: int
    height: float
    weight: float
    gender: str
    brand: str
    predicted_size: Optional[str]
    shirt_size: Optional[str] = None
    pants_size: Optional[str] = None
    confidence: float
    pose_quality: Optional[float] = None
    overall_feedback: Optional[str] = None
    created_at: str


class BrandInfo(BaseModel):
    name: str
    available_regions: List[str]
    available_genders: List[str]
    sizes: List[str]
    garment_types: List[str] = ["shirt", "pants"]


class BrandsResponse(BaseModel):
    brands: List[BrandInfo]
    default_brand: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None