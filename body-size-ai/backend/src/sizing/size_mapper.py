"""
Size Mapper Module
Maps body measurements to clothing sizes.
Supports separate shirt and pants sizing.
"""

from typing import Dict, List, Optional, Tuple
import os
import json

from .brand_rules import BrandRules


class SizeMapper:
    """Maps body measurements to clothing sizes."""
    
    # Standard size order
    SIZE_ORDER = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
    
    # Which measurements are relevant for each garment type
    SHIRT_MEASUREMENTS = ['chest', 'waist', 'shoulder_width_cm', 'back_length']
    PANTS_MEASUREMENTS = ['waist', 'hip', 'inseam', 'thigh_circumference']
    
    def __init__(self, size_chart_path: Optional[str] = None):
        """
        Initialize size mapper.
        
        Args:
            size_chart_path: Path to size charts JSON file
        """
        self.brand_rules = BrandRules(size_chart_path)
        self.available_brands = self.brand_rules.get_available_brands()
    
    def map_size(self, 
                 measurements: Dict[str, float],
                 gender: str = 'male',
                 brand: str = 'generic',
                 region: str = 'asia') -> Dict:
        """
        Map measurements to a single overall size (backward compatible).
        
        Args:
            measurements: Dict with body measurements in cm
            gender: 'male' or 'female'
            brand: Brand name
            
        Returns:
            Dictionary with size recommendation
        """
        # Use shirt size as the primary recommendation for backward compatibility
        size_chart = self.brand_rules.get_size_chart(brand, region, gender, 'shirt')
        
        if not size_chart:
            size_chart = self.brand_rules.get_size_chart('generic', region, gender, 'shirt')
        
        if not size_chart:
            return {
                'recommended_size': 'M',
                'confidence': 0.5,
                'alternative_sizes': ['S', 'L'],
                'match_details': {},
                'error': 'No size chart available'
            }
        
        # Filter measurements to relevant ones for shirt
        relevant_measurements = {
            k: v for k, v in measurements.items() 
            if k in size_chart.get(next(iter(size_chart), 'M'), {})
        }
        
        if not relevant_measurements:
            # Fallback: use all measurements
            relevant_measurements = measurements
        
        # Find best matching size
        best_size, confidence, match_details = self._find_best_size(
            relevant_measurements, size_chart
        )
        
        # Get alternative sizes
        alternatives = self._get_alternative_sizes(best_size)
        
        return {
            'recommended_size': best_size,
            'confidence': round(confidence, 2),
            'alternative_sizes': alternatives,
            'match_details': match_details,
            'brand': brand,
            'gender': gender
        }
    
    def map_size_detailed(self,
                          measurements: Dict[str, float],
                          gender: str = 'male',
                          brand: str = 'generic',
                          region: str = 'asia') -> Dict:
        """
        Map measurements to separate shirt and pants sizes.
        
        Args:
            measurements: Dict with all body measurements in cm
            gender: 'male' or 'female'  
            brand: Brand name
            
        Returns:
            Dictionary with separate shirt and pants recommendations
        """
        result = {
            'brand': brand,
            'region': region,
            'gender': gender,
            'shirt': self._map_garment('shirt', measurements, gender, brand, region),
            'pants': self._map_garment('pants', measurements, gender, brand, region),
        }
        
        return result
    
    def _map_garment(self,
                     garment_type: str,
                     measurements: Dict[str, float],
                     gender: str,
                     brand: str,
                     region: str) -> Dict:
        """
        Map measurements to size for a specific garment type.
        
        Args:
            garment_type: 'shirt' or 'pants'
            measurements: All body measurements
            gender: 'male' or 'female'
            brand: Brand name
            
        Returns:
            Size recommendation for the garment type
        """
        size_chart = self.brand_rules.get_size_chart(brand, region, gender, garment_type)
        
        if not size_chart:
            size_chart = self.brand_rules.get_size_chart('generic', region, gender, garment_type)
        
        if not size_chart:
            return {
                'recommended_size': 'M',
                'confidence': 0.5,
                'alternative_sizes': ['S', 'L'],
                'match_details': {},
                'reason': 'Không có bảng size phù hợp'
            }
        
        # Get the set of measurement keys used in this size chart
        chart_measurements = set()
        for size_data in size_chart.values():
            chart_measurements.update(size_data.keys())
        
        # Filter to relevant measurements present in both user data and chart
        relevant_measurements = {
            k: v for k, v in measurements.items() 
            if k in chart_measurements and v > 0
        }
        
        if not relevant_measurements:
            return {
                'recommended_size': 'M',
                'confidence': 0.4,
                'alternative_sizes': ['S', 'L'],
                'match_details': {},
                'reason': 'Thiếu dữ liệu số đo'
            }
        
        # Find best matching size
        best_size, confidence, match_details = self._find_best_size(
            relevant_measurements, size_chart
        )
        
        # Generate explanation reason
        reason = self._generate_reason(best_size, match_details, garment_type)
        
        # Get alternative sizes
        alternatives = self._get_alternative_sizes(best_size)
        
        return {
            'recommended_size': best_size,
            'confidence': round(confidence, 2),
            'alternative_sizes': alternatives,
            'match_details': match_details,
            'reason': reason
        }
    
    def _generate_reason(self, size: str, match_details: Dict, 
                         garment_type: str) -> str:
        """Generate human-readable reason for the size recommendation."""
        if not match_details:
            return f"Dựa trên số đo tổng thể, {size} là phù hợp nhất"
        
        # Vietnamese measurement names
        vn_names = {
            'chest': 'ngực', 'waist': 'eo', 'hip': 'hông',
            'shoulder_width_cm': 'vai', 'back_length': 'lưng',
            'inseam': 'dài chân trong', 'thigh_circumference': 'đùi',
            'neck_circumference': 'cổ', 'arm_circumference': 'bắp tay'
        }
        
        fit_parts = []
        tight_parts = []
        loose_parts = []
        
        for measure, detail in match_details.items():
            name = vn_names.get(measure, measure)
            if detail['status'] == 'fit':
                fit_parts.append(name)
            elif detail['status'] == 'tight':
                tight_parts.append(name)
            elif detail['status'] == 'loose':
                loose_parts.append(name)
        
        parts = []
        if fit_parts:
            parts.append(f"Vừa vặn ở {', '.join(fit_parts)}")
        if tight_parts:
            parts.append(f"Hơi chật ở {', '.join(tight_parts)}")
        if loose_parts:
            parts.append(f"Hơi rộng ở {', '.join(loose_parts)}")
        
        garment_vn = 'áo' if garment_type == 'shirt' else 'quần'
        return f"Size {size} cho {garment_vn}: {'. '.join(parts)}" if parts else f"Size {size} phù hợp"
    
    def _find_best_size(self, 
                        measurements: Dict[str, float],
                        size_chart: Dict) -> Tuple[str, float, Dict]:
        """
        Find the best matching size.
        
        Args:
            measurements: Body measurements
            size_chart: Size chart for brand/gender
            
        Returns:
            Tuple of (size, confidence, match_details)
        """
        best_size = 'M'
        best_score = -1
        best_details = {}
        
        for size, ranges in size_chart.items():
            score, details = self._calculate_match_score(measurements, ranges)
            
            if score > best_score:
                best_score = score
                best_size = size
                best_details = details
        
        # Convert score to confidence (0-1)
        confidence = min(best_score, 1.0)
        
        return best_size, confidence, best_details
    
    def _calculate_match_score(self, 
                               measurements: Dict[str, float],
                               ranges: Dict) -> Tuple[float, Dict]:
        """
        Calculate how well measurements match a size range.
        
        Args:
            measurements: Body measurements
            ranges: Size ranges (e.g., {'chest': [88, 96], 'waist': [76, 84]})
            
        Returns:
            Tuple of (score, details)
        """
        scores = []
        details = {}
        
        for measure, value in measurements.items():
            if measure in ranges:
                min_val, max_val = ranges[measure]
                
                if min_val <= value <= max_val:
                    # Perfect match - score based on how centered
                    mid = (min_val + max_val) / 2
                    deviation = abs(value - mid)
                    range_half = (max_val - min_val) / 2
                    score = 1.0 - (deviation / range_half) * 0.3
                    status = 'fit'
                elif value < min_val:
                    # Too small
                    diff = min_val - value
                    score = max(0.3, 0.8 - (diff / 10) * 0.2)
                    status = 'tight'
                else:
                    # Too large
                    diff = value - max_val
                    score = max(0.3, 0.8 - (diff / 10) * 0.2)
                    status = 'loose'
                
                scores.append(score)
                details[measure] = {
                    'value': value,
                    'range': [min_val, max_val],
                    'status': status,
                    'score': round(score, 2)
                }
        
        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = 0.5
        
        return avg_score, details
    
    def _get_alternative_sizes(self, size: str) -> List[str]:
        """Get adjacent sizes as alternatives."""
        try:
            idx = self.SIZE_ORDER.index(size)
            alternatives = []
            
            if idx > 0:
                alternatives.append(self.SIZE_ORDER[idx - 1])
            if idx < len(self.SIZE_ORDER) - 1:
                alternatives.append(self.SIZE_ORDER[idx + 1])
            
            return alternatives
        except ValueError:
            return ['S', 'L'] if size != 'S' and size != 'L' else ['M']
    
    def get_size_comparison(self,
                            measurements: Dict[str, float],
                            gender: str = 'male',
                            brand: str = 'generic',
                            region: str = 'asia',
                            garment_type: str = 'shirt') -> Dict:
        """
        Get comparison of how measurements fit across all sizes.
        
        Args:
            measurements: Body measurements
            gender: 'male' or 'female'
            brand: Brand name
            garment_type: 'shirt' or 'pants'
            
        Returns:
            Dictionary with score for each size
        """
        size_chart = self.brand_rules.get_size_chart(brand, region, gender, garment_type)
        
        if not size_chart:
            return {}
        
        comparison = {}
        for size in self.SIZE_ORDER:
            if size in size_chart:
                score, details = self._calculate_match_score(measurements, size_chart[size])
                comparison[size] = {
                    'score': round(score, 2),
                    'details': details
                }
        
        return comparison
    
    def get_size_for_all_brands(self,
                                measurements: Dict[str, float],
                                gender: str = 'male',
                                region: str = 'asia') -> Dict[str, Dict]:
        """
        Get size recommendation for all available brands.
        
        Args:
            measurements: Body measurements
            gender: 'male' or 'female'
            
        Returns:
            Dictionary of brand to detailed size recommendations
        """
        results = {}
        
        for brand in self.available_brands:
            results[brand] = self.map_size_detailed(measurements, gender, brand, region)
        
        return results
    
    def get_available_brands(self) -> List[str]:
        """Get list of available brands."""
        return self.available_brands.copy()
    
    def add_brand(self, brand: str, size_chart: Dict) -> None:
        """
        Add a new brand size chart.
        
        Args:
            brand: Brand name
            size_chart: Size chart with 'male' and/or 'female' keys
        """
        self.brand_rules.add_brand(brand, size_chart)
        self.available_brands = self.brand_rules.get_available_brands()
