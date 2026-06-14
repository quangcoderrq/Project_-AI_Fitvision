"""
Pixel Converter Module
Converts pixel measurements to real-world measurements (cm).
"""

from typing import Optional


class PixelConverter:
    """Converts between pixel and real-world measurements."""
    
    def __init__(self):
        self.pixels_per_cm: Optional[float] = None
        self.cm_per_pixel: Optional[float] = None
        self.reference_height_cm: Optional[float] = None
        self.reference_height_px: Optional[float] = None
    
    def calibrate(self, real_height_cm: float, pixel_height: float) -> None:
        """
        Calibrate the converter using known height.
        
        Args:
            real_height_cm: Actual height in centimeters
            pixel_height: Height in pixels from image
        """
        if pixel_height <= 0:
            raise ValueError("Pixel height must be positive")
        if real_height_cm <= 0:
            raise ValueError("Real height must be positive")
        
        self.reference_height_cm = real_height_cm
        self.reference_height_px = pixel_height
        self.cm_per_pixel = real_height_cm / pixel_height
        self.pixels_per_cm = pixel_height / real_height_cm
    
    def pixels_to_cm(self, pixels: float) -> float:
        """
        Convert pixel measurement to centimeters.
        
        Args:
            pixels: Measurement in pixels
            
        Returns:
            Measurement in centimeters
        """
        if self.cm_per_pixel is None:
            raise ValueError("Converter not calibrated. Call calibrate() first.")
        return pixels * self.cm_per_pixel
    
    def cm_to_pixels(self, cm: float) -> float:
        """
        Convert centimeter measurement to pixels.
        
        Args:
            cm: Measurement in centimeters
            
        Returns:
            Measurement in pixels
        """
        if self.pixels_per_cm is None:
            raise ValueError("Converter not calibrated. Call calibrate() first.")
        return cm * self.pixels_per_cm
    
    def get_scale_factor(self) -> Optional[float]:
        """Get the cm per pixel ratio."""
        return self.cm_per_pixel
    
    def is_calibrated(self) -> bool:
        """Check if converter is calibrated."""
        return self.cm_per_pixel is not None
    
    def reset(self) -> None:
        """Reset calibration."""
        self.pixels_per_cm = None
        self.cm_per_pixel = None
        self.reference_height_cm = None
        self.reference_height_px = None
    
    def estimate_measurement_accuracy(self) -> float:
        """
        Estimate the accuracy of conversions.
        
        Returns:
            Estimated accuracy as a percentage (0-100)
        """
        if not self.is_calibrated():
            return 0.0
        
        # Base accuracy starts at 80%
        accuracy = 80.0
        
        # Higher resolution (more pixels per cm) = better accuracy
        if self.pixels_per_cm:
            if self.pixels_per_cm > 5:  # High resolution
                accuracy += 10
            elif self.pixels_per_cm > 2:  # Medium resolution
                accuracy += 5
            elif self.pixels_per_cm < 1:  # Low resolution
                accuracy -= 15
        
        return min(max(accuracy, 50.0), 95.0)
