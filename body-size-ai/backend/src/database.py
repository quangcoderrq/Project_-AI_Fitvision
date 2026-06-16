import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitvision.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def migrate_db():
    """Apply lightweight schema migrations."""
    inspector = inspect(engine)

    if not inspector.has_table("users"):
        return

    user_columns = {col["name"] for col in inspector.get_columns("users")}
    prediction_columns = {
        col["name"] for col in inspector.get_columns("prediction_logs")
    } if inspector.has_table("prediction_logs") else set()

    with engine.begin() as conn:
        if "full_name" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR"))

        # Prediction log migrations
        migrations = {
            "region": "VARCHAR",
            "garment_type": "VARCHAR",
            "shirt_size": "VARCHAR",
            "pants_size": "VARCHAR",
            "pose_quality": "FLOAT",

            "chest": "FLOAT",
            "waist": "FLOAT",
            "hip": "FLOAT",
            "shoulder_width_cm": "FLOAT",
            "back_length": "FLOAT",
            "inseam": "FLOAT",
            "thigh_circumference": "FLOAT",
            "neck_circumference": "FLOAT",
            "arm_circumference": "FLOAT",

            "selected_shirt_size": "VARCHAR",
            "selected_pants_size": "VARCHAR",
            "shirt_feedback": "VARCHAR",
            "pants_feedback": "VARCHAR",
            "overall_feedback": "VARCHAR",
            "issue_area": "VARCHAR",
            "feedback_note": "VARCHAR",
            "returned_or_exchanged": "BOOLEAN",
            "feedback_created_at": "TIMESTAMP",
        }

        for column_name, column_type in migrations.items():
            if column_name not in prediction_columns:
                conn.execute(
                    text(
                        f"ALTER TABLE prediction_logs "
                        f"ADD COLUMN {column_name} {column_type}"
                    )
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()