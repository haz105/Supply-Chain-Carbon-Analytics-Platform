"""
Shipment data generator for the Supply Chain Carbon Analytics Platform.
Generates realistic synthetic shipment data with seasonal patterns and geographic distributions.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from geopy.distance import geodesic
import structlog

logger = structlog.get_logger(__name__)


class ShipmentGenerator:
    """Generates realistic synthetic shipment data for carbon analytics."""
    
    def __init__(self):
        """Initialize shipment generator with US city data and patterns."""
        self.major_cities = self._load_major_cities()
        self.package_types = self._load_package_types()
        self.transport_modes = ['air', 'ground', 'sea']
        self.carriers = self._load_carriers()
        
        logger.info("Shipment generator initialized", city_count=len(self.major_cities))
    
    def generate_shipments(
        self,
        num_shipments: int,
        start_date: datetime,
        end_date: datetime,
        include_seasonal_patterns: bool = True
    ) -> List[Dict]:
        """
        Generate synthetic shipment data with realistic patterns.
        
        Args:
            num_shipments: Number of shipments to generate
            start_date: Start date for shipment period
            end_date: End date for shipment period
            include_seasonal_patterns: Whether to include seasonal variations
            
        Returns:
            List of shipment dictionaries
        """
        try:
            shipments = []
            
            # Generate base shipment data
            for i in range(num_shipments):
                shipment = self._generate_single_shipment(
                    start_date, end_date, include_seasonal_patterns
                )
                shipments.append(shipment)
                
                if (i + 1) % 1000 == 0:
                    logger.info(f"Generated {i + 1} shipments")
            
            logger.info(
                "Shipment generation completed",
                total_shipments=len(shipments),
                date_range=f"{start_date.date()} to {end_date.date()}"
            )
            
            return shipments
            
        except Exception as e:
            logger.error("Error generating shipments", error=str(e))
            raise
    
    def _generate_single_shipment(
        self,
        start_date: datetime,
        end_date: datetime,
        include_seasonal_patterns: bool
    ) -> Dict:
        """Generate a single shipment with realistic parameters."""
        
        # Select origin and destination cities
        origin_city = random.choice(self.major_cities)
        destination_city = random.choice(self.major_cities)
        
        # Ensure origin and destination are different
        while destination_city['name'] == origin_city['name']:
            destination_city = random.choice(self.major_cities)
        
        # Calculate distance
        distance_km = self._calculate_distance(
            origin_city['lat'], origin_city['lng'],
            destination_city['lat'], destination_city['lng']
        )
        
        # Determine transport mode based on distance and seasonal factors
        transport_mode = self._select_transport_mode(distance_km, include_seasonal_patterns)
        
        # Generate weight based on transport mode and package type
        weight_kg = self._generate_weight(transport_mode)
        
        # Generate timing with seasonal patterns
        departure_time, arrival_time = self._generate_timing(
            start_date, end_date, distance_km, transport_mode, include_seasonal_patterns
        )
        
        # Select package type
        package_type = self._select_package_type(weight_kg, transport_mode)
        
        # Generate shipment
        shipment = {
            'shipment_id': str(uuid.uuid4()),
            'origin_lat': origin_city['lat'],
            'origin_lng': origin_city['lng'],
            'origin_city': origin_city['name'],
            'destination_lat': destination_city['lat'],
            'destination_lng': destination_city['lng'],
            'destination_city': destination_city['name'],
            'transport_mode': transport_mode,
            'weight_kg': round(weight_kg, 2),
            'distance_km': round(distance_km, 2),
            'package_type': package_type,
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'carrier_id': str(uuid.uuid4()),
            'created_at': datetime.now()
        }
        
        return shipment
    
    def _load_major_cities(self) -> List[Dict]:
        """Load major US cities with coordinates."""
        return [
            {'name': 'New York', 'lat': 40.7128, 'lng': -74.0060},
            {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437},
            {'name': 'Chicago', 'lat': 41.8781, 'lng': -87.6298},
            {'name': 'Houston', 'lat': 29.7604, 'lng': -95.3698},
            {'name': 'Phoenix', 'lat': 33.4484, 'lng': -112.0740},
            {'name': 'Philadelphia', 'lat': 39.9526, 'lng': -75.1652},
            {'name': 'San Antonio', 'lat': 29.4241, 'lng': -98.4936},
            {'name': 'San Diego', 'lat': 32.7157, 'lng': -117.1611},
            {'name': 'Dallas', 'lat': 32.7767, 'lng': -96.7970},
            {'name': 'San Jose', 'lat': 37.3382, 'lng': -121.8863},
            {'name': 'Austin', 'lat': 30.2672, 'lng': -97.7431},
            {'name': 'Jacksonville', 'lat': 30.3322, 'lng': -81.6557},
            {'name': 'Fort Worth', 'lat': 32.7555, 'lng': -97.3308},
            {'name': 'Columbus', 'lat': 39.9612, 'lng': -82.9988},
            {'name': 'Charlotte', 'lat': 35.2271, 'lng': -80.8431},
            {'name': 'San Francisco', 'lat': 37.7749, 'lng': -122.4194},
            {'name': 'Indianapolis', 'lat': 39.7684, 'lng': -86.1581},
            {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321},
            {'name': 'Denver', 'lat': 39.7392, 'lng': -104.9903},
            {'name': 'Washington', 'lat': 38.9072, 'lng': -77.0369},
            {'name': 'Boston', 'lat': 42.3601, 'lng': -71.0589},
            {'name': 'El Paso', 'lat': 31.7619, 'lng': -106.4850},
            {'name': 'Nashville', 'lat': 36.1627, 'lng': -86.7816},
            {'name': 'Detroit', 'lat': 42.3314, 'lng': -83.0458},
            {'name': 'Oklahoma City', 'lat': 35.4676, 'lng': -97.5164},
            {'name': 'Portland', 'lat': 45.5152, 'lng': -122.6784},
            {'name': 'Las Vegas', 'lat': 36.1699, 'lng': -115.1398},
            {'name': 'Memphis', 'lat': 35.1495, 'lng': -90.0490},
            {'name': 'Louisville', 'lat': 38.2527, 'lng': -85.7585},
            {'name': 'Baltimore', 'lat': 39.2904, 'lng': -76.6122},
            {'name': 'Milwaukee', 'lat': 43.0389, 'lng': -87.9065},
            {'name': 'Albuquerque', 'lat': 35.0844, 'lng': -106.6504},
            {'name': 'Tucson', 'lat': 32.2226, 'lng': -110.9747},
            {'name': 'Fresno', 'lat': 36.7378, 'lng': -119.7871},
            {'name': 'Sacramento', 'lat': 38.5816, 'lng': -121.4944},
            {'name': 'Mesa', 'lat': 33.4152, 'lng': -111.8315},
            {'name': 'Kansas City', 'lat': 39.0997, 'lng': -94.5786},
            {'name': 'Atlanta', 'lat': 33.7490, 'lng': -84.3880},
            {'name': 'Miami', 'lat': 25.7617, 'lng': -80.1918},
            {'name': 'New Orleans', 'lat': 29.9511, 'lng': -90.0715},
            {'name': 'Minneapolis', 'lat': 44.9778, 'lng': -93.2650},
            {'name': 'Cleveland', 'lat': 41.4993, 'lng': -81.6944},
            {'name': 'Tampa', 'lat': 27.9506, 'lng': -82.4572},
            {'name': 'Pittsburgh', 'lat': 40.4406, 'lng': -79.9959},
            {'name': 'Cincinnati', 'lat': 39.1031, 'lng': -84.5120},
            {'name': 'Orlando', 'lat': 28.5383, 'lng': -81.3792},
            {'name': 'St. Louis', 'lat': 38.6270, 'lng': -90.1994},
            {'name': 'Buffalo', 'lat': 42.8864, 'lng': -78.8784},
            {'name': 'Raleigh', 'lat': 35.7796, 'lng': -78.6382},
            {'name': 'Richmond', 'lat': 37.5407, 'lng': -77.4360},
            {'name': 'Birmingham', 'lat': 33.5207, 'lng': -86.8025},
            {'name': 'Salt Lake City', 'lat': 40.7608, 'lng': -111.8910},
            {'name': 'Rochester', 'lat': 43.1566, 'lng': -77.6088},
            {'name': 'Grand Rapids', 'lat': 42.9634, 'lng': -85.6681},
            {'name': 'Tulsa', 'lat': 36.1540, 'lng': -95.9928},
            {'name': 'Honolulu', 'lat': 21.3099, 'lng': -157.8581},
        ]
    
    def _load_package_types(self) -> List[Dict]:
        """Load package types with weight distributions."""
        return [
            {'name': 'Small Package', 'min_weight': 0.1, 'max_weight': 5.0, 'probability': 0.4},
            {'name': 'Medium Package', 'min_weight': 5.0, 'max_weight': 25.0, 'probability': 0.3},
            {'name': 'Large Package', 'min_weight': 25.0, 'max_weight': 100.0, 'probability': 0.2},
            {'name': 'Pallet', 'min_weight': 100.0, 'max_weight': 500.0, 'probability': 0.08},
            {'name': 'Container', 'min_weight': 500.0, 'max_weight': 2000.0, 'probability': 0.02},
        ]
    
    def _load_carriers(self) -> List[str]:
        """Load major carrier companies."""
        return [
            'FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics',
            'XPO Logistics', 'J.B. Hunt', 'C.H. Robinson',
            'Maersk', 'MSC', 'CMA CGM', 'Evergreen',
            'American Airlines Cargo', 'Delta Cargo', 'United Cargo'
        ]
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using geodesic distance."""
        return geodesic((lat1, lng1), (lat2, lng2)).kilometers
    
    def _select_transport_mode(self, distance_km: float, include_seasonal_patterns: bool) -> str:
        """Select transport mode based on distance and seasonal factors."""
        
        # Base probabilities by distance
        if distance_km < 100:
            # Local/regional: mostly ground
            probabilities = {'ground': 0.9, 'air': 0.1, 'sea': 0.0}
        elif distance_km < 500:
            # Regional: ground and air
            probabilities = {'ground': 0.7, 'air': 0.3, 'sea': 0.0}
        elif distance_km < 2000:
            # National: air and ground
            probabilities = {'ground': 0.4, 'air': 0.6, 'sea': 0.0}
        else:
            # International: air and sea
            probabilities = {'ground': 0.1, 'air': 0.6, 'sea': 0.3}
        
        # Apply seasonal adjustments if enabled
        if include_seasonal_patterns:
            current_month = datetime.now().month
            
            # Q4 (Oct-Dec): Higher air freight due to holiday rush
            if current_month in [10, 11, 12]:
                if 'air' in probabilities:
                    probabilities['air'] = min(0.9, probabilities['air'] * 1.3)
                    probabilities['ground'] = max(0.1, probabilities['ground'] * 0.8)
            
            # Winter months (Dec-Feb): More ground transport due to weather
            elif current_month in [12, 1, 2]:
                if 'ground' in probabilities:
                    probabilities['ground'] = min(0.9, probabilities['ground'] * 1.2)
                    probabilities['air'] = max(0.1, probabilities['air'] * 0.9)
        
        # Select transport mode based on probabilities
        modes = list(probabilities.keys())
        probs = list(probabilities.values())
        
        return random.choices(modes, weights=probs)[0]
    
    def _generate_weight(self, transport_mode: str) -> float:
        """Generate realistic weight based on transport mode."""
        
        # Weight distributions by transport mode
        if transport_mode == 'air':
            # Air freight: lighter packages, faster delivery
            mean_weight = 50.0
            std_weight = 30.0
        elif transport_mode == 'ground':
            # Ground freight: medium packages
            mean_weight = 100.0
            std_weight = 60.0
        else:  # sea
            # Sea freight: heavier packages, slower delivery
            mean_weight = 500.0
            std_weight = 300.0
        
        # Generate weight using log-normal distribution
        weight = np.random.lognormal(mean=np.log(mean_weight), sigma=0.5)
        
        # Apply reasonable bounds
        weight = max(0.1, min(2000.0, weight))
        
        return weight
    
    def _generate_timing(
        self,
        start_date: datetime,
        end_date: datetime,
        distance_km: float,
        transport_mode: str,
        include_seasonal_patterns: bool
    ) -> Tuple[datetime, datetime]:
        """Generate departure and arrival times with realistic patterns."""
        
        # Generate departure time within the date range
        time_range = (end_date - start_date).days
        departure_days = random.randint(0, time_range)
        departure_time = start_date + timedelta(days=departure_days)
        
        # Add random time within the day (business hours bias)
        hour = random.choices(
            range(24),
            weights=[0.1] * 6 + [0.3] * 8 + [0.2] * 4 + [0.1] * 6  # Business hours bias
        )[0]
        minute = random.randint(0, 59)
        departure_time = departure_time.replace(hour=hour, minute=minute)
        
        # Calculate travel time based on distance and transport mode
        travel_hours = self._calculate_travel_time(distance_km, transport_mode)
        
        # Add some variability to travel time
        travel_hours *= random.uniform(0.8, 1.2)
        
        arrival_time = departure_time + timedelta(hours=travel_hours)
        
        # Ensure arrival time is within the date range
        if arrival_time > end_date:
            arrival_time = end_date - timedelta(hours=random.randint(1, 6))
        
        return departure_time, arrival_time
    
    def _calculate_travel_time(self, distance_km: float, transport_mode: str) -> float:
        """Calculate travel time based on distance and transport mode."""
        
        if transport_mode == 'air':
            # Air: 800 km/h average speed
            speed_kmh = 800
        elif transport_mode == 'ground':
            # Ground: 60 km/h average speed (including stops)
            speed_kmh = 60
        else:  # sea
            # Sea: 25 km/h average speed
            speed_kmh = 25
        
        travel_hours = distance_km / speed_kmh
        
        # Add minimum travel times
        min_hours = {'air': 2, 'ground': 4, 'sea': 24}
        travel_hours = max(travel_hours, min_hours[transport_mode])
        
        return travel_hours
    
    def _select_package_type(self, weight_kg: float, transport_mode: str) -> str:
        """Select package type based on weight and transport mode."""
        
        # Filter package types based on weight
        suitable_types = [
            pkg for pkg in self.package_types
            if pkg['min_weight'] <= weight_kg <= pkg['max_weight']
        ]
        
        if not suitable_types:
            # If no exact match, find the closest
            suitable_types = self.package_types
        
        # Select based on probability
        types = [pkg['name'] for pkg in suitable_types]
        probs = [pkg['probability'] for pkg in suitable_types]
        
        return random.choices(types, weights=probs)[0]
    
    def generate_seasonal_dataset(
        self,
        year: int,
        include_holiday_patterns: bool = True
    ) -> List[Dict]:
        """
        Generate a full year of shipment data with seasonal patterns.
        
        Args:
            year: Year to generate data for
            include_holiday_patterns: Whether to include holiday-related patterns
            
        Returns:
            List of shipment dictionaries for the entire year
        """
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)
        
        # Calculate shipments per month with seasonal variations
        base_shipments_per_month = 10000  # 10K per month base
        
        all_shipments = []
        
        for month in range(1, 13):
            # Apply seasonal multipliers
            seasonal_multiplier = self._get_seasonal_multiplier(month, include_holiday_patterns)
            shipments_this_month = int(base_shipments_per_month * seasonal_multiplier)
            
            month_start = datetime(year, month, 1)
            if month == 12:
                month_end = datetime(year, month, 31, 23, 59, 59)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
            
            month_shipments = self.generate_shipments(
                shipments_this_month, month_start, month_end, include_seasonal_patterns=True
            )
            
            all_shipments.extend(month_shipments)
            
            logger.info(
                f"Generated {len(month_shipments)} shipments for {month_start.strftime('%B %Y')}",
                seasonal_multiplier=seasonal_multiplier
            )
        
        logger.info(
            "Full year dataset generated",
            total_shipments=len(all_shipments),
            year=year
        )
        
        return all_shipments
    
    def _get_seasonal_multiplier(self, month: int, include_holiday_patterns: bool) -> float:
        """Get seasonal multiplier for shipment volume."""
        
        # Base seasonal pattern (higher in Q4, lower in Q1)
        base_multipliers = {
            1: 0.8, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.1, 6: 1.0,
            7: 0.9, 8: 1.0, 9: 1.1, 10: 1.2, 11: 1.3, 12: 1.4
        }
        
        multiplier = base_multipliers[month]
        
        # Apply holiday patterns if enabled
        if include_holiday_patterns:
            if month == 11:  # November (Black Friday, Cyber Monday)
                multiplier *= 1.5
            elif month == 12:  # December (Holiday season)
                multiplier *= 1.8
            elif month == 1:  # January (post-holiday lull)
                multiplier *= 0.7
            elif month == 7:  # July (summer slowdown)
                multiplier *= 0.8
        
        return multiplier 