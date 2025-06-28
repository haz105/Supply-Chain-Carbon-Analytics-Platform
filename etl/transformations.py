"""
ETL transformation module for the Supply Chain Carbon Analytics Platform.
Handles carbon emission calculation, aggregation, and derived metrics.
"""

from typing import List, Dict, Any
from analytics.carbon_calculator import CarbonCalculator
import structlog

logger = structlog.get_logger(__name__)

class DataTransformationPipeline:
    """
    ETL transformation pipeline for calculating emissions and aggregating data.
    """
    def __init__(self):
        self.carbon_calculator = CarbonCalculator()

    def calculate_emissions_for_shipments(self, shipments: List[Dict]) -> List[Dict]:
        """
        Calculate carbon emissions for each shipment and return enriched records.
        Args:
            shipments: List of shipment dictionaries
        Returns:
            List of shipment records with emission fields
        """
        enriched = []
        for shipment in shipments:
            emissions = self.carbon_calculator.calculate_transport_emissions(
                distance_km=shipment['distance_km'],
                weight_kg=shipment['weight_kg'],
                transport_mode=shipment['transport_mode']
            )
            shipment.update(emissions)
            enriched.append(shipment)
        logger.info("Calculated emissions for shipments", count=len(enriched))
        return enriched

    def aggregate_by_supplier(self, shipments: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate emissions and metrics by supplier.
        Args:
            shipments: List of shipment dictionaries
        Returns:
            Dictionary mapping supplier_id to aggregated metrics
        """
        supplier_agg = {}
        for shipment in shipments:
            supplier_id = shipment.get('supplier_id')
            if not supplier_id:
                continue
            if supplier_id not in supplier_agg:
                supplier_agg[supplier_id] = {
                    'total_co2_kg': 0.0,
                    'total_shipments': 0
                }
            supplier_agg[supplier_id]['total_co2_kg'] += shipment.get('co2_kg', 0.0)
            supplier_agg[supplier_id]['total_shipments'] += 1
        logger.info("Aggregated emissions by supplier", supplier_count=len(supplier_agg))
        return supplier_agg

    def create_derived_metrics(self, shipments: List[Dict]) -> List[Dict]:
        """
        Create derived metrics such as carbon per mile and efficiency scores.
        Args:
            shipments: List of shipment dictionaries
        Returns:
            List of shipment records with derived metrics
        """
        for shipment in shipments:
            if shipment['distance_km'] > 0:
                shipment['carbon_per_mile'] = shipment['co2_kg'] / shipment['distance_km']
            else:
                shipment['carbon_per_mile'] = 0.0
        logger.info("Created derived metrics for shipments", count=len(shipments))
        return shipments 