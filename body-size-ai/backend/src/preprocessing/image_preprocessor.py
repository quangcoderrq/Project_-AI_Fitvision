"""
Image Preprocessor Module
Preprocesses images for pose estimation.
"""

from typing import Tuple, Optional
import numpy as np
import cv2
from PIL import Image
import io
import base64


class ImagePreprocessor:
    """Preprocesses images for body pose estimation."""
    
    # Target dimensions for processing
    TARGET_WIDTH = 640
    TARGET_HEIGHT = 480
    
    def __init__(self, target_size: Tuple[int, int] = None):
        """
        Initialize preprocessor.
        
        Args:
            target_size: Tuple of (width, height) for resizing
        """
        if target_size:
            self.target_width, self.target_height = target_size
        else:
            self.target_width = self.TARGET_WIDTH
            self.target_height = self.TARGET_HEIGHT
    
    def preprocess(self, image: np.ndarray, 
                   maintain_aspect: bool = True) -> np.ndarray:
        """
        Preprocess image for pose estimation.
        
        Args:
            image: Input image as numpy array (BGR)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Preprocessed image
        """
        # Ensure RGB
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Resize
        if maintain_aspect:
            image = self._resize_with_aspect(image)
        else:
            image = cv2.resize(image, (self.target_width, self.target_height))
        
        # Normalize colors
        image = self._normalize_colors(image)
        
        return image
    
    def preprocess_from_file(self, image_path: str, 
                             maintain_aspect: bool = True) -> np.ndarray:
        """
        Load and preprocess image from file.
        
        Args:
            image_path: Path to image file
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Preprocessed image
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return self.preprocess(image, maintain_aspect)
    
    def preprocess_from_base64(self, base64_string: str,
                               maintain_aspect: bool = True) -> np.ndarray:
        """
        Decode and preprocess base64 encoded image.
        
        Args:
            base64_string: Base64 encoded image
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Preprocessed image
        """
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode
        image_bytes = base64.b64decode(base64_string)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode base64 image")
        
        return self.preprocess(image, maintain_aspect)
    
    def _resize_with_aspect(self, image: np.ndarray) -> np.ndarray:
        """Resize image maintaining aspect ratio."""
        height, width = image.shape[:2]
        
        # Calculate scaling factor
        scale_w = self.target_width / width
        scale_h = self.target_height / height
        scale = min(scale_w, scale_h)
        
        # Only downscale, don't upscale
        if scale >= 1:
            return image
        
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        return cv2.resize(image, (new_width, new_height), 
                         interpolation=cv2.INTER_AREA)
    
    def _normalize_colors(self, image: np.ndarray) -> np.ndarray:
        """Normalize image colors for consistent processing."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Split channels
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge and convert back
        lab = cv2.merge([l, a, b])
        normalized = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return normalized
    
    def to_rgb(self, image: np.ndarray) -> np.ndarray:
        """Convert BGR image to RGB."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    def to_bgr(self, image: np.ndarray) -> np.ndarray:
        """Convert RGB image to BGR."""
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    def to_base64(self, image: np.ndarray, format: str = 'jpg') -> str:
        """
        Convert image to base64 string.
        
        Args:
            image: Image as numpy array (BGR)
            format: Output format ('jpg' or 'png')
            
        Returns:
            Base64 encoded string
        """
        if format.lower() == 'png':
            ext = '.png'
            params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
        else:
            ext = '.jpg'
            params = [cv2.IMWRITE_JPEG_QUALITY, 85]
        
        _, buffer = cv2.imencode(ext, image, params)
        return base64.b64encode(buffer).decode('utf-8')
    
    def pad_to_square(self, image: np.ndarray, 
                      pad_color: Tuple[int, int, int] = (0, 0, 0)) -> np.ndarray:
        """
        Pad image to make it square.
        
        Args:
            image: Input image
            pad_color: Color for padding (BGR)
            
        Returns:
            Square padded image
        """
        height, width = image.shape[:2]
        
        if height == width:
            return image
        
        size = max(height, width)
        
        # Create square canvas
        if len(image.shape) == 3:
            canvas = np.full((size, size, 3), pad_color, dtype=np.uint8)
        else:
            canvas = np.full((size, size), pad_color[0], dtype=np.uint8)
        
        # Center the image
        y_offset = (size - height) // 2
        x_offset = (size - width) // 2
        canvas[y_offset:y_offset+height, x_offset:x_offset+width] = image
        
        return canvas
