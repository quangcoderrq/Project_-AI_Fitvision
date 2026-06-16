import os
import sys
import csv

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from src.database import SessionLocal
from src.models.db_models import PredictionLog


OUTPUT_PATH = os.path.join(
    project_root,
    "data",
    "feedback",
    "feedback_training.csv"
)


def export_feedback_dataset():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    db = SessionLocal()

    try:
        logs = db.query(PredictionLog).filter(
            PredictionLog.overall_feedback.isnot(None)
        ).all()

        rows = []

        for log in logs:
            actual_shirt_size = log.selected_shirt_size or log.shirt_size
            actual_pants_size = log.selected_pants_size or log.pants_size

            rows.append({
                "id": log.id,

                "height": log.height,
                "weight": log.weight,
                "gender": log.gender,
                "brand": log.brand,
                "region": log.region,
                "garment_type": log.garment_type,

                "predicted_size": log.predicted_size,
                "predicted_shirt_size": log.shirt_size,
                "predicted_pants_size": log.pants_size,

                "actual_shirt_size": actual_shirt_size,
                "actual_pants_size": actual_pants_size,

                "overall_feedback": log.overall_feedback,
                "shirt_feedback": log.shirt_feedback,
                "pants_feedback": log.pants_feedback,
                "issue_area": log.issue_area,
                "returned_or_exchanged": log.returned_or_exchanged,

                "confidence": log.confidence,
                "pose_quality": log.pose_quality,

                "chest": log.chest,
                "waist": log.waist,
                "hip": log.hip,
                "shoulder_width_cm": log.shoulder_width_cm,
                "back_length": log.back_length,
                "inseam": log.inseam,
                "thigh_circumference": log.thigh_circumference,
                "neck_circumference": log.neck_circumference,
                "arm_circumference": log.arm_circumference,

                "created_at": log.created_at,
                "feedback_created_at": log.feedback_created_at,
            })

        fieldnames = list(rows[0].keys()) if rows else [
            "id",
            "height",
            "weight",
            "gender",
            "brand",
            "region",
            "garment_type",
            "predicted_size",
            "predicted_shirt_size",
            "predicted_pants_size",
            "actual_shirt_size",
            "actual_pants_size",
            "overall_feedback",
            "shirt_feedback",
            "pants_feedback",
            "issue_area",
            "returned_or_exchanged",
            "confidence",
            "pose_quality",
            "chest",
            "waist",
            "hip",
            "shoulder_width_cm",
            "back_length",
            "inseam",
            "thigh_circumference",
            "neck_circumference",
            "arm_circumference",
            "created_at",
            "feedback_created_at",
        ]

        with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Exported {len(rows)} feedback rows")
        print(f"Saved to: {OUTPUT_PATH}")

    finally:
        db.close()


if __name__ == "__main__":
    export_feedback_dataset()