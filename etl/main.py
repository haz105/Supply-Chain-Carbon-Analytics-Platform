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

logger = structlog.get_logger(__name__)

def run_etl_pipeline(num_shipments: int = 1000):
    """
    Run the full ETL pipeline: generate, validate, transform, ingest, and report.
    Args:
        num_shipments: Number of synthetic shipments to generate
    """
    logger.info("Starting ETL pipeline", num_shipments=num_shipments)

    # 1. Generate synthetic shipment data
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

    # 2. Validate data quality
    dq_checker = DataQualityChecker()
    issues = dq_checker.validate_shipments(shipments)

    # 3. Transform: calculate emissions and derived metrics
    transformer = DataTransformationPipeline()
    shipments = transformer.calculate_emissions_for_shipments(shipments)
    shipments = transformer.create_derived_metrics(shipments)

    # 4. Flag anomalies
    anomalies = dq_checker.flag_anomalous_emissions(shipments)

    # 5. Ingest into database
    ingestion = DataIngestionPipeline()
    ingestion.ingest_daily_shipments(shipments)

    # 6. Print data quality report
    report = dq_checker.generate_data_quality_report(issues, anomalies)
    logger.info("ETL pipeline completed", report=report)
    print("\nData Quality Report:")
    print(report)

if __name__ == "__main__":
    run_etl_pipeline(num_shipments=1000) 