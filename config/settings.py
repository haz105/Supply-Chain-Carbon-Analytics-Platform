"""
Configuration settings for the Supply Chain Carbon Analytics Platform.
Uses Pydantic for type-safe environment variable management.
"""

from typing import Optional
from pydantic import BaseSettings, Field, validator
import os


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(..., env="DATABASE_URL")
    test_url: Optional[str] = Field(None, env="DATABASE_TEST_URL")
    max_connections: int = Field(20, env="MAX_CONNECTIONS")
    connection_timeout: int = Field(30, env="CONNECTION_TIMEOUT")
    query_timeout: int = Field(60, env="QUERY_TIMEOUT")
    
    class Config:
        env_file = ".env"


class AWSSettings(BaseSettings):
    """AWS configuration settings."""
    
    access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    region: str = Field("us-east-1", env="AWS_REGION")
    s3_bucket: str = Field(..., env="AWS_S3_BUCKET")
    timestream_database: str = Field(..., env="AWS_TIMESTREAM_DATABASE")
    timestream_table: str = Field(..., env="AWS_TIMESTREAM_TABLE")
    
    class Config:
        env_file = ".env"


class APISettings(BaseSettings):
    """External API configuration settings."""
    
    openweather_api_key: str = Field(..., env="OPENWEATHER_API_KEY")
    epa_api_key: str = Field(..., env="EPA_API_KEY")
    mapbox_api_key: str = Field(..., env="MAPBOX_API_KEY")
    
    class Config:
        env_file = ".env"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(..., env="SECRET_KEY")
    api_key_header: str = Field("X-API-Key", env="API_KEY_HEADER")
    api_key: str = Field(..., env="API_KEY")
    
    class Config:
        env_file = ".env"


class MLModelSettings(BaseSettings):
    """Machine learning model configuration settings."""
    
    model_path: str = Field("./models/", env="MODEL_PATH")
    model_version: str = Field("v1.0", env="MODEL_VERSION")
    prediction_batch_size: int = Field(1000, env="PREDICTION_BATCH_SIZE")
    
    class Config:
        env_file = ".env"


class DashboardSettings(BaseSettings):
    """Dashboard configuration settings."""
    
    port: int = Field(8050, env="DASHBOARD_PORT")
    host: str = Field("0.0.0.0", env="DASHBOARD_HOST")
    
    class Config:
        env_file = ".env"


class ETLSettings(BaseSettings):
    """ETL pipeline configuration settings."""
    
    batch_size: int = Field(10000, env="ETL_BATCH_SIZE")
    schedule_interval: int = Field(3600, env="ETL_SCHEDULE_INTERVAL")
    data_retention_days: int = Field(365, env="DATA_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"


class MonitoringSettings(BaseSettings):
    """Monitoring and logging configuration settings."""
    
    prometheus_port: int = Field(9090, env="PROMETHEUS_PORT")
    health_check_interval: int = Field(30, env="HEALTH_CHECK_INTERVAL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"


class AppSettings(BaseSettings):
    """Main application configuration settings."""
    
    name: str = Field("Supply Chain Carbon Analytics", env="APP_NAME")
    version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    aws: AWSSettings = AWSSettings()
    api: APISettings = APISettings()
    security: SecuritySettings = SecuritySettings()
    ml_model: MLModelSettings = MLModelSettings()
    dashboard: DashboardSettings = DashboardSettings()
    etl: ETLSettings = ETLSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    @validator("debug", pre=True)
    def parse_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = AppSettings()


def get_settings() -> AppSettings:
    """Get the application settings instance."""
    return settings 