"""
Irrigation Model Testing and Evaluation Script
Tests the irrigation model with various scenarios
"""

from IR_model_irrigation import IrrigationModel

def test_basic_scenarios():
    """Test basic irrigation scenarios."""
    print("="*60)
    print("TESTING BASIC IRRIGATION SCENARIOS")
    print("="*60 + "\n")

    model = IrrigationModel()

    scenarios = [
        {
            'name': 'Very Dry - No Rain',
            'params': {
                'soil_moisture': 15,
                'recent_rainfall_mm': 0,
                'rainfall_days_ago': 15,
                'temperature': 38,
                'humidity': 30,
                'wind_speed': 4,
                'soil_type': 'sand',
                'crop_type': 'maize',
                'growth_stage': 'mid',
                'acres': 2
            }
        },
        {
            'name': 'Moderate - Light Rain Recently',
            'params': {
                'soil_moisture': 40,
                'recent_rainfall_mm': 20,
                'rainfall_days_ago': 2,
                'temperature': 30,
                'humidity': 55,
                'wind_speed': 2,
                'soil_type': 'loam',
                'crop_type': 'wheat',
                'growth_stage': 'mid',
                'acres': 3
            }
        },
        {
            'name': 'Wet - Heavy Rain Recently',
            'params': {
                'soil_moisture': 80,
                'recent_rainfall_mm': 80,
                'rainfall_days_ago': 1,
                'temperature': 22,
                'humidity': 85,
                'wind_speed': 1,
                'soil_type': 'clay',
                'crop_type': 'rice',
                'growth_stage': 'mid',
                'acres': 1
            }
        },
        {
            'name': 'Marginal - Borderline',
            'params': {
                'soil_moisture': 50,
                'recent_rainfall_mm': 10,
                'rainfall_days_ago': 5,
                'temperature': 28,
                'humidity': 60,
                'wind_speed': 2,
                'soil_type': 'sandy_loam',
                'crop_type': 'cotton',
                'growth_stage': 'mid',
                'acres': 5
            }
        }
    ]

    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        print("-" * 60)
        result = model.predict(scenario['params'])

        print(f"Irrigation Required: {result['irrigation_required']}")
        print(f"Water Needed: {result['water_amount_liters_per_sqm']} L/m²")
        print(f"Total Water: {result['total_water_liters']:,.0f} L ({result['total_water_cubic_meters']:,.1f} m³)")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"\nDetails:")
        print(f"  - Reference ET: {result['details']['reference_evapotranspiration']} mm/day")
        print(f"  - Crop ET: {result['details']['crop_evapotranspiration']} mm/day")
        print(f"  - Effective Rainfall: {result['details']['effective_rainfall']} mm")
        print(f"  - Soil Water Deficit: {result['details']['soil_water_deficit']} mm")
        print(f"  - Current Soil Water: {result['details']['current_soil_water']} mm")
        print()

def test_different_crops():
    """Test irrigation requirements for different crops."""
    print("="*60)
    print("TESTING DIFFERENT CROPS")
    print("="*60 + "\n")

    model = IrrigationModel()

    crops = ['rice', 'maize', 'wheat', 'cotton', 'sugarcane', 'potato']

    base_params = {
        'soil_moisture': 35,
        'recent_rainfall_mm': 5,
        'rainfall_days_ago': 7,
        'temperature': 30,
        'humidity': 50,
        'wind_speed': 2,
        'soil_type': 'loam',
        'growth_stage': 'mid',
        'acres': 1
    }

    print(f"{'Crop':<15} {'Irrigation':<12} {'Water (L/m²)':<15} {'Total (L)':<15}")
    print("-" * 60)

    for crop in crops:
        params = base_params.copy()
        params['crop_type'] = crop
        result = model.predict(params)

        print(f"{crop:<15} {str(result['irrigation_required']):<12} "
              f"{result['water_amount_liters_per_sqm']:<15.2f} "
              f"{result['total_water_liters']:,.0f}")

    print()

def test_different_soil_types():
    """Test irrigation requirements for different soil types."""
    print("="*60)
    print("TESTING DIFFERENT SOIL TYPES")
    print("="*60 + "\n")

    model = IrrigationModel()

    soil_types = ['sand', 'loamy_sand', 'sandy_loam', 'loam', 'clay_loam', 'clay']

    base_params = {
        'soil_moisture': 30,
        'recent_rainfall_mm': 10,
        'rainfall_days_ago': 5,
        'temperature': 32,
        'humidity': 45,
        'wind_speed': 2.5,
        'crop_type': 'maize',
        'growth_stage': 'mid',
        'acres': 1
    }

    print(f"{'Soil Type':<15} {'Irrigation':<12} {'Water (L/m²)':<15} {'Total (L)':<15}")
    print("-" * 60)

    for soil in soil_types:
        params = base_params.copy()
        params['soil_type'] = soil
        result = model.predict(params)

        print(f"{soil:<15} {str(result['irrigation_required']):<12} "
              f"{result['water_amount_liters_per_sqm']:<15.2f} "
              f"{result['total_water_liters']:,.0f}")

    print()

def test_missing_parameters():
    """Test model with missing parameters (should use defaults)."""
    print("="*60)
    print("TESTING WITH MISSING PARAMETERS")
    print("="*60 + "\n")

    model = IrrigationModel()

    # Test with minimal parameters
    minimal_params = {
        'soil_moisture': 25,
        'crop_type': 'rice',
        'acres': 2
    }

    print("Minimal parameters provided:")
    print(f"  - soil_moisture: {minimal_params['soil_moisture']}")
    print(f"  - crop_type: {minimal_params['crop_type']}")
    print(f"  - acres: {minimal_params['acres']}")
    print(f"\nModel should use defaults for other parameters\n")

    result = model.predict(minimal_params)

    print(f"Irrigation Required: {result['irrigation_required']}")
    print(f"Water Needed: {result['water_amount_liters_per_sqm']} L/m²")
    print(f"Total Water: {result['total_water_liters']:,.0f} L ({result['total_water_cubic_meters']:,.1f} m³)")
    print(f"Confidence: {result['confidence']:.2f}")
    print()

def test_growth_stages():
    """Test irrigation requirements at different growth stages."""
    print("="*60)
    print("TESTING DIFFERENT GROWTH STAGES")
    print("="*60 + "\n")

    model = IrrigationModel()

    growth_stages = ['initial', 'mid', 'late']

    base_params = {
        'soil_moisture': 40,
        'recent_rainfall_mm': 5,
        'rainfall_days_ago': 7,
        'temperature': 28,
        'humidity': 55,
        'wind_speed': 2,
        'soil_type': 'loam',
        'crop_type': 'maize',
        'acres': 1
    }

    print(f"{'Growth Stage':<15} {'Irrigation':<12} {'Water (L/m²)':<15} {'Total (L)':<15}")
    print("-" * 60)

    for stage in growth_stages:
        params = base_params.copy()
        params['growth_stage'] = stage
        result = model.predict(params)

        print(f"{stage:<15} {str(result['irrigation_required']):<12} "
              f"{result['water_amount_liters_per_sqm']:<15.2f} "
              f"{result['total_water_liters']:,.0f}")

    print()

def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("IRRIGATION MODEL - COMPREHENSIVE TESTING")
    print("="*60 + "\n")

    test_basic_scenarios()
    test_different_crops()
    test_different_soil_types()
    test_missing_parameters()
    test_growth_stages()

    print("="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
