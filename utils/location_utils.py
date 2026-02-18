# utils/location_utils.py
import re

def extract_location(text, known_areas):
    """Extract specific location from text"""
    text_lower = text.lower()
    
    for area in known_areas:
        if area in text_lower or area.replace('-', ' ') in text_lower:
            return area.title()
    
    return None

def classify_location(area, location_features):
    """Classify location by category"""
    if area in location_features:
        return location_features[area]['category']
    return 'unknown'

def estimate_distance_to_cbd(area, location_features):
    """Estimate distance to CBD in km"""
    if area in location_features:
        return location_features[area]['distance_to_cbd']
    return None