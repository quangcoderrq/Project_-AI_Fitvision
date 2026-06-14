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
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp'}
    
    # Minimum image dimensions
    MIN_WIDTH = 640
    MIN_HEIGHT = 480
    
    # Quality thresholds
    MIN_BRIGHTNESS = 30
    MAX_BRIGHTNESS = 220
    MIN_CONTRAST = 20
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, image_path: str) -> Tuple[bool, list, list]:
        """
        Validate an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Check file exists
        if not os.path.exists(image_path):
            self.errors.append(f"File not found: {image_path}")
            return False, self.errors, self.warnings
        
        # Check format
        if not self._check_format(image_path):
            return False, self.errors, self.warnings
        
        # Load image
        image = self._load_image(image_path)
        if image is None:
            return False, self.errors, self.warnings
        
        # Check dimensions
        self._check_dimensions(image)
        
        # Check quality
        self._check_quality(image)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def validate_array(self, image: np.ndarray) -> Tuple[bool, list, list]:
        """
        Validate a numpy array image.
        
        Args:
            image: Image as numpy array (BGR or RGB)
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        if image is None or not isinstance(image, np.ndarray):
            self.errors.append("Invalid image array")
            return False, self.errors, self.warnings
        
        if len(image.shape) < 2:
            self.errors.append("Image must be at least 2D")
            return False, self.errors, self.warnings
        
        # Check dimensions
        self._check_dimensions(image)
        
        # Check quality
        self._check_quality(image)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _check_format(self, image_path: str) -> bool:
        """Check if image format is supported."""
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            self.errors.append(
                f"Unsupported format: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
            return False
        return True
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image using OpenCV."""
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
        """Check image dimensions."""
        height, width = image.shape[:2]
        
        if width < self.MIN_WIDTH:
            self.errors.append(
                f"Image width ({width}px) is below minimum ({self.MIN_WIDTH}px)"
            )
        
        if height < self.MIN_HEIGHT:
            self.errors.append(
                f"Image height ({height}px) is below minimum ({self.MIN_HEIGHT}px)"
            )
        
        # Check aspect ratio
        aspect_ratio = height / width
        if aspect_ratio < 1.0:
            self.warnings.append(
                "Image is landscape. Portrait orientation recommended for full body."
            )
    
    def _check_quality(self, image: np.ndarray) -> None:
        """Check image quality (brightness, contrast)."""
        # Convert to grayscale for analysis
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Check brightness
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
        
        # Check contrast
        contrast = np.std(gray)
        if contrast < self.MIN_CONTRAST:
            self.warnings.append(
                f"Low contrast detected ({contrast:.1f}). "
                "This may affect pose detection accuracy."
            )
    
    def get_image_info(self, image_path: str) -> dict:
        """Get information about an image file."""
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
