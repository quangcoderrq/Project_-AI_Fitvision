"""
Image Validator Module
Validates input images for quality and format requirements.
"""

import os
from typing import Tuple, Optional
import numpy as np
from PIL import Image
import cv2


class ImageValidator:
    """Validates images for body size estimation."""

    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp'}

    # Allow smaller user-uploaded images
    MIN_WIDTH = 300
    MIN_HEIGHT = 300

    TARGET_WIDTH = 640

    MIN_BRIGHTNESS = 30
    MAX_BRIGHTNESS = 220
    MIN_CONTRAST = 20

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, image_path: str) -> Tuple[bool, list, list]:
        self.errors = []
        self.warnings = []

        if not os.path.exists(image_path):
            self.errors.append(f"File not found: {image_path}")
            return False, self.errors, self.warnings

        if not self._check_format(image_path):
            return False, self.errors, self.warnings

        image = self._load_image(image_path)
        if image is None:
            return False, self.errors, self.warnings

        self._check_dimensions(image)
        self._check_quality(image)

        return len(self.errors) == 0, self.errors, self.warnings

    def validate_array(self, image: np.ndarray) -> Tuple[bool, list, list]:
        self.errors = []
        self.warnings = []

        if image is None or not isinstance(image, np.ndarray):
            self.errors.append("Invalid image array")
            return False, self.errors, self.warnings

        if len(image.shape) < 2:
            self.errors.append("Image must be at least 2D")
            return False, self.errors, self.warnings

        self._check_dimensions(image)
        self._check_quality(image)

        return len(self.errors) == 0, self.errors, self.warnings

    def resize_if_needed(self, image: np.ndarray) -> np.ndarray:
        """
        Resize small images before pose detection.
        Keeps aspect ratio.
        """
        if image is None:
            return image

        height, width = image.shape[:2]

        if width >= self.TARGET_WIDTH:
            return image

        scale = self.TARGET_WIDTH / width
        new_height = int(height * scale)

        return cv2.resize(
            image,
            (self.TARGET_WIDTH, new_height),
            interpolation=cv2.INTER_CUBIC
        )

    def _check_format(self, image_path: str) -> bool:
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            self.errors.append(
                f"Unsupported format: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
            return False
        return True

    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.errors.append("Failed to load image")
                return None
            return image
        except Exception as e:
            self.errors.append(f"Error loading image: {str(e)}")
            return None

    def _check_dimensions(self, image: np.ndarray) -> None:
        height, width = image.shape[:2]

        if width < self.MIN_WIDTH:
            self.errors.append(
                f"Image width ({width}px) is too small. Minimum is {self.MIN_WIDTH}px."
            )

        if height < self.MIN_HEIGHT:
            self.errors.append(
                f"Image height ({height}px) is too small. Minimum is {self.MIN_HEIGHT}px."
            )

        if width < 640 or height < 480:
            self.warnings.append(
                f"Image resolution is low ({width}x{height}). "
                "The system will upscale it, but accuracy may decrease."
            )

        aspect_ratio = height / width
        if aspect_ratio < 1.0:
            self.warnings.append(
                "Image is landscape. Portrait orientation is recommended for full body."
            )

    def _check_quality(self, image: np.ndarray) -> None:
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        brightness = np.mean(gray)
        if brightness < self.MIN_BRIGHTNESS:
            self.warnings.append(
                f"Image is too dark (brightness: {brightness:.1f}). "
                "Consider using better lighting."
            )
        elif brightness > self.MAX_BRIGHTNESS:
            self.warnings.append(
                f"Image is too bright (brightness: {brightness:.1f}). "
                "Consider reducing exposure."
            )

        contrast = np.std(gray)
        if contrast < self.MIN_CONTRAST:
            self.warnings.append(
                f"Low contrast detected ({contrast:.1f}). "
                "This may affect pose detection accuracy."
            )

    def get_image_info(self, image_path: str) -> dict:
        info = {
            'path': image_path,
            'exists': os.path.exists(image_path),
            'size_bytes': 0,
            'width': 0,
            'height': 0,
            'format': '',
            'mode': ''
        }

        if not info['exists']:
            return info

        info['size_bytes'] = os.path.getsize(image_path)
        info['format'] = os.path.splitext(image_path)[1].lower()

        try:
            with Image.open(image_path) as img:
                info['width'], info['height'] = img.size
                info['mode'] = img.mode
        except Exception:
            pass

        return info