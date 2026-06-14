"""
Image Utilities Module
Helper functions for image handling.
"""

import os
import base64
from typing import Optional, Tuple, Union
import numpy as np
import cv2
from PIL import Image
import io


class ImageUtils:
    """Utility class for image operations."""
    
    @staticmethod
    def load_image(path: str) -> Optional[np.ndarray]:
        """
        Load image from file path.
        
        Args:
            path: Path to image file
            
        Returns:
            Image as numpy array (BGR) or None if failed
        """
        if not os.path.exists(path):
            return None
        
        try:
            image = cv2.imread(path)
            return image
        except Exception:
            return None
    
    @staticmethod
    def save_image(image: np.ndarray, path: str, 
                   quality: int = 95) -> bool:
        """
        Save image to file.
        
        Args:
            image: Image as numpy array
            path: Output path
            quality: JPEG quality (1-100)
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            ext = os.path.splitext(path)[1].lower()
            
            if ext == '.png':
                params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
            else:
                params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            
            return cv2.imwrite(path, image, params)
        except Exception:
            return False
    
    @staticmethod
    def from_base64(base64_string: str) -> Optional[np.ndarray]:
        """
        Decode base64 string to image.
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            Image as numpy array (BGR) or None
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode
            image_bytes = base64.b64decode(base64_string)
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            return image
        except Exception:
            return None
    
    @staticmethod
    def to_base64(image: np.ndarray, format: str = 'jpg') -> str:
        """
        Encode image to base64 string.
        
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
    
    @staticmethod
    def from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Load image from bytes.
        
        Args:
            image_bytes: Image as bytes
            
        Returns:
            Image as numpy array or None
        """
        try:
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            return image
        except Exception:
            return None
    
    @staticmethod
    def to_bytes(image: np.ndarray, format: str = 'jpg') -> bytes:
        """
        Convert image to bytes.
        
        Args:
            image: Image as numpy array
            format: Output format ('jpg' or 'png')
            
        Returns:
            Image as bytes
        """
        if format.lower() == 'png':
            ext = '.png'
            params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
        else:
            ext = '.jpg'
            params = [cv2.IMWRITE_JPEG_QUALITY, 85]
        
        _, buffer = cv2.imencode(ext, image, params)
        return buffer.tobytes()
    
    @staticmethod
    def resize(image: np.ndarray, 
               width: Optional[int] = None,
               height: Optional[int] = None,
               maintain_aspect: bool = True) -> np.ndarray:
        """
        Resize image.
        
        Args:
            image: Input image
            width: Target width
            height: Target height
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        
        if width is None and height is None:
            return image
        
        if maintain_aspect:
            if width is not None and height is not None:
                # Use the dimension that results in smaller image
                scale_w = width / w
                scale_h = height / h
                scale = min(scale_w, scale_h)
            elif width is not None:
                scale = width / w
            else:
                scale = height / h
            
            new_w = int(w * scale)
            new_h = int(h * scale)
        else:
            new_w = width if width is not None else w
            new_h = height if height is not None else h
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def get_dimensions(image: np.ndarray) -> Tuple[int, int]:
        """Get image dimensions (width, height)."""
        h, w = image.shape[:2]
        return w, h
    
    @staticmethod
    def is_valid_image(data: Union[str, bytes, np.ndarray]) -> bool:
        """
        Check if data is a valid image.
        
        Args:
            data: Image as base64, bytes, or numpy array
            
        Returns:
            True if valid image
        """
        try:
            if isinstance(data, np.ndarray):
                return len(data.shape) >= 2
            elif isinstance(data, bytes):
                image = ImageUtils.from_bytes(data)
                return image is not None
            elif isinstance(data, str):
                image = ImageUtils.from_base64(data)
                return image is not None
            return False
        except Exception:
            return False
    
    @staticmethod
    def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
        """Convert BGR to RGB."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def rgb_to_bgr(image: np.ndarray) -> np.ndarray:
        """Convert RGB to BGR."""
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
