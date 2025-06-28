"""
ETL ingestion pipeline for the Supply Chain Carbon Analytics Platform.
Handles data ingestion from generators and external APIs.
"""

from typing import Any, Dict, List
from config.settings import get_settings
from database.connection import get_db_session
import structlog
from uuid import uuid4, UUID
import traceback

logger = structlog.get_logger(__name__)
settings = get_settings()

class DataIngestionPipeline:
    """
    Modular ETL ingestion pipeline for loading shipment and weather data.
    """
    def __init__(self, config: Any = None):
        self.config = config or settings
        # Placeholders for API clients, generators, etc.
        # self.weather_api = WeatherAPI(self.config.api.openweather_api_key)
        # self.shipment_generator = ShipmentGenerator()

    def ingest_daily_shipments(self, shipments: List[Dict]) -> None:
        """
        Ingest a batch of shipment records into the database using batch inserts.
        Args:
            shipments: List of shipment dictionaries
        """
        from database.models import Shipment, CarbonEmission
        
        if not shipments:
            logger.warning("No shipments to ingest")
            print("[DEBUG] No shipments to ingest")
            return
            
        print(f"[DEBUG] Starting ingestion of {len(shipments)} shipments...")
        
        try:
            with get_db_session() as session:
                print("[DEBUG] Database session created successfully")
                
                # Prepare batch data for shipments
                shipment_records = []
                emission_records = []
                
                print("[DEBUG] Preparing shipment records...")
                for i, shipment_data in enumerate(shipments):
                    if i % 1000 == 0:
                        print(f"[DEBUG] Processed {i} shipments...")
                    
                    # Create shipment record
                    shipment = Shipment(
                        shipment_id=UUID(shipment_data['shipment_id']),
                        origin_lat=shipment_data['origin_lat'],
                        origin_lng=shipment_data['origin_lng'],
                        destination_lat=shipment_data['destination_lat'],
                        destination_lng=shipment_data['destination_lng'],
                        transport_mode=shipment_data['transport_mode'],
                        weight_kg=shipment_data['weight_kg'],
                        distance_km=shipment_data['distance_km'],
                        departure_time=shipment_data['departure_time'],
                        arrival_time=shipment_data['arrival_time'],
                        carrier_id=UUID(shipment_data['carrier_id']) if shipment_data['carrier_id'] else None,
                        package_type=shipment_data['package_type'],
                    )
                    shipment_records.append(shipment)
                    
                    # Create carbon emission record if emissions data exists
                    if 'co2_kg' in shipment_data:
                        carbon_emission = CarbonEmission(
                            emission_id=uuid4(),
                            shipment_id=UUID(shipment_data['shipment_id']),
                            co2_kg=shipment_data['co2_kg'],
                            ch4_kg=shipment_data.get('ch4_kg', 0.0),
                            n2o_kg=shipment_data.get('n2o_kg', 0.0),
                            co2_equivalent_kg=shipment_data.get('co2_equivalent_kg', shipment_data['co2_kg']),
                            emission_factor_source=shipment_data.get('emission_factor_source', 'default'),
                            calculation_method=shipment_data.get('calculation_method', 'standard'),
                            weather_impact_factor=shipment_data.get('weather_impact_factor', 1.0),
                        )
                        emission_records.append(carbon_emission)
                
                print(f"[DEBUG] Prepared {len(shipment_records)} shipment records and {len(emission_records)} emission records")
                
                # Batch insert shipments
                if shipment_records:
                    print("[DEBUG] Adding shipments to session...")
                    session.add_all(shipment_records)
                    logger.info("Added shipments to session", count=len(shipment_records))
                    print(f"[DEBUG] Added {len(shipment_records)} shipments to session")
                
                # Batch insert emissions
                if emission_records:
                    print("[DEBUG] Adding emissions to session...")
                    session.add_all(emission_records)
                    logger.info("Added emissions to session", count=len(emission_records))
                    print(f"[DEBUG] Added {len(emission_records)} emissions to session")
                
                # Commit all changes
                print("[DEBUG] Committing to database...")
                session.commit()
                logger.info("Successfully committed all records to database")
                print("[DEBUG] Successfully committed all records to database")
                
        except Exception as e:
            logger.error("Error during data ingestion", error=str(e), error_type=type(e).__name__)
            print(f"❌ Error during data ingestion: {e}")
            print(f"Error type: {type(e).__name__}")
            print("Full traceback:")
            traceback.print_exc()
            # Re-raise to see the full error
            raise
        
        # Print summary at the very end
        emissions_count = sum('co2_kg' in s for s in shipments)
        print(f"[SUMMARY] Ingested {len(shipments)} shipments, {emissions_count} with emissions.")

    def enrich_with_weather(self, shipment_ids: List[str]) -> None:
        """
        Enrich shipments with weather data (stub for future implementation).
        Args:
            shipment_ids: List of shipment UUIDs
        """
        # TODO: Implement weather enrichment logic
        logger.info("Weather enrichment not yet implemented", shipment_ids=shipment_ids) 