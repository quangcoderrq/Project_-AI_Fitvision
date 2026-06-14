"""
Brand Rules Module
Manages size charts for different brands.
Supports separate shirt and pants sizing, and regional standard variations.
"""

from typing import Dict, List, Optional, Tuple
import os
import json
import copy


class BrandRules:
    """Manages brand-specific size charts with shirt/pants separation and region support."""
    
    # Default generic size chart — split into shirt and pants
    # Hierarchy: brand -> region -> gender -> garment_type -> size
    DEFAULT_SIZE_CHART = {
        'generic': {
            'asia': {
                'male': {
                    'shirt': {
                        'XS': {'chest': [80, 88], 'waist': [68, 76], 'shoulder_width_cm': [40, 42], 'back_length': [42, 44]},
                        'S':  {'chest': [88, 94], 'waist': [76, 82], 'shoulder_width_cm': [42, 44], 'back_length': [44, 47]},
                        'M':  {'chest': [94, 100], 'waist': [82, 88], 'shoulder_width_cm': [44, 46], 'back_length': [47, 50]},
                        'L':  {'chest': [100, 106], 'waist': [88, 94], 'shoulder_width_cm': [46, 48], 'back_length': [50, 53]},
                        'XL': {'chest': [106, 112], 'waist': [94, 100], 'shoulder_width_cm': [48, 50], 'back_length': [53, 56]},
                        'XXL': {'chest': [112, 120], 'waist': [100, 108], 'shoulder_width_cm': [50, 53], 'back_length': [56, 60]},
                    },
                    'pants': {
                        'XS': {'waist': [68, 76], 'hip': [82, 90], 'inseam': [72, 76], 'thigh_circumference': [48, 52]},
                        'S':  {'waist': [76, 82], 'hip': [90, 96], 'inseam': [74, 78], 'thigh_circumference': [50, 55]},
                        'M':  {'waist': [82, 88], 'hip': [96, 102], 'inseam': [76, 80], 'thigh_circumference': [53, 58]},
                        'L':  {'waist': [88, 94], 'hip': [102, 108], 'inseam': [78, 82], 'thigh_circumference': [56, 62]},
                        'XL': {'waist': [94, 100], 'hip': [108, 114], 'inseam': [79, 83], 'thigh_circumference': [60, 66]},
                        'XXL': {'waist': [100, 108], 'hip': [114, 122], 'inseam': [80, 84], 'thigh_circumference': [64, 70]},
                    }
                },
                'female': {
                    'shirt': {
                        'XS': {'chest': [76, 82], 'waist': [58, 64], 'shoulder_width_cm': [35, 37], 'back_length': [38, 40]},
                        'S':  {'chest': [82, 88], 'waist': [64, 70], 'shoulder_width_cm': [37, 39], 'back_length': [39, 42]},
                        'M':  {'chest': [88, 94], 'waist': [70, 76], 'shoulder_width_cm': [39, 41], 'back_length': [41, 44]},
                        'L':  {'chest': [94, 100], 'waist': [76, 82], 'shoulder_width_cm': [41, 43], 'back_length': [43, 46]},
                        'XL': {'chest': [100, 108], 'waist': [82, 90], 'shoulder_width_cm': [43, 45], 'back_length': [45, 48]},
                        'XXL': {'chest': [108, 116], 'waist': [90, 98], 'shoulder_width_cm': [45, 48], 'back_length': [47, 50]},
                    },
                    'pants': {
                        'XS': {'waist': [58, 64], 'hip': [82, 88], 'inseam': [68, 72], 'thigh_circumference': [46, 50]},
                        'S':  {'waist': [64, 70], 'hip': [88, 94], 'inseam': [69, 73], 'thigh_circumference': [49, 53]},
                        'M':  {'waist': [70, 76], 'hip': [94, 100], 'inseam': [70, 74], 'thigh_circumference': [52, 56]},
                        'L':  {'waist': [76, 82], 'hip': [100, 106], 'inseam': [71, 75], 'thigh_circumference': [55, 60]},
                        'XL': {'waist': [82, 90], 'hip': [106, 114], 'inseam': [72, 76], 'thigh_circumference': [58, 64]},
                        'XXL': {'waist': [90, 98], 'hip': [114, 122], 'inseam': [73, 77], 'thigh_circumference': [62, 68]},
                    }
                }
            }
        },
        'uniqlo': {
            'asia': {
                'male': {
                    'shirt': {
                        'XS': {'chest': [80, 86], 'waist': [68, 74], 'shoulder_width_cm': [40, 42], 'back_length': [64, 66]},
                        'S':  {'chest': [86, 92], 'waist': [74, 80], 'shoulder_width_cm': [42, 44], 'back_length': [66, 68]},
                        'M':  {'chest': [92, 98], 'waist': [80, 86], 'shoulder_width_cm': [44, 46], 'back_length': [68, 70]},
                        'L':  {'chest': [98, 104], 'waist': [86, 92], 'shoulder_width_cm': [46, 48], 'back_length': [70, 72]},
                        'XL': {'chest': [104, 112], 'waist': [92, 100], 'shoulder_width_cm': [48, 50], 'back_length': [72, 74]},
                    },
                    'pants': {
                        'XS': {'waist': [68, 74], 'hip': [84, 90], 'inseam': [72, 76], 'thigh_circumference': [50, 54]},
                        'S':  {'waist': [74, 80], 'hip': [90, 96], 'inseam': [74, 78], 'thigh_circumference': [52, 56]},
                        'M':  {'waist': [80, 86], 'hip': [96, 102], 'inseam': [76, 80], 'thigh_circumference': [54, 60]},
                        'L':  {'waist': [86, 92], 'hip': [102, 108], 'inseam': [78, 82], 'thigh_circumference': [58, 64]},
                        'XL': {'waist': [92, 100], 'hip': [108, 114], 'inseam': [79, 83], 'thigh_circumference': [62, 68]},
                    }
                },
                'female': {
                    'shirt': {
                        'XS': {'chest': [74, 80], 'waist': [58, 64], 'shoulder_width_cm': [35, 37], 'back_length': [56, 58]},
                        'S':  {'chest': [80, 86], 'waist': [64, 70], 'shoulder_width_cm': [37, 39], 'back_length': [58, 60]},
                        'M':  {'chest': [86, 92], 'waist': [70, 76], 'shoulder_width_cm': [39, 41], 'back_length': [60, 62]},
                        'L':  {'chest': [92, 98], 'waist': [76, 82], 'shoulder_width_cm': [41, 43], 'back_length': [62, 64]},
                        'XL': {'chest': [98, 106], 'waist': [82, 90], 'shoulder_width_cm': [43, 45], 'back_length': [64, 66]},
                    },
                    'pants': {
                        'XS': {'waist': [58, 64], 'hip': [82, 88], 'inseam': [68, 72], 'thigh_circumference': [48, 52]},
                        'S':  {'waist': [64, 70], 'hip': [88, 94], 'inseam': [69, 73], 'thigh_circumference': [50, 54]},
                        'M':  {'waist': [70, 76], 'hip': [94, 100], 'inseam': [70, 74], 'thigh_circumference': [52, 58]},
                        'L':  {'waist': [76, 82], 'hip': [100, 106], 'inseam': [71, 75], 'thigh_circumference': [56, 62]},
                        'XL': {'waist': [82, 90], 'hip': [106, 112], 'inseam': [72, 76], 'thigh_circumference': [60, 66]},
                    }
                }
            },
            'us': {
                # Just an example of a different region for Uniqlo US (sizes shifted up roughly)
                'male': {
                    'shirt': {
                        'XXS': {'chest': [80, 86], 'waist': [68, 74], 'shoulder_width_cm': [40, 42], 'back_length': [64, 66]},
                        'XS':  {'chest': [86, 92], 'waist': [74, 80], 'shoulder_width_cm': [42, 44], 'back_length': [66, 68]},
                        'S':  {'chest': [92, 98], 'waist': [80, 86], 'shoulder_width_cm': [44, 46], 'back_length': [68, 70]},
                        'M':  {'chest': [98, 104], 'waist': [86, 92], 'shoulder_width_cm': [46, 48], 'back_length': [70, 72]},
                        'L': {'chest': [104, 112], 'waist': [92, 100], 'shoulder_width_cm': [48, 50], 'back_length': [72, 74]},
                    },
                    'pants': {
                        'XXS': {'waist': [68, 74], 'hip': [84, 90], 'inseam': [72, 76], 'thigh_circumference': [50, 54]},
                        'XS':  {'waist': [74, 80], 'hip': [90, 96], 'inseam': [74, 78], 'thigh_circumference': [52, 56]},
                        'S':  {'waist': [80, 86], 'hip': [96, 102], 'inseam': [76, 80], 'thigh_circumference': [54, 60]},
                        'M':  {'waist': [86, 92], 'hip': [102, 108], 'inseam': [78, 82], 'thigh_circumference': [58, 64]},
                        'L': {'waist': [92, 100], 'hip': [108, 114], 'inseam': [79, 83], 'thigh_circumference': [62, 68]},
                    }
                }
            }
        },
        'zara': {
            'eu': {
                'male': {
                    'shirt': {
                        'S':  {'chest': [86, 92], 'waist': [74, 80], 'shoulder_width_cm': [42, 44], 'back_length': [68, 70]},
                        'M':  {'chest': [92, 98], 'waist': [80, 86], 'shoulder_width_cm': [44, 46], 'back_length': [70, 72]},
                        'L':  {'chest': [98, 104], 'waist': [86, 92], 'shoulder_width_cm': [46, 48], 'back_length': [72, 74]},
                        'XL': {'chest': [104, 110], 'waist': [92, 98], 'shoulder_width_cm': [48, 50], 'back_length': [74, 76]},
                    },
                    'pants': {
                        'S':  {'waist': [74, 80], 'hip': [90, 96], 'inseam': [76, 80], 'thigh_circumference': [52, 56]},
                        'M':  {'waist': [80, 86], 'hip': [96, 102], 'inseam': [78, 82], 'thigh_circumference': [54, 60]},
                        'L':  {'waist': [86, 92], 'hip': [102, 108], 'inseam': [80, 84], 'thigh_circumference': [58, 64]},
                        'XL': {'waist': [92, 98], 'hip': [108, 114], 'inseam': [81, 85], 'thigh_circumference': [62, 68]},
                    }
                },
                'female': {
                    'shirt': {
                        'S':  {'chest': [82, 88], 'waist': [64, 70], 'shoulder_width_cm': [37, 39], 'back_length': [58, 60]},
                        'M':  {'chest': [88, 94], 'waist': [70, 76], 'shoulder_width_cm': [39, 41], 'back_length': [60, 62]},
                        'L':  {'chest': [94, 100], 'waist': [76, 82], 'shoulder_width_cm': [41, 43], 'back_length': [62, 64]},
                        'XL': {'chest': [100, 108], 'waist': [82, 90], 'shoulder_width_cm': [43, 45], 'back_length': [64, 66]},
                    },
                    'pants': {
                        'S':  {'waist': [64, 70], 'hip': [88, 94], 'inseam': [72, 76], 'thigh_circumference': [50, 54]},
                        'M':  {'waist': [70, 76], 'hip': [94, 100], 'inseam': [73, 77], 'thigh_circumference': [52, 58]},
                        'L':  {'waist': [76, 82], 'hip': [100, 106], 'inseam': [74, 78], 'thigh_circumference': [56, 62]},
                        'XL': {'waist': [82, 90], 'hip': [106, 112], 'inseam': [75, 79], 'thigh_circumference': [60, 66]},
                    }
                }
            }
        }
    }
    
    def __init__(self, size_chart_path: Optional[str] = None):
        """
        Initialize brand rules.
        
        Args:
            size_chart_path: Path to JSON file with size charts
        """
        self.size_charts = copy.deepcopy(self.DEFAULT_SIZE_CHART)
        
        if size_chart_path and os.path.exists(size_chart_path):
            self.load_from_file(size_chart_path)
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load size charts from JSON file.
        
        Args:
            filepath: Path to JSON file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for brand, brand_data in data.items():
            brand_key = brand.lower()
            if brand_key not in self.size_charts:
                self.size_charts[brand_key] = {}
                
            # Check if brand_data has region level or goes straight to gender
            # (Backwards compatibility)
            has_region = any(k not in ['male', 'female'] for k in brand_data.keys())
            
            if not has_region:
                # Old format without region, default to 'asia'
                region_key = 'asia'
                self._merge_gender_data(brand_key, region_key, brand_data)
            else:
                for region, region_data in brand_data.items():
                    self._merge_gender_data(brand_key, region.lower(), region_data)
                    
    def _merge_gender_data(self, brand: str, region: str, region_data: Dict):
        """Helper to merge gender-level data, handling legacy flat format."""
        if region not in self.size_charts[brand]:
            self.size_charts[brand][region] = {}
            
        for gender in ['male', 'female']:
            if gender in region_data:
                chart = region_data[gender]
                if isinstance(chart, dict):
                    first_key = next(iter(chart), '')
                    if first_key in ['shirt', 'pants']:
                        self.size_charts[brand][region][gender] = chart
                    else:
                        # Old format (flat sizes)
                        self.size_charts[brand][region][gender] = {
                            'shirt': chart,
                            'pants': chart
                        }

    
    def save_to_file(self, filepath: str) -> None:
        """Save size charts to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.size_charts, f, indent=2)
    
    def get_size_chart(self, brand: str, region: str, gender: str, 
                       garment_type: str = 'shirt') -> Optional[Dict]:
        """
        Get size chart for a brand, region, gender, and garment type.
        
        Args:
            brand: Brand name (case-insensitive)
            region: Region/Standard (e.g., 'asia', 'us')
            gender: 'male' or 'female'
            garment_type: 'shirt' or 'pants'
            
        Returns:
            Size chart dictionary or None
        """
        brand_lower = brand.lower()
        region_lower = region.lower()
        gender_lower = gender.lower()
        
        if brand_lower in self.size_charts:
            brand_data = self.size_charts[brand_lower]
            
            # If region not found, fallback to first available region for this brand
            target_region = region_lower if region_lower in brand_data else next(iter(brand_data.keys()), None)
            
            if target_region and target_region in brand_data:
                region_data = brand_data[target_region]
                if gender_lower in region_data:
                    gender_chart = region_data[gender_lower]
                    if garment_type in gender_chart:
                        return gender_chart[garment_type]
        
        # Fall back to generic
        if brand_lower != 'generic' and 'generic' in self.size_charts:
            return self.get_size_chart('generic', region, gender, garment_type)
        
        return None
    
    def get_available_brands(self) -> List[str]:
        """Get list of available brands."""
        return list(self.size_charts.keys())
        
    def get_available_regions(self, brand: str) -> List[str]:
        """Get list of available regions for a brand."""
        brand_lower = brand.lower()
        if brand_lower in self.size_charts:
            return list(self.size_charts[brand_lower].keys())
        return []
    
    def get_garment_types(self, brand: str = 'generic', region: str = 'asia', gender: str = 'male') -> List[str]:
        """Get available garment types for a brand/region/gender."""
        brand_lower = brand.lower()
        region_lower = region.lower()
        gender_lower = gender.lower()
        
        if brand_lower in self.size_charts:
            brand_data = self.size_charts[brand_lower]
            target_region = region_lower if region_lower in brand_data else next(iter(brand_data.keys()), None)
            if target_region:
                region_data = brand_data[target_region]
                if gender_lower in region_data:
                    return list(region_data[gender_lower].keys())
        return ['shirt', 'pants']
    
    def add_brand(self, brand: str, size_chart: Dict) -> None:
        self.size_charts[brand.lower()] = size_chart
    
    def remove_brand(self, brand: str) -> bool:
        brand_lower = brand.lower()
        if brand_lower in self.size_charts and brand_lower != 'generic':
            del self.size_charts[brand_lower]
            return True
        return False
