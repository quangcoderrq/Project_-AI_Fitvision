"""
Test Size Mapping Module
"""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.sizing.size_mapper import SizeMapper
from src.sizing.brand_rules import BrandRules


class TestBrandRules:
    """Tests for BrandRules class."""
    
    def test_default_size_chart_exists(self):
        """Test that default size chart is available."""
        rules = BrandRules()
        
        assert 'generic' in rules.get_available_brands()
    
    def test_get_size_chart_male(self):
        """Test getting male size chart."""
        rules = BrandRules()
        
        chart = rules.get_size_chart('generic', 'male')
        
        assert chart is not None
        assert 'M' in chart
        assert 'chest' in chart['M']
    
    def test_get_size_chart_female(self):
        """Test getting female size chart."""
        rules = BrandRules()
        
        chart = rules.get_size_chart('generic', 'female')
        
        assert chart is not None
        assert 'M' in chart
    
    def test_get_size_chart_nonexistent_brand(self):
        """Test fallback to generic for nonexistent brand."""
        rules = BrandRules()
        
        chart = rules.get_size_chart('nonexistent_brand', 'male')
        
        # Should fall back to generic
        assert chart is not None
    
    def test_add_brand(self):
        """Test adding a new brand."""
        rules = BrandRules()
        
        new_chart = {
            'male': {
                'M': {'chest': [90, 98], 'waist': [78, 86], 'hip': [92, 100]}
            }
        }
        
        rules.add_brand('test_brand', new_chart)
        
        assert 'test_brand' in rules.get_available_brands()
    
    def test_remove_brand(self):
        """Test removing a brand."""
        rules = BrandRules()
        rules.add_brand('to_remove', {'male': {'M': {'chest': [90, 98]}}})
        
        success = rules.remove_brand('to_remove')
        
        assert success is True
        assert 'to_remove' not in rules.get_available_brands()
    
    def test_cannot_remove_generic(self):
        """Test that generic brand cannot be removed."""
        rules = BrandRules()
        
        success = rules.remove_brand('generic')
        
        assert success is False
        assert 'generic' in rules.get_available_brands()


class TestSizeMapper:
    """Tests for SizeMapper class."""
    
    def test_map_size_medium(self):
        """Test size mapping for medium measurements."""
        mapper = SizeMapper()
        measurements = {'chest': 96, 'waist': 82, 'hip': 98}
        
        result = mapper.map_size(measurements, gender='male')
        
        assert result['recommended_size'] in ['S', 'M', 'L']
        assert result['confidence'] > 0
    
    def test_map_size_small(self):
        """Test size mapping for small measurements."""
        mapper = SizeMapper()
        measurements = {'chest': 86, 'waist': 74, 'hip': 88}
        
        result = mapper.map_size(measurements, gender='male')
        
        assert result['recommended_size'] in ['XS', 'S', 'M']
    
    def test_map_size_large(self):
        """Test size mapping for large measurements."""
        mapper = SizeMapper()
        measurements = {'chest': 108, 'waist': 96, 'hip': 110}
        
        result = mapper.map_size(measurements, gender='male')
        
        assert result['recommended_size'] in ['L', 'XL', 'XXL']
    
    def test_map_size_female(self):
        """Test size mapping for female."""
        mapper = SizeMapper()
        measurements = {'chest': 88, 'waist': 70, 'hip': 94}
        
        result = mapper.map_size(measurements, gender='female')
        
        assert result['recommended_size'] in ['S', 'M', 'L']
        assert result['gender'] == 'female'
    
    def test_alternative_sizes(self):
        """Test that alternative sizes are provided."""
        mapper = SizeMapper()
        measurements = {'chest': 96, 'waist': 82, 'hip': 98}
        
        result = mapper.map_size(measurements, gender='male')
        
        assert 'alternative_sizes' in result
        assert len(result['alternative_sizes']) > 0
    
    def test_match_details(self):
        """Test that match details are provided."""
        mapper = SizeMapper()
        measurements = {'chest': 96, 'waist': 82, 'hip': 98}
        
        result = mapper.map_size(measurements, gender='male')
        
        assert 'match_details' in result
        if result['match_details']:
            for measure, detail in result['match_details'].items():
                assert 'status' in detail
                assert detail['status'] in ['fit', 'tight', 'loose']
    
    def test_get_available_brands(self):
        """Test getting available brands."""
        mapper = SizeMapper()
        
        brands = mapper.get_available_brands()
        
        assert isinstance(brands, list)
        assert 'generic' in brands
    
    def test_get_size_for_all_brands(self):
        """Test getting size for all brands."""
        mapper = SizeMapper()
        measurements = {'chest': 96, 'waist': 82, 'hip': 98}
        
        result = mapper.get_size_for_all_brands(measurements, gender='male')
        
        assert isinstance(result, dict)
        assert 'generic' in result
    
    def test_map_size_detailed(self):
        """Test separate shirt and pants sizing."""
        mapper = SizeMapper()
        measurements = {
            'chest': 96, 'shoulder_width_cm': 44, 'back_length': 65,  # Shirt
            'waist': 82, 'hip': 98, 'inseam': 75, 'thigh_circumference': 55  # Pants
        }
        
        result = mapper.map_size_detailed(measurements, gender='male')
        
        assert 'shirt' in result
        assert 'pants' in result
        assert 'recommended_size' in result['shirt']
        assert 'recommended_size' in result['pants']
        
        # Test reason generation
        assert 'reason' in result['shirt']
        assert 'reason' in result['pants']


class TestSizeMapperWithBrandChart:
    """Tests with actual brand size charts."""
    
    @pytest.fixture
    def mapper_with_charts(self):
        """Create mapper with size charts if available."""
        chart_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'size_chart', 'size_charts.json'
        )
        if os.path.exists(chart_path):
            return SizeMapper(chart_path)
        return SizeMapper()
    
    def test_brands_loaded(self, mapper_with_charts):
        """Test that brands are loaded from file."""
        brands = mapper_with_charts.get_available_brands()
        
        # Should have at least generic
        assert len(brands) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
