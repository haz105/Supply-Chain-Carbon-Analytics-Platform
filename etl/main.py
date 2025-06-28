"""
Main ETL pipeline runner for the Supply Chain Carbon Analytics Platform.
Generates, validates, transforms, and ingests synthetic shipment data.
"""

from datetime import datetime, timedelta
from data_generators.shipment_generator import ShipmentGenerator
from etl.data_quality import DataQualityChecker
from etl.transformations import DataTransformationPipeline
from etl.ingestion import DataIngestionPipeline
import structlog
import traceback

logger = structlog.get_logger(__name__)

def run_etl_pipeline(num_shipments: int = 1000):
    """
    Run the full ETL pipeline: generate, validate, transform, ingest, and report.
    Args:
        num_shipments: Number of synthetic shipments to generate
    """
    logger.info("Starting ETL pipeline", num_shipments=num_shipments)

    try:
        # 1. Generate synthetic shipment data
        print(f"[DEBUG] Starting data generation for {num_shipments} shipments...")
        generator = ShipmentGenerator()
        today = datetime.now()
        # Use a past date range to avoid generating future dates
        start_date = today - timedelta(days=30)  # Start 30 days ago
        end_date = today - timedelta(days=1)     # End yesterday
        
        shipments = generator.generate_shipments(
            num_shipments=num_shipments,
            start_date=start_date,
            end_date=end_date,
            include_seasonal_patterns=True
        )
        logger.info("Generated synthetic shipments", count=len(shipments))
        print(f"[DEBUG] Generated {len(shipments)} shipments")

        # 2. Validate data quality
        print("[DEBUG] Starting data quality validation...")
        dq_checker = DataQualityChecker()
        issues = dq_checker.validate_shipments(shipments)
        print(f"[DEBUG] Data quality validation completed, {len(issues)} issues found")

        # 3. Transform: calculate emissions and derived metrics
        print("[DEBUG] Starting emissions calculation...")
        transformer = DataTransformationPipeline()
        shipments = transformer.calculate_emissions_for_shipments(shipments)
        print(f"[DEBUG] After emissions calc: {sum('co2_kg' in s for s in shipments)} shipments have co2_kg")
        
        print("[DEBUG] Starting derived metrics calculation...")
        shipments = transformer.create_derived_metrics(shipments)
        print(f"[DEBUG] Derived metrics completed for {len(shipments)} shipments")

        # 4. Flag anomalies
        print("[DEBUG] Starting anomaly detection...")
        anomalies = dq_checker.flag_anomalous_emissions(shipments)
        print(f"[DEBUG] Anomaly detection completed, {len(anomalies)} anomalies found")

        # 5. Ingest into database
        print("[DEBUG] Starting database ingestion...")
        ingestion = DataIngestionPipeline()
        ingestion.ingest_daily_shipments(shipments)
        print(f"[DEBUG] Database ingestion completed for {len(shipments)} shipments")

        # 6. Print data quality report
        report = dq_checker.generate_data_quality_report(issues, anomalies)
        logger.info("ETL pipeline completed", report=report)
        print("\nData Quality Report:")
        print(report)
        
    except Exception as e:
        print(f"❌ Error in ETL pipeline: {e}")
        print(f"Error type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_etl_pipeline(num_shipments=1000) 