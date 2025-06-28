"""
Configuration settings for the Supply Chain Carbon Analytics Platform.
Uses Pydantic v2 for type-safe environment variable management.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(..., validation_alias="DATABASE_URL")
    test_url: Optional[str] = Field(None, validation_alias="DATABASE_TEST_URL")
    max_connections: int = Field(20, validation_alias="MAX_CONNECTIONS")
    connection_timeout: int = Field(30, validation_alias="CONNECTION_TIMEOUT")
    query_timeout: int = Field(60, validation_alias="QUERY_TIMEOUT")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class AWSSettings(BaseSettings):
    """AWS configuration settings."""
    
    access_key_id: str = Field(..., validation_alias="AWS_ACCESS_KEY_ID")
    secret_access_key: str = Field(..., validation_alias="AWS_SECRET_ACCESS_KEY")
    region: str = Field("us-east-1", validation_alias="AWS_REGION")
    s3_bucket: str = Field(..., validation_alias="AWS_S3_BUCKET")
    timestream_database: str = Field(..., validation_alias="AWS_TIMESTREAM_DATABASE")
    timestream_table: str = Field(..., validation_alias="AWS_TIMESTREAM_TABLE")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class APISettings(BaseSettings):
    """External API configuration settings."""
    
    openweather_api_key: str = Field(..., validation_alias="OPENWEATHER_API_KEY")
    epa_api_key: str = Field(..., validation_alias="EPA_API_KEY")
    mapbox_api_key: str = Field(..., validation_alias="MAPBOX_API_KEY")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(..., validation_alias="SECRET_KEY")
    api_key_header: str = Field("X-API-Key", validation_alias="API_KEY_HEADER")
    api_key: str = Field(..., validation_alias="API_KEY")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class MLModelSettings(BaseSettings):
    """Machine learning model configuration settings."""
    
    model_path: str = Field("./models/", validation_alias="MODEL_PATH")
    model_version: str = Field("v1.0", validation_alias="MODEL_VERSION")
    prediction_batch_size: int = Field(1000, validation_alias="PREDICTION_BATCH_SIZE")
    
    model_config = {"protected_namespaces": ("settings_",), "extra": "ignore", "env_file": ".env"}


class DashboardSettings(BaseSettings):
    """Dashboard configuration settings."""
    
    port: int = Field(8050, validation_alias="DASHBOARD_PORT")
    host: str = Field("0.0.0.0", validation_alias="DASHBOARD_HOST")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class ETLSettings(BaseSettings):
    """ETL pipeline configuration settings."""
    
    batch_size: int = Field(10000, validation_alias="ETL_BATCH_SIZE")
    schedule_interval: int = Field(3600, validation_alias="ETL_SCHEDULE_INTERVAL")
    data_retention_days: int = Field(365, validation_alias="DATA_RETENTION_DAYS")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration settings."""
    
    prometheus_port: int = Field(9090, validation_alias="PROMETHEUS_PORT")
    health_check_interval: int = Field(30, validation_alias="HEALTH_CHECK_INTERVAL")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    
    model_config = {"extra": "ignore", "env_file": ".env"}


class AppSettings(BaseSettings):
    """Main application configuration settings."""
    
    name: str = Field("Supply Chain Carbon Analytics", validation_alias="APP_NAME")
    version: str = Field("1.0.0", validation_alias="APP_VERSION")
    debug: bool = Field(False, validation_alias="DEBUG")
    
    # Sub-settings
    database: DatabaseSettings = Field(default_factory=lambda: DatabaseSettings())
    aws: AWSSettings = Field(default_factory=lambda: AWSSettings())
    api: APISettings = Field(default_factory=lambda: APISettings())
    security: SecuritySettings = Field(default_factory=lambda: SecuritySettings())
    ml_model: MLModelSettings = Field(default_factory=lambda: MLModelSettings())
    dashboard: DashboardSettings = Field(default_factory=lambda: DashboardSettings())
    etl: ETLSettings = Field(default_factory=lambda: ETLSettings())
    monitoring: MonitoringSettings = Field(default_factory=lambda: MonitoringSettings())
    
    @validator("debug", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    model_config = {"extra": "ignore", "env_file": ".env"}


@lru_cache()
def get_settings() -> AppSettings:
    """Get the application settings instance."""
    return AppSettings() 