from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    active_plan = Column(String, default="Free", nullable=False)  # Free, Starter, Professional, Enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tokens = relationship("APIToken", back_populates="user", cascade="all, delete-orphan")
    prediction_logs = relationship("PredictionLog", back_populates="user", cascade="all, delete-orphan")


class APIToken(Base):
    __tablename__ = "api_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tokens")


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # User input
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    gender = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    region = Column(String, nullable=True)
    garment_type = Column(String, nullable=True)

    # AI result
    predicted_size = Column(String, nullable=True)
    shirt_size = Column(String, nullable=True)
    pants_size = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    pose_quality = Column(Float, nullable=True)

    # Predicted measurements
    chest = Column(Float, nullable=True)
    waist = Column(Float, nullable=True)
    hip = Column(Float, nullable=True)
    shoulder_width_cm = Column(Float, nullable=True)
    back_length = Column(Float, nullable=True)
    inseam = Column(Float, nullable=True)
    thigh_circumference = Column(Float, nullable=True)
    neck_circumference = Column(Float, nullable=True)
    arm_circumference = Column(Float, nullable=True)

    # User actual choice
    selected_shirt_size = Column(String, nullable=True)
    selected_pants_size = Column(String, nullable=True)

    # Feedback
    shirt_feedback = Column(String, nullable=True)
    pants_feedback = Column(String, nullable=True)

    # fit / tight / loose / wrong
    overall_feedback = Column(String, nullable=True)

    # specific fit issue
    issue_area = Column(String, nullable=True)
    # chest / shoulder / waist / hip / thigh / length / inseam / other

    feedback_note = Column(String, nullable=True)

    returned_or_exchanged = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    feedback_created_at = Column(DateTime(timezone=True), nullable=True)

    # Learning / retraining metadata
    model_version = Column(String, nullable=True)
    prediction_source = Column(String, nullable=True)

    feedback_score = Column(Integer, nullable=True)
    would_use_again = Column(Boolean, nullable=True)
    is_training_sample = Column(Boolean, default=False)

    user = relationship("User", back_populates="prediction_logs")