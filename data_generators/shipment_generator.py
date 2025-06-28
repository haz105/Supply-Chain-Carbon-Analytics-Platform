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
        
        # First, determine the desired distance range for this shipment
        distance_category = self._select_distance_category()
        
        # Select origin and destination cities based on distance category
        origin_city, destination_city = self._select_cities_by_distance(distance_category)

        # Calculate distance
        distance_km = self._calculate_distance(
            origin_city['lat'], origin_city['lng'],
            destination_city['lat'], destination_city['lng']
        )

        # Determine transport mode based on distance and seasonal factors
        transport_mode = self._select_transport_mode(distance_km, include_seasonal_patterns)

        # Select package type first using probabilities
        package_type = self._select_package_type()
        # Generate weight within the selected package type's range
        weight_kg = self._generate_weight(package_type)

        # Generate timing with seasonal patterns
        departure_time, arrival_time = self._generate_timing(
            start_date, end_date, distance_km, transport_mode, include_seasonal_patterns
        )

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
            'package_type': package_type['name'],
            'departure_time': departure_time,
            'arrival_time': arrival_time,
            'carrier_id': str(uuid.uuid4()),
            'created_at': datetime.now()
        }
        return shipment
    
    def _select_distance_category(self) -> str:
        """Select a distance category to create balanced transport mode distribution."""
        # Define distance categories with probabilities to achieve realistic transport mode distribution
        categories = [
            ('local', 0.25),      # 0-100 km: mostly ground
            ('regional', 0.35),   # 100-500 km: ground and air
            ('national', 0.25),   # 500-2000 km: air and ground
            ('international', 0.15)  # 2000+ km: air and sea
        ]
        
        category_names = [cat[0] for cat in categories]
        probabilities = [cat[1] for cat in categories]
        
        return random.choices(category_names, weights=probabilities)[0]
    
    def _select_cities_by_distance(self, distance_category: str) -> Tuple[Dict, Dict]:
        """Select origin and destination cities based on distance category."""
        
        if distance_category == 'local':
            # Local: Same region, nearby cities
            region = random.choice(['north_america', 'europe', 'asia'])
            region_cities = [city for city in self.major_cities if city['region'] == region]
            
            if len(region_cities) >= 2:
                origin_city = random.choice(region_cities)
                destination_city = random.choice(region_cities)
                while destination_city['name'] == origin_city['name']:
                    destination_city = random.choice(region_cities)
            else:
                # Fallback to any cities if region doesn't have enough
                origin_city = random.choice(self.major_cities)
                destination_city = random.choice(self.major_cities)
                while destination_city['name'] == origin_city['name']:
                    destination_city = random.choice(self.major_cities)
        
        elif distance_category == 'regional':
            # Regional: Same continent, different regions
            continent = random.choice(['north_america', 'europe', 'asia'])
            continent_cities = [city for city in self.major_cities if city['region'] == continent]
            
            if len(continent_cities) >= 2:
                origin_city = random.choice(continent_cities)
                destination_city = random.choice(continent_cities)
                while destination_city['name'] == origin_city['name']:
                    destination_city = random.choice(continent_cities)
            else:
                # Fallback
                origin_city = random.choice(self.major_cities)
                destination_city = random.choice(self.major_cities)
                while destination_city['name'] == origin_city['name']:
                    destination_city = random.choice(self.major_cities)
        
        elif distance_category == 'national':
            # National: Same continent, could be same or different regions
            continent = random.choice(['north_america', 'europe', 'asia'])
            continent_cities = [city for city in self.major_cities if city['region'] == continent]
            
            if len(continent_cities) >= 2:
                origin_city = random.choice(continent_cities)
                destination_city = random.choice(continent_cities)
                while destination_city['name'] == origin_city['name']:
                    destination_city = random.choice(continent_cities)
            else:
                # Fallback
                origin_city = random.choice(self.major_cities)
                destination_city = random.choice(self.major_cities)
                while destination_city['name'] == origin_city['name']:
                    destination_city = random.choice(self.major_cities)
        
        else:  # international
            # International: Different continents
            origin_city = random.choice(self.major_cities)
            destination_city = random.choice(self.major_cities)
            while (destination_city['name'] == origin_city['name'] or 
                   destination_city['region'] == origin_city['region']):
                destination_city = random.choice(self.major_cities)
        
        return origin_city, destination_city
    
    def _load_major_cities(self) -> List[Dict]:
        """Load major world cities/ports with coordinates (global realism)."""
        return [
            # North America - Major Cities
            {'name': 'New York', 'lat': 40.7128, 'lng': -74.0060, 'region': 'north_america'},
            {'name': 'Los Angeles', 'lat': 34.0522, 'lng': -118.2437, 'region': 'north_america'},
            {'name': 'Chicago', 'lat': 41.8781, 'lng': -87.6298, 'region': 'north_america'},
            {'name': 'Houston', 'lat': 29.7604, 'lng': -95.3698, 'region': 'north_america'},
            {'name': 'Toronto', 'lat': 43.651070, 'lng': -79.347015, 'region': 'north_america'},
            {'name': 'Mexico City', 'lat': 19.4326, 'lng': -99.1332, 'region': 'north_america'},
            {'name': 'Vancouver', 'lat': 49.2827, 'lng': -123.1207, 'region': 'north_america'},
            {'name': 'Panama City', 'lat': 8.9824, 'lng': -79.5199, 'region': 'north_america'},
            
            # North America - Regional Cities (for shorter distances)
            {'name': 'Boston', 'lat': 42.3601, 'lng': -71.0589, 'region': 'north_america'},
            {'name': 'Philadelphia', 'lat': 39.9526, 'lng': -75.1652, 'region': 'north_america'},
            {'name': 'Miami', 'lat': 25.7617, 'lng': -80.1918, 'region': 'north_america'},
            {'name': 'Atlanta', 'lat': 33.7490, 'lng': -84.3880, 'region': 'north_america'},
            {'name': 'Dallas', 'lat': 32.7767, 'lng': -96.7970, 'region': 'north_america'},
            {'name': 'Phoenix', 'lat': 33.4484, 'lng': -112.0740, 'region': 'north_america'},
            {'name': 'Seattle', 'lat': 47.6062, 'lng': -122.3321, 'region': 'north_america'},
            {'name': 'Denver', 'lat': 39.7392, 'lng': -104.9903, 'region': 'north_america'},
            {'name': 'Montreal', 'lat': 45.5017, 'lng': -73.5673, 'region': 'north_america'},
            {'name': 'Calgary', 'lat': 51.0447, 'lng': -114.0719, 'region': 'north_america'},
            
            # South America
            {'name': 'São Paulo', 'lat': -23.5505, 'lng': -46.6333, 'region': 'south_america'},
            {'name': 'Buenos Aires', 'lat': -34.6037, 'lng': -58.3816, 'region': 'south_america'},
            {'name': 'Lima', 'lat': -12.0464, 'lng': -77.0428, 'region': 'south_america'},
            {'name': 'Santiago', 'lat': -33.4489, 'lng': -70.6693, 'region': 'south_america'},
            {'name': 'Bogotá', 'lat': 4.7110, 'lng': -74.0721, 'region': 'south_america'},
            {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lng': -43.1729, 'region': 'south_america'},
            {'name': 'Caracas', 'lat': 10.4806, 'lng': -66.9036, 'region': 'south_america'},
            
            # Europe - Major Cities
            {'name': 'London', 'lat': 51.5074, 'lng': -0.1278, 'region': 'europe'},
            {'name': 'Rotterdam', 'lat': 51.9225, 'lng': 4.47917, 'region': 'europe'},
            {'name': 'Hamburg', 'lat': 53.5511, 'lng': 9.9937, 'region': 'europe'},
            {'name': 'Antwerp', 'lat': 51.2194, 'lng': 4.4025, 'region': 'europe'},
            {'name': 'Paris', 'lat': 48.8566, 'lng': 2.3522, 'region': 'europe'},
            {'name': 'Madrid', 'lat': 40.4168, 'lng': -3.7038, 'region': 'europe'},
            {'name': 'Moscow', 'lat': 55.7558, 'lng': 37.6173, 'region': 'europe'},
            
            # Europe - Regional Cities
            {'name': 'Berlin', 'lat': 52.5200, 'lng': 13.4050, 'region': 'europe'},
            {'name': 'Rome', 'lat': 41.9028, 'lng': 12.4964, 'region': 'europe'},
            {'name': 'Amsterdam', 'lat': 52.3676, 'lng': 4.9041, 'region': 'europe'},
            {'name': 'Barcelona', 'lat': 41.3851, 'lng': 2.1734, 'region': 'europe'},
            {'name': 'Milan', 'lat': 45.4642, 'lng': 9.1900, 'region': 'europe'},
            {'name': 'Frankfurt', 'lat': 50.1109, 'lng': 8.6821, 'region': 'europe'},
            {'name': 'Brussels', 'lat': 50.8503, 'lng': 4.3517, 'region': 'europe'},
            {'name': 'Vienna', 'lat': 48.2082, 'lng': 16.3738, 'region': 'europe'},
            
            # Africa
            {'name': 'Lagos', 'lat': 6.5244, 'lng': 3.3792, 'region': 'africa'},
            {'name': 'Cape Town', 'lat': -33.9249, 'lng': 18.4241, 'region': 'africa'},
            {'name': 'Durban', 'lat': -29.8587, 'lng': 31.0218, 'region': 'africa'},
            {'name': 'Cairo', 'lat': 30.0444, 'lng': 31.2357, 'region': 'africa'},
            {'name': 'Nairobi', 'lat': -1.2921, 'lng': 36.8219, 'region': 'africa'},
            {'name': 'Johannesburg', 'lat': -26.2041, 'lng': 28.0473, 'region': 'africa'},
            {'name': 'Casablanca', 'lat': 33.5731, 'lng': -7.5898, 'region': 'africa'},
            
            # Asia - Major Cities
            {'name': 'Shanghai', 'lat': 31.2304, 'lng': 121.4737, 'region': 'asia'},
            {'name': 'Singapore', 'lat': 1.3521, 'lng': 103.8198, 'region': 'asia'},
            {'name': 'Hong Kong', 'lat': 22.3193, 'lng': 114.1694, 'region': 'asia'},
            {'name': 'Tokyo', 'lat': 35.6895, 'lng': 139.6917, 'region': 'asia'},
            {'name': 'Mumbai', 'lat': 19.0760, 'lng': 72.8777, 'region': 'asia'},
            {'name': 'Dubai', 'lat': 25.2048, 'lng': 55.2708, 'region': 'asia'},
            {'name': 'Busan', 'lat': 35.1796, 'lng': 129.0756, 'region': 'asia'},
            
            # Asia - Regional Cities
            {'name': 'Beijing', 'lat': 39.9042, 'lng': 116.4074, 'region': 'asia'},
            {'name': 'Seoul', 'lat': 37.5665, 'lng': 126.9780, 'region': 'asia'},
            {'name': 'Bangkok', 'lat': 13.7563, 'lng': 100.5018, 'region': 'asia'},
            {'name': 'Manila', 'lat': 14.5995, 'lng': 120.9842, 'region': 'asia'},
            {'name': 'Jakarta', 'lat': -6.2088, 'lng': 106.8456, 'region': 'asia'},
            {'name': 'Kuala Lumpur', 'lat': 3.1390, 'lng': 101.6869, 'region': 'asia'},
            {'name': 'Ho Chi Minh City', 'lat': 10.8231, 'lng': 106.6297, 'region': 'asia'},
            {'name': 'Chennai', 'lat': 13.0827, 'lng': 80.2707, 'region': 'asia'},
            {'name': 'Kolkata', 'lat': 22.5726, 'lng': 88.3639, 'region': 'asia'},
            
            # Oceania
            {'name': 'Sydney', 'lat': -33.8688, 'lng': 151.2093, 'region': 'oceania'},
            {'name': 'Melbourne', 'lat': -37.8136, 'lng': 144.9631, 'region': 'oceania'},
            {'name': 'Auckland', 'lat': -36.8485, 'lng': 174.7633, 'region': 'oceania'},
            {'name': 'Brisbane', 'lat': -27.4698, 'lng': 153.0251, 'region': 'oceania'},
            {'name': 'Perth', 'lat': -31.9505, 'lng': 115.8605, 'region': 'oceania'},
            
            # Middle East
            {'name': 'Jeddah', 'lat': 21.4858, 'lng': 39.1925, 'region': 'middle_east'},
            {'name': 'Istanbul', 'lat': 41.0082, 'lng': 28.9784, 'region': 'middle_east'},
            {'name': 'Tehran', 'lat': 35.6892, 'lng': 51.3890, 'region': 'middle_east'},
            {'name': 'Riyadh', 'lat': 24.7136, 'lng': 46.6753, 'region': 'middle_east'},
        ]
    
    def _load_package_types(self) -> List[Dict]:
        """Load package types with weight distributions."""
        return [
            {'name': 'Small Package', 'min_weight': 0.1, 'max_weight': 5.0, 'probability': 0.5},
            {'name': 'Medium Package', 'min_weight': 5.0, 'max_weight': 25.0, 'probability': 0.25},
            {'name': 'Large Package', 'min_weight': 25.0, 'max_weight': 100.0, 'probability': 0.15},
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
    
    def _select_package_type(self) -> Dict:
        """Randomly select a package type based on defined probabilities."""
        types = self.package_types
        names = [t['name'] for t in types]
        probs = [t['probability'] for t in types]
        selected_name = random.choices(names, weights=probs, k=1)[0]
        return next(t for t in types if t['name'] == selected_name)
    
    def _generate_weight(self, package_type: Dict) -> float:
        """Generate a weight within the selected package type's range."""
        return random.uniform(package_type['min_weight'], package_type['max_weight'])
    
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