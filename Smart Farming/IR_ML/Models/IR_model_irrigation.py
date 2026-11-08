"""
Irrigation Management Model
Based on FAO-56 Penman-Monteith equation and soil water balance
Calculates irrigation requirement and water amount
"""

import math
from crop_coefficients import (
    get_crop_coefficient,
    get_crop_info,
    get_soil_water_capacity,
    DEFAULT_VALUES
)

class IrrigationModel:
    """
    Irrigation Management Model using agricultural scientific formulas.
    Based on FAO-56 guidelines for crop water requirements.
    """

    def __init__(self):
        self.model_name = "FAO-56 Irrigation Model"
        self.version = "1.0"

    def calculate_reference_evapotranspiration(self, temperature, humidity, wind_speed):
        """
        Calculate Reference Evapotranspiration (ETo) using simplified Penman-Monteith.

        Args:
            temperature: Temperature in Celsius
            humidity: Relative humidity in percentage
            wind_speed: Wind speed in m/s at 2m height

        Returns:
            ETo in mm/day
        """
        # Simplified Hargreaves equation (more practical when full weather data unavailable)
        # ETo = 0.0023 * (Tmean + 17.8) * sqrt(Tmax - Tmin) * Ra
        # Using temperature as proxy

        # Convert to absolute if needed
        temp = max(temperature, 0)  # Ensure non-negative

        # Simplified formula based on temperature and humidity
        # Lower humidity = higher evapotranspiration
        humidity_factor = 1 - (humidity / 200)  # Humidity reduces ETo

        # Wind increases evapotranspiration
        wind_factor = 1 + (wind_speed / 10)

        # Base ETo from temperature
        base_eto = 0.2 * temp

        # Apply factors
        eto = base_eto * humidity_factor * wind_factor

        # Reasonable bounds (typical ETo range: 2-8 mm/day)
        eto = max(2.0, min(eto, 8.0))

        return eto

    def calculate_crop_evapotranspiration(self, eto, crop_type, growth_stage='mid'):
        """
        Calculate Crop Evapotranspiration (ETc) = Kc × ETo

        Args:
            eto: Reference evapotranspiration in mm/day
            crop_type: Type of crop
            growth_stage: 'initial', 'mid', or 'late'

        Returns:
            ETc in mm/day
        """
        kc = get_crop_coefficient(crop_type, growth_stage)

        if kc is None:
            # Default to typical value if crop not found
            kc = 1.0

        etc = kc * eto
        return etc

    def calculate_rainfall_effectiveness(self, rainfall_mm, days_ago):
        """
        Calculate effective rainfall considering time since rainfall.

        Args:
            rainfall_mm: Amount of rainfall in mm
            days_ago: Days since rainfall

        Returns:
            Effective rainfall in mm (decreases over time)
        """
        if rainfall_mm <= 0:
            return 0.0

        # Rainfall effectiveness decreases over time due to evaporation and drainage
        # Exponential decay factor
        decay_factor = math.exp(-days_ago / 5)  # 5-day half-life equivalent

        effective_rainfall = rainfall_mm * decay_factor

        # Maximum 7 days of rainfall effect
        if days_ago > 7:
            effective_rainfall = 0.0

        return effective_rainfall

    def calculate_soil_water_balance(self, soil_moisture, soil_type, root_depth, depletion_fraction):
        """
        Calculate available soil water and irrigation trigger point.

        Args:
            soil_moisture: Current soil moisture percentage
            soil_type: Type of soil
            root_depth: Root depth in meters
            depletion_fraction: Fraction of available water that can be depleted

        Returns:
            Dictionary with water balance information
        """
        # Get soil water holding capacity
        water_capacity = get_soil_water_capacity(soil_type)  # mm/m

        # Total available water in root zone
        total_available_water = water_capacity * root_depth  # mm

        # Current soil water (convert percentage to mm)
        current_soil_water = (soil_moisture / 100) * total_available_water

        # Irrigation trigger point (when soil water drops below this)
        irrigation_trigger = total_available_water * (1 - depletion_fraction)

        # Water deficit
        water_deficit = irrigation_trigger - current_soil_water

        return {
            'total_available_water': total_available_water,
            'current_soil_water': current_soil_water,
            'irrigation_trigger': irrigation_trigger,
            'water_deficit': max(0, water_deficit)
        }

    def calculate_irrigation_requirement(self, input_params):
        """
        Calculate irrigation requirement and water amount.

        Args:
            input_params: Dictionary with:
                - soil_moisture: Current soil moisture percentage
                - recent_rainfall_mm: Recent rainfall in mm
                - rainfall_days_ago: Days since rainfall
                - temperature: Temperature in Celsius
                - humidity: Relative humidity percentage
                - wind_speed: Wind speed in m/s
                - soil_type: Type of soil
                - crop_type: Type of crop
                - growth_stage: Growth stage ('initial', 'mid', 'late')
                - acres: Land area in acres

        Returns:
            Dictionary with irrigation recommendation
        """
        # Fill missing values with defaults
        params = DEFAULT_VALUES.copy()
        params.update(input_params)

        # Extract parameters
        soil_moisture = params['soil_moisture']
        rainfall_mm = params['recent_rainfall_mm']
        rainfall_days_ago = params['rainfall_days_ago']
        temperature = params['temperature']
        humidity = params['humidity']
        wind_speed = params['wind_speed']
        soil_type = params['soil_type']
        crop_type = params['crop_type']
        growth_stage = params['growth_stage']
        acres = params['acres']

        # Get crop information
        crop_info = get_crop_info(crop_type)
        if crop_info is None:
            crop_info = get_crop_info('rice')  # Default to rice

        root_depth = crop_info['root_depth']
        depletion_fraction = crop_info['depletion_fraction']

        # Step 1: Calculate Reference Evapotranspiration (ETo)
        eto = self.calculate_reference_evapotranspiration(temperature, humidity, wind_speed)

        # Step 2: Calculate Crop Evapotranspiration (ETc)
        etc = self.calculate_crop_evapotranspiration(eto, crop_type, growth_stage)

        # Step 3: Calculate Effective Rainfall
        effective_rainfall = self.calculate_rainfall_effectiveness(rainfall_mm, rainfall_days_ago)

        # Step 4: Calculate Soil Water Balance
        water_balance = self.calculate_soil_water_balance(
            soil_moisture, soil_type, root_depth, depletion_fraction
        )

        # Step 5: Determine Irrigation Requirement
        # Irrigation needed if water deficit > 0 AND effective rainfall is insufficient
        water_needed = water_balance['water_deficit']

        # Subtract effective rainfall from water needed
        net_water_needed = max(0, water_needed - effective_rainfall)

        # Step 6: Determine if irrigation is required
        irrigation_required = net_water_needed > 1.0  # Threshold: > 1mm needed

        # Step 7: Calculate irrigation amount (if needed)
        if irrigation_required:
            irrigation_amount_mm = net_water_needed
            # Add efficiency factor (irrigation is not 100% efficient)
            irrigation_efficiency = 0.75  # 75% efficiency typical
            irrigation_amount_mm = irrigation_amount_mm / irrigation_efficiency
        else:
            irrigation_amount_mm = 0.0

        # Step 8: Convert to practical units
        # 1 mm = 1 liter per square meter
        irrigation_liters_per_sqm = irrigation_amount_mm

        # Calculate total water for given area
        # 1 acre = 4046.86 square meters
        area_sqm = acres * 4046.86
        total_water_liters = irrigation_liters_per_sqm * area_sqm

        # Convert to more readable units
        total_water_cubic_meters = total_water_liters / 1000  # 1 m³ = 1000 liters

        # Calculate confidence score
        confidence = self._calculate_confidence(params, water_balance, effective_rainfall)

        return {
            'irrigation_required': irrigation_required,
            'water_amount_mm': round(irrigation_amount_mm, 2),
            'water_amount_liters_per_sqm': round(irrigation_liters_per_sqm, 2),
            'total_water_liters': round(total_water_liters, 2),
            'total_water_cubic_meters': round(total_water_cubic_meters, 2),
            'confidence': round(confidence, 2),
            'details': {
                'reference_evapotranspiration': round(eto, 2),
                'crop_evapotranspiration': round(etc, 2),
                'effective_rainfall': round(effective_rainfall, 2),
                'soil_water_deficit': round(water_balance['water_deficit'], 2),
                'current_soil_water': round(water_balance['current_soil_water'], 2),
                'irrigation_trigger': round(water_balance['irrigation_trigger'], 2)
            }
        }

    def _calculate_confidence(self, params, water_balance, effective_rainfall):
        """
        Calculate confidence score for the recommendation.

        Args:
            params: Input parameters
            water_balance: Soil water balance results
            effective_rainfall: Effective rainfall

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Increase confidence if soil moisture is provided
        if 'soil_moisture' in params and params['soil_moisture'] > 0:
            confidence += 0.2

        # Increase confidence if rainfall data is recent
        if params['rainfall_days_ago'] <= 3:
            confidence += 0.1

        # Increase confidence if water deficit is clear
        if water_balance['water_deficit'] > 5 or water_balance['water_deficit'] < -5:
            confidence += 0.1

        # Decrease confidence if conditions are marginal
        if abs(water_balance['water_deficit']) < 2:
            confidence -= 0.1

        # Ensure bounds
        confidence = max(0.3, min(confidence, 0.95))

        return confidence

    def predict(self, input_params):
        """
        Main prediction function - same as calculate_irrigation_requirement.

        Args:
            input_params: Dictionary with input parameters

        Returns:
            Dictionary with irrigation recommendation
        """
        return self.calculate_irrigation_requirement(input_params)


def main():
    """Test the irrigation model with sample data."""
    model = IrrigationModel()

    # Test case 1: Dry conditions, no recent rain
    print("Test Case 1: Dry conditions")
    params1 = {
        'soil_moisture': 20,
        'recent_rainfall_mm': 0,
        'rainfall_days_ago': 10,
        'temperature': 35,
        'humidity': 40,
        'wind_speed': 3,
        'soil_type': 'sandy_loam',
        'crop_type': 'maize',
        'growth_stage': 'mid',
        'acres': 2
    }
    result1 = model.predict(params1)
    print(f"Irrigation Required: {result1['irrigation_required']}")
    print(f"Water Amount: {result1['water_amount_liters_per_sqm']} L/m²")
    print(f"Total Water: {result1['total_water_liters']} L ({result1['total_water_cubic_meters']} m³)")
    print(f"Confidence: {result1['confidence']}\n")

    # Test case 2: Wet conditions, recent rain
    print("Test Case 2: Wet conditions")
    params2 = {
        'soil_moisture': 70,
        'recent_rainfall_mm': 50,
        'rainfall_days_ago': 1,
        'temperature': 25,
        'humidity': 80,
        'wind_speed': 1,
        'soil_type': 'clay',
        'crop_type': 'rice',
        'growth_stage': 'mid',
        'acres': 1
    }
    result2 = model.predict(params2)
    print(f"Irrigation Required: {result2['irrigation_required']}")
    print(f"Water Amount: {result2['water_amount_liters_per_sqm']} L/m²")
    print(f"Total Water: {result2['total_water_liters']} L ({result2['total_water_cubic_meters']} m³)")
    print(f"Confidence: {result2['confidence']}\n")

    # Test case 3: Marginal conditions
    print("Test Case 3: Marginal conditions")
    params3 = {
        'soil_moisture': 45,
        'recent_rainfall_mm': 15,
        'rainfall_days_ago': 4,
        'temperature': 28,
        'humidity': 60,
        'wind_speed': 2,
        'soil_type': 'loam',
        'crop_type': 'wheat',
        'growth_stage': 'mid',
        'acres': 5
    }
    result3 = model.predict(params3)
    print(f"Irrigation Required: {result3['irrigation_required']}")
    print(f"Water Amount: {result3['water_amount_liters_per_sqm']} L/m²")
    print(f"Total Water: {result3['total_water_liters']} L ({result3['total_water_cubic_meters']} m³)")
    print(f"Confidence: {result3['confidence']}\n")

    print("Model test completed successfully!")


if __name__ == "__main__":
    main()
