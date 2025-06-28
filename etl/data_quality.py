"""
ETL data quality module for the Supply Chain Carbon Analytics Platform.
Implements automated validation rules and anomaly detection.
"""

from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)

class DataQualityChecker:
    """
    Data quality checker for validating and flagging shipment data issues.
    """
    def __init__(self):
        self.issues = []

    def validate_shipments(self, shipments: List[Dict]) -> List[Dict]:
        """
        Validate shipment records for missing or invalid data.
        Args:
            shipments: List of shipment dictionaries
        Returns:
            List of issues found (as dictionaries)
        """
        issues = []
        for shipment in shipments:
            if shipment['origin_lat'] is None or shipment['origin_lng'] is None:
                issues.append({'shipment_id': shipment['shipment_id'], 'issue': 'Missing origin coordinates'})
            if shipment['destination_lat'] is None or shipment['destination_lng'] is None:
                issues.append({'shipment_id': shipment['shipment_id'], 'issue': 'Missing destination coordinates'})
            if shipment['weight_kg'] <= 0:
                issues.append({'shipment_id': shipment['shipment_id'], 'issue': 'Non-positive weight'})
            if shipment['distance_km'] <= 0:
                issues.append({'shipment_id': shipment['shipment_id'], 'issue': 'Non-positive distance'})
            if shipment['departure_time'] > shipment['arrival_time']:
                issues.append({'shipment_id': shipment['shipment_id'], 'issue': 'Departure after arrival'})
            if shipment['departure_time'] > shipment['created_at']:
                issues.append({'shipment_id': shipment['shipment_id'], 'issue': 'Departure in the future'})
        logger.info("Validated shipments for data quality", issues_found=len(issues))
        return issues

    def flag_anomalous_emissions(self, shipments: List[Dict], threshold: float = 3.0) -> List[Dict]:
        """
        Flag shipments with anomalous emission calculations (z-score based).
        Args:
            shipments: List of shipment dictionaries
            threshold: Z-score threshold for anomaly
        Returns:
            List of flagged anomalies
        """
        import numpy as np
        co2_values = [s['co2_kg'] for s in shipments if 'co2_kg' in s]
        if not co2_values:
            return []
        mean = np.mean(co2_values)
        std = np.std(co2_values)
        anomalies = []
        for shipment in shipments:
            co2 = shipment.get('co2_kg')
            if co2 is None or std == 0:
                continue
            z = abs((co2 - mean) / std)
            if z > threshold:
                anomalies.append({'shipment_id': shipment['shipment_id'], 'z_score': z, 'co2_kg': co2})
        logger.info("Flagged anomalous emissions", anomaly_count=len(anomalies))
        return anomalies

    def generate_data_quality_report(self, issues: List[Dict], anomalies: List[Dict]) -> Dict[str, Any]:
        """
        Generate a summary data quality report.
        Args:
            issues: List of data quality issues
            anomalies: List of flagged anomalies
        Returns:
            Dictionary report
        """
        report = {
            'total_issues': len(issues),
            'total_anomalies': len(anomalies),
            'issues': issues,
            'anomalies': anomalies
        }
        logger.info("Generated data quality report", total_issues=len(issues), total_anomalies=len(anomalies))
        return report 