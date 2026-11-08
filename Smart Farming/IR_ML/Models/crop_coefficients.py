"""
Crop Coefficient Database for Irrigation Management
Based on FAO-56 standard crop coefficients (Kc values)
"""

CROP_COEFFICIENTS = {
    'rice': {
        'initial': 1.05,
        'mid': 1.20,
        'late': 0.90,
        'max_height': 1.0,
        'root_depth': 0.5,
        'depletion_fraction': 0.2
    },
    'maize': {
        'initial': 0.30,
        'mid': 1.20,
        'late': 0.60,
        'max_height': 2.0,
        'root_depth': 0.8,
        'depletion_fraction': 0.55
    },
    'wheat': {
        'initial': 0.30,
        'mid': 1.15,
        'late': 0.40,
        'max_height': 1.0,
        'root_depth': 0.7,
        'depletion_fraction': 0.55
    },
    'cotton': {
        'initial': 0.35,
        'mid': 1.15,
        'late': 0.70,
        'max_height': 1.5,
        'root_depth': 1.2,
        'depletion_fraction': 0.6
    },
    'sugarcane': {
        'initial': 0.40,
        'mid': 1.25,
        'late': 0.75,
        'max_height': 3.0,
        'root_depth': 1.5,
        'depletion_fraction': 0.65
    },
    'potato': {
        'initial': 0.45,
        'mid': 1.15,
        'late': 0.75,
        'max_height': 0.6,
        'root_depth': 0.4,
        'depletion_fraction': 0.35
    },
    'tomato': {
        'initial': 0.60,
        'mid': 1.15,
        'late': 0.80,
        'max_height': 0.8,
        'root_depth': 0.6,
        'depletion_fraction': 0.40
    },
    'chickpea': {
        'initial': 0.40,
        'mid': 1.05,
        'late': 0.30,
        'max_height': 0.5,
        'root_depth': 0.6,
        'depletion_fraction': 0.5
    },
    'lentil': {
        'initial': 0.40,
        'mid': 1.10,
        'late': 0.35,
        'max_height': 0.4,
        'root_depth': 0.5,
        'depletion_fraction': 0.5
    },
    'mungbean': {
        'initial': 0.40,
        'mid': 1.05,
        'late': 0.35,
        'max_height': 0.4,
        'root_depth': 0.5,
        'depletion_fraction': 0.45
    },
    'blackgram': {
        'initial': 0.40,
        'mid': 1.05,
        'late': 0.35,
        'max_height': 0.4,
        'root_depth': 0.5,
        'depletion_fraction': 0.45
    },
    'pigeonpeas': {
        'initial': 0.40,
        'mid': 1.10,
        'late': 0.45,
        'max_height': 1.5,
        'root_depth': 1.0,
        'depletion_fraction': 0.5
    },
    'soybean': {
        'initial': 0.40,
        'mid': 1.10,
        'late': 0.45,
        'max_height': 0.8,
        'root_depth': 0.6,
        'depletion_fraction': 0.5
    },
    'groundnut': {
        'initial': 0.45,
        'mid': 1.05,
        'late': 0.60,
        'max_height': 0.5,
        'root_depth': 0.5,
        'depletion_fraction': 0.5
    },
    'mustard': {
        'initial': 0.35,
        'mid': 1.10,
        'late': 0.35,
        'max_height': 1.0,
        'root_depth': 0.6,
        'depletion_fraction': 0.5
    },
    'sunflower': {
        'initial': 0.35,
        'mid': 1.15,
        'late': 0.40,
        'max_height': 2.0,
        'root_depth': 0.8,
        'depletion_fraction': 0.45
    },
    'banana': {
        'initial': 0.95,
        'mid': 1.10,
        'late': 1.05,
        'max_height': 4.0,
        'root_depth': 0.5,
        'depletion_fraction': 0.4
    },
    'mango': {
        'initial': 0.70,
        'mid': 0.90,
        'late': 0.75,
        'max_height': 10.0,
        'root_depth': 1.5,
        'depletion_fraction': 0.5
    },
    'grapes': {
        'initial': 0.30,
        'mid': 0.85,
        'late': 0.60,
        'max_height': 2.0,
        'root_depth': 1.2,
        'depletion_fraction': 0.45
    },
    'apple': {
        'initial': 0.45,
        'mid': 0.95,
        'late': 0.70,
        'max_height': 4.0,
        'root_depth': 1.0,
        'depletion_fraction': 0.5
    },
    'orange': {
        'initial': 0.70,
        'mid': 0.75,
        'late': 0.70,
        'max_height': 5.0,
        'root_depth': 1.2,
        'depletion_fraction': 0.5
    },
    'coconut': {
        'initial': 0.85,
        'mid': 0.95,
        'late': 0.90,
        'max_height': 15.0,
        'root_depth': 0.8,
        'depletion_fraction': 0.5
    },
    'coffee': {
        'initial': 0.90,
        'mid': 0.95,
        'late': 0.90,
        'max_height': 3.0,
        'root_depth': 0.8,
        'depletion_fraction': 0.4
    },
    'jute': {
        'initial': 0.45,
        'mid': 1.10,
        'late': 0.70,
        'max_height': 3.0,
        'root_depth': 0.5,
        'depletion_fraction': 0.5
    },
    'papaya': {
        'initial': 0.50,
        'mid': 1.00,
        'late': 0.80,
        'max_height': 5.0,
        'root_depth': 0.5,
        'depletion_fraction': 0.4
    },
    'pomegranate': {
        'initial': 0.40,
        'mid': 0.80,
        'late': 0.65,
        'max_height': 4.0,
        'root_depth': 1.0,
        'depletion_fraction': 0.5
    },
    'watermelon': {
        'initial': 0.45,
        'mid': 1.00,
        'late': 0.75,
        'max_height': 0.3,
        'root_depth': 0.4,
        'depletion_fraction': 0.4
    },
    'muskmelon': {
        'initial': 0.45,
        'mid': 1.00,
        'late': 0.75,
        'max_height': 0.3,
        'root_depth': 0.4,
        'depletion_fraction': 0.4
    }
}

# Soil water holding capacity (mm/m) for different soil types
SOIL_WATER_CAPACITY = {
    'sand': 60,
    'loamy_sand': 90,
    'sandy_loam': 120,
    'loam': 150,
    'silt_loam': 170,
    'sandy_clay_loam': 160,
    'clay_loam': 180,
    'silty_clay_loam': 190,
    'sandy_clay': 170,
    'silty_clay': 200,
    'clay': 220
}

# Default values for missing inputs
DEFAULT_VALUES = {
    'temperature': 25.0,
    'humidity': 60.0,
    'wind_speed': 2.0,
    'soil_moisture': 50.0,
    'soil_type': 'loam',
    'crop_type': 'rice',
    'growth_stage': 'mid',
    'recent_rainfall_mm': 0.0,
    'rainfall_days_ago': 7,
    'acres': 1.0
}

def get_crop_coefficient(crop_type, growth_stage='mid'):
    """
    Get crop coefficient (Kc) for a specific crop and growth stage.

    Args:
        crop_type: Name of the crop
        growth_stage: 'initial', 'mid', or 'late'

    Returns:
        Kc value or None if crop not found
    """
    crop_type_lower = crop_type.lower().strip()

    # Try exact match
    if crop_type_lower in CROP_COEFFICIENTS:
        return CROP_COEFFICIENTS[crop_type_lower].get(growth_stage)

    # Try to find partial match
    for crop, data in CROP_COEFFICIENTS.items():
        if crop_type_lower in crop or crop in crop_type_lower:
            return data.get(growth_stage)

    return None

def get_crop_info(crop_type):
    """
    Get complete crop information including all Kc values and parameters.

    Args:
        crop_type: Name of the crop

    Returns:
        Dictionary with crop parameters or None
    """
    crop_type_lower = crop_type.lower().strip()

    if crop_type_lower in CROP_COEFFICIENTS:
        return CROP_COEFFICIENTS[crop_type_lower]

    # Try partial match
    for crop, data in CROP_COEFFICIENTS.items():
        if crop_type_lower in crop or crop in crop_type_lower:
            return data

    return None

def get_soil_water_capacity(soil_type):
    """
    Get soil water holding capacity.

    Args:
        soil_type: Type of soil

    Returns:
        Water capacity in mm/m
    """
    soil_type_lower = soil_type.lower().strip()

    if soil_type_lower in SOIL_WATER_CAPACITY:
        return SOIL_WATER_CAPACITY[soil_type_lower]

    # Default to loam if not found
    return SOIL_WATER_CAPACITY['loam']
