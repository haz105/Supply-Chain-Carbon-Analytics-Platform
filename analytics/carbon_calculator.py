"""
Carbon calculation engine for the Supply Chain Carbon Analytics Platform.
Implements EPA emission factors and advanced calculation methods for transportation emissions.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class EmissionFactors:
    """EPA emission factors for different transportation modes."""
    
    # CO2 emission factors (kg CO2 per ton-km)
    air_freight: float = 1.02
    ground_freight: float = 0.089
    sea_freight: float = 0.014
    
    # CH4 emission factors (kg CH4 per ton-km)
    air_freight_ch4: float = 0.0001
    ground_freight_ch4: float = 0.0002
    sea_freight_ch4: float = 0.00005
    
    # N2O emission factors (kg N2O per ton-km)
    air_freight_n2o: float = 0.00001
    ground_freight_n2o: float = 0.00002
    sea_freight_n2o: float = 0.000005
    
    # Global Warming Potentials (GWP)
    ch4_gwp: float = 25.0  # CH4 is 25x more potent than CO2 over 100 years
    n2o_gwp: float = 298.0  # N2O is 298x more potent than CO2 over 100 years


@dataclass
class WeatherImpact:
    """Weather impact factors on fuel efficiency."""
    
    temperature_factor: float = 1.0
    wind_factor: float = 1.0
    precipitation_factor: float = 1.0
    humidity_factor: float = 1.0
    
    def calculate_combined_factor(self) -> float:
        """Calculate combined weather impact factor."""
        return (
            self.temperature_factor *
            self.wind_factor *
            self.precipitation_factor *
            self.humidity_factor
        )


class CarbonCalculator:
    """Advanced carbon calculation engine with EPA factors and weather adjustments."""
    
    def __init__(self):
        """Initialize carbon calculator with emission factors."""
        self.emission_factors = EmissionFactors()
        logger.info("Carbon calculator initialized with EPA emission factors")
    
    def calculate_transport_emissions(
        self,
        distance_km: float,
        weight_kg: float,
        transport_mode: str,
        weather_impact: Optional[WeatherImpact] = None,
        load_factor: float = 0.8,
        fuel_efficiency: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate CO2 emissions based on EPA factors and operational parameters.
        
        Args:
            distance_km: Distance in kilometers
            weight_kg: Weight in kilograms
            transport_mode: 'air', 'ground', or 'sea'
            weather_impact: Weather impact factors
            load_factor: Vehicle load factor (0.0 to 1.0)
            fuel_efficiency: Fuel efficiency multiplier
            
        Returns:
            Dictionary with emission values in kg
        """
        try:
            # Validate inputs
            if distance_km <= 0 or weight_kg <= 0:
                raise ValueError("Distance and weight must be positive")
            
            if transport_mode not in ['air', 'ground', 'sea']:
                raise ValueError("Transport mode must be 'air', 'ground', or 'sea'")
            
            # Get emission factors for transport mode
            co2_factor = self._get_co2_factor(transport_mode)
            ch4_factor = self._get_ch4_factor(transport_mode)
            n2o_factor = self._get_n2o_factor(transport_mode)
            
            # Convert weight to tons
            weight_tons = weight_kg / 1000.0
            
            # Calculate base emissions
            base_co2 = co2_factor * weight_tons * distance_km
            base_ch4 = ch4_factor * weight_tons * distance_km
            base_n2o = n2o_factor * weight_tons * distance_km
            
            # Apply operational factors
            operational_factor = (1.0 / load_factor) * fuel_efficiency
            
            # Apply weather impact if provided
            weather_factor = 1.0
            if weather_impact:
                weather_factor = weather_impact.calculate_combined_factor()
            
            # Calculate final emissions
            co2_kg = base_co2 * operational_factor * weather_factor
            ch4_kg = base_ch4 * operational_factor * weather_factor
            n2o_kg = base_n2o * operational_factor * weather_factor
            
            # Calculate CO2 equivalent
            co2_equivalent_kg = (
                co2_kg +
                (ch4_kg * self.emission_factors.ch4_gwp) +
                (n2o_kg * self.emission_factors.n2o_gwp)
            )
            
            result = {
                'co2_kg': round(co2_kg, 6),
                'ch4_kg': round(ch4_kg, 6),
                'n2o_kg': round(n2o_kg, 6),
                'co2_equivalent_kg': round(co2_equivalent_kg, 6),
                'weather_factor': round(weather_factor, 4),
                'operational_factor': round(operational_factor, 4)
            }
            
            logger.debug(
                "Carbon calculation completed",
                distance_km=distance_km,
                weight_kg=weight_kg,
                transport_mode=transport_mode,
                co2_kg=result['co2_kg'],
                co2_equivalent_kg=result['co2_equivalent_kg']
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Error in carbon calculation",
                error=str(e),
                distance_km=distance_km,
                weight_kg=weight_kg,
                transport_mode=transport_mode
            )
            raise
    
    def calculate_weather_impact(
        self,
        temperature_celsius: float,
        wind_speed_kmh: float,
        wind_direction_degrees: float,
        precipitation_mm: float,
        humidity_percent: float,
        transport_mode: str
    ) -> WeatherImpact:
        """
        Calculate weather impact on fuel efficiency for different transport modes.
        
        Args:
            temperature_celsius: Temperature in Celsius
            wind_speed_kmh: Wind speed in km/h
            wind_direction_degrees: Wind direction in degrees
            precipitation_mm: Precipitation in mm
            humidity_percent: Humidity percentage
            transport_mode: Transport mode for specific calculations
            
        Returns:
            WeatherImpact object with calculated factors
        """
        try:
            # Temperature impact (optimal range: 15-25°C)
            temp_factor = self._calculate_temperature_factor(temperature_celsius, transport_mode)
            
            # Wind impact
            wind_factor = self._calculate_wind_factor(wind_speed_kmh, wind_direction_degrees, transport_mode)
            
            # Precipitation impact
            precip_factor = self._calculate_precipitation_factor(precipitation_mm, transport_mode)
            
            # Humidity impact
            humidity_factor = self._calculate_humidity_factor(humidity_percent, transport_mode)
            
            weather_impact = WeatherImpact(
                temperature_factor=temp_factor,
                wind_factor=wind_factor,
                precipitation_factor=precip_factor,
                humidity_factor=humidity_factor
            )
            
            logger.debug(
                "Weather impact calculated",
                temperature_factor=temp_factor,
                wind_factor=wind_factor,
                precipitation_factor=precip_factor,
                humidity_factor=humidity_factor,
                combined_factor=weather_impact.calculate_combined_factor()
            )
            
            return weather_impact
            
        except Exception as e:
            logger.error("Error calculating weather impact", error=str(e))
            # Return neutral factors on error
            return WeatherImpact()
    
    def calculate_supply_chain_emissions(
        self,
        shipments: List[Dict],
        include_scope_3: bool = True
    ) -> Dict[str, float]:
        """
        Calculate total emissions for a supply chain with multiple shipments.
        
        Args:
            shipments: List of shipment dictionaries
            include_scope_3: Whether to include scope 3 emissions (packaging, etc.)
            
        Returns:
            Dictionary with total emission values
        """
        try:
            total_co2 = 0.0
            total_ch4 = 0.0
            total_n2o = 0.0
            total_co2e = 0.0
            
            for shipment in shipments:
                emissions = self.calculate_transport_emissions(
                    distance_km=shipment['distance_km'],
                    weight_kg=shipment['weight_kg'],
                    transport_mode=shipment['transport_mode'],
                    weather_impact=shipment.get('weather_impact'),
                    load_factor=shipment.get('load_factor', 0.8),
                    fuel_efficiency=shipment.get('fuel_efficiency', 1.0)
                )
                
                total_co2 += emissions['co2_kg']
                total_ch4 += emissions['ch4_kg']
                total_n2o += emissions['n2o_kg']
                total_co2e += emissions['co2_equivalent_kg']
            
            # Add scope 3 emissions if requested
            scope_3_emissions = 0.0
            if include_scope_3:
                scope_3_emissions = self._calculate_scope_3_emissions(shipments)
                total_co2e += scope_3_emissions
            
            result = {
                'total_co2_kg': round(total_co2, 6),
                'total_ch4_kg': round(total_ch4, 6),
                'total_n2o_kg': round(total_n2o, 6),
                'total_co2_equivalent_kg': round(total_co2e, 6),
                'scope_3_emissions_kg': round(scope_3_emissions, 6),
                'shipment_count': len(shipments)
            }
            
            logger.info(
                "Supply chain emissions calculated",
                total_co2_kg=result['total_co2_kg'],
                total_co2_equivalent_kg=result['total_co2_equivalent_kg'],
                shipment_count=result['shipment_count']
            )
            
            return result
            
        except Exception as e:
            logger.error("Error calculating supply chain emissions", error=str(e))
            raise
    
    def _get_co2_factor(self, transport_mode: str) -> float:
        """Get CO2 emission factor for transport mode."""
        factors = {
            'air': self.emission_factors.air_freight,
            'ground': self.emission_factors.ground_freight,
            'sea': self.emission_factors.sea_freight
        }
        return factors.get(transport_mode, 0.0)
    
    def _get_ch4_factor(self, transport_mode: str) -> float:
        """Get CH4 emission factor for transport mode."""
        factors = {
            'air': self.emission_factors.air_freight_ch4,
            'ground': self.emission_factors.ground_freight_ch4,
            'sea': self.emission_factors.sea_freight_ch4
        }
        return factors.get(transport_mode, 0.0)
    
    def _get_n2o_factor(self, transport_mode: str) -> float:
        """Get N2O emission factor for transport mode."""
        factors = {
            'air': self.emission_factors.air_freight_n2o,
            'ground': self.emission_factors.ground_freight_n2o,
            'sea': self.emission_factors.sea_freight_n2o
        }
        return factors.get(transport_mode, 0.0)
    
    def _calculate_temperature_factor(self, temperature_celsius: float, transport_mode: str) -> float:
        """Calculate temperature impact on fuel efficiency."""
        # Optimal temperature range: 15-25°C
        optimal_min = 15.0
        optimal_max = 25.0
        
        if optimal_min <= temperature_celsius <= optimal_max:
            return 1.0
        
        # Calculate deviation from optimal range
        if temperature_celsius < optimal_min:
            deviation = optimal_min - temperature_celsius
        else:
            deviation = temperature_celsius - optimal_max
        
        # Temperature impact varies by transport mode
        impact_multiplier = {
            'air': 0.02,  # Air transport is less sensitive to temperature
            'ground': 0.03,  # Ground transport is moderately sensitive
            'sea': 0.01  # Sea transport is least sensitive
        }.get(transport_mode, 0.02)
        
        factor = 1.0 + (deviation * impact_multiplier)
        return max(0.8, min(1.2, factor))  # Clamp between 0.8 and 1.2
    
    def _calculate_wind_factor(self, wind_speed_kmh: float, wind_direction_degrees: float, transport_mode: str) -> float:
        """Calculate wind impact on fuel efficiency."""
        if transport_mode == 'air':
            # Air transport is most affected by wind
            if wind_speed_kmh > 50:  # Strong winds
                return 1.15
            elif wind_speed_kmh > 25:  # Moderate winds
                return 1.08
            else:
                return 1.0
        elif transport_mode == 'ground':
            # Ground transport is moderately affected by wind
            if wind_speed_kmh > 40:  # Strong winds
                return 1.05
            else:
                return 1.0
        else:  # sea
            # Sea transport is least affected by wind
            return 1.0
    
    def _calculate_precipitation_factor(self, precipitation_mm: float, transport_mode: str) -> float:
        """Calculate precipitation impact on fuel efficiency."""
        if transport_mode == 'ground':
            # Ground transport is most affected by precipitation
            if precipitation_mm > 10:  # Heavy rain
                return 1.12
            elif precipitation_mm > 5:  # Moderate rain
                return 1.06
            else:
                return 1.0
        elif transport_mode == 'air':
            # Air transport is moderately affected
            if precipitation_mm > 5:
                return 1.05
            else:
                return 1.0
        else:  # sea
            # Sea transport is least affected
            return 1.0
    
    def _calculate_humidity_factor(self, humidity_percent: float, transport_mode: str) -> float:
        """Calculate humidity impact on fuel efficiency."""
        # High humidity can affect engine performance
        if humidity_percent > 80:
            return 1.02
        elif humidity_percent > 60:
            return 1.01
        else:
            return 1.0
    
    def _calculate_scope_3_emissions(self, shipments: List[Dict]) -> float:
        """Calculate scope 3 emissions (packaging, warehousing, etc.)."""
        total_scope_3 = 0.0
        
        for shipment in shipments:
            weight_kg = shipment['weight_kg']
            
            # Packaging emissions (estimated 0.1 kg CO2e per kg of goods)
            packaging_emissions = weight_kg * 0.1
            
            # Warehousing emissions (estimated 0.05 kg CO2e per kg per day)
            # Assuming average 2 days in warehouse
            warehousing_emissions = weight_kg * 0.05 * 2
            
            total_scope_3 += packaging_emissions + warehousing_emissions
        
        return total_scope_3 