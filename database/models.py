"""
SQLAlchemy database models for the Supply Chain Carbon Analytics Platform.
Defines the core entities and their relationships.
"""

from datetime import datetime, date
from typing import Optional, List
from uuid import uuid4
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Date, Boolean, 
    ForeignKey, Text, Index, CheckConstraint, UniqueConstraint, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class Shipment(Base):
    """Shipment entity representing transportation data."""
    
    __tablename__ = "shipments"
    
    # Primary key
    shipment_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    
    # Location data
    origin_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    origin_lng: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    destination_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    destination_lng: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    
    # Transportation details
    transport_mode: Mapped[str] = mapped_column(String(50), nullable=False)  # air, ground, sea
    weight_kg: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    distance_km: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    package_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Timing
    departure_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    carrier_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), nullable=True)
    supplier_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("suppliers.supplier_id"), 
        nullable=True
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    carbon_emissions: Mapped[List["CarbonEmission"]] = relationship("CarbonEmission", back_populates="shipment")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="shipments")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("weight_kg > 0", name="positive_weight"),
        CheckConstraint("distance_km > 0", name="positive_distance"),
        CheckConstraint("transport_mode IN ('air', 'ground', 'sea')", name="valid_transport_mode"),
        Index("idx_shipments_dates", "departure_time", "arrival_time"),
        Index("idx_shipments_mode", "transport_mode"),
        Index("idx_shipments_supplier", "supplier_id"),
    )


class CarbonEmission(Base):
    """Carbon emission calculations for shipments."""
    
    __tablename__ = "carbon_emissions"
    
    # Primary key
    emission_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    
    # Foreign key
    shipment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("shipments.shipment_id"), 
        nullable=False
    )
    
    # Emission values (kg)
    co2_kg: Mapped[float] = mapped_column(DECIMAL(10, 6), nullable=False)
    ch4_kg: Mapped[float] = mapped_column(DECIMAL(10, 6), nullable=False, default=0)
    n2o_kg: Mapped[float] = mapped_column(DECIMAL(10, 6), nullable=False, default=0)
    co2_equivalent_kg: Mapped[float] = mapped_column(DECIMAL(10, 6), nullable=False)
    
    # Calculation metadata
    emission_factor_source: Mapped[str] = mapped_column(String(100), nullable=False)
    calculation_method: Mapped[str] = mapped_column(String(100), nullable=False)
    weather_impact_factor: Mapped[float] = mapped_column(DECIMAL(5, 4), nullable=False, default=1.0)
    
    # Metadata
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    shipment: Mapped["Shipment"] = relationship("Shipment", back_populates="carbon_emissions")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("co2_kg >= 0", name="positive_co2"),
        CheckConstraint("co2_equivalent_kg >= 0", name="positive_co2e"),
        CheckConstraint("weather_impact_factor > 0", name="positive_weather_factor"),
        Index("idx_emissions_shipment", "shipment_id"),
        Index("idx_emissions_calculated", "calculated_at"),
    )


class Supplier(Base):
    """Supplier entity with sustainability information."""
    
    __tablename__ = "suppliers"
    
    # Primary key
    supplier_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    location_lng: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    
    # Sustainability metrics
    sustainability_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-100
    renewable_energy_percent: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False, default=0)
    carbon_intensity_kg_per_dollar: Mapped[float] = mapped_column(DECIMAL(10, 6), nullable=False, default=0)
    certification_level: Mapped[str] = mapped_column(String(50), nullable=False, default="None")  # None, Bronze, Silver, Gold
    
    # Audit information
    last_audit_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    audit_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-100
    
    # Additional ESG metrics
    waste_reduction_percent: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False, default=0)
    water_efficiency_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 1-100
    social_responsibility_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # 1-100
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    shipments: Mapped[List["Shipment"]] = relationship("Shipment", back_populates="supplier")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("sustainability_score BETWEEN 1 AND 100", name="valid_sustainability_score"),
        CheckConstraint("renewable_energy_percent BETWEEN 0 AND 100", name="valid_renewable_energy"),
        CheckConstraint("carbon_intensity_kg_per_dollar >= 0", name="positive_carbon_intensity"),
        CheckConstraint("certification_level IN ('None', 'Bronze', 'Silver', 'Gold')", name="valid_certification"),
        CheckConstraint("waste_reduction_percent BETWEEN 0 AND 100", name="valid_waste_reduction"),
        CheckConstraint("water_efficiency_score BETWEEN 1 AND 100", name="valid_water_score"),
        CheckConstraint("social_responsibility_score BETWEEN 1 AND 100", name="valid_social_score"),
        UniqueConstraint("name", name="unique_supplier_name"),
        Index("idx_suppliers_location", "location_lat", "location_lng"),
        Index("idx_suppliers_sustainability", "sustainability_score"),
    )


class WeatherData(Base):
    """Weather data affecting transportation efficiency."""
    
    __tablename__ = "weather_data"
    
    # Primary key
    weather_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    
    # Location and time
    location_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    location_lng: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Weather conditions
    temperature_celsius: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    humidity_percent: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    wind_speed_kmh: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    wind_direction_degrees: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    precipitation_mm: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False, default=0)
    
    # Impact factors
    fuel_efficiency_impact: Mapped[float] = mapped_column(DECIMAL(5, 4), nullable=False, default=1.0)
    route_delay_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Metadata
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="OpenWeatherMap")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("humidity_percent BETWEEN 0 AND 100", name="valid_humidity"),
        CheckConstraint("wind_speed_kmh >= 0", name="positive_wind_speed"),
        CheckConstraint("wind_direction_degrees BETWEEN 0 AND 360", name="valid_wind_direction"),
        CheckConstraint("precipitation_mm >= 0", name="positive_precipitation"),
        CheckConstraint("fuel_efficiency_impact > 0", name="positive_efficiency_impact"),
        Index("idx_weather_location_time", "location_lat", "location_lng", "recorded_at"),
    )


class RouteOptimization(Base):
    """Route optimization results and recommendations."""
    
    __tablename__ = "route_optimizations"
    
    # Primary key
    optimization_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    
    # Route details
    origin_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    origin_lng: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    destination_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    destination_lng: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    
    # Optimization parameters
    weight_kg: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)  # cost, carbon, balanced
    constraints: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of constraints
    
    # Results
    optimal_route: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of route waypoints
    total_distance_km: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    estimated_carbon_kg: Mapped[float] = mapped_column(DECIMAL(10, 6), nullable=False)
    estimated_duration_hours: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    
    # Alternative routes
    alternative_routes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of alternatives
    
    # Metadata
    algorithm_used: Mapped[str] = mapped_column(String(100), nullable=False)
    optimization_time_seconds: Mapped[float] = mapped_column(DECIMAL(8, 3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("weight_kg > 0", name="positive_weight"),
        CheckConstraint("priority IN ('cost', 'carbon', 'balanced')", name="valid_priority"),
        CheckConstraint("total_distance_km > 0", name="positive_distance"),
        CheckConstraint("estimated_cost_usd >= 0", name="positive_cost"),
        CheckConstraint("estimated_carbon_kg >= 0", name="positive_carbon"),
        CheckConstraint("estimated_duration_hours > 0", name="positive_duration"),
        Index("idx_optimization_route", "origin_lat", "origin_lng", "destination_lat", "destination_lng"),
        Index("idx_optimization_priority", "priority"),
    )


class ScenarioAnalysis(Base):
    """Scenario analysis results for sustainability planning."""
    
    __tablename__ = "scenario_analyses"
    
    # Primary key
    scenario_id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    
    # Scenario details
    scenario_name: Mapped[str] = mapped_column(String(255), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(100), nullable=False)  # carbon_reduction, cost_optimization, etc.
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Parameters
    parameters: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string of scenario parameters
    time_horizon_months: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Results
    baseline_carbon_kg: Mapped[float] = mapped_column(DECIMAL(15, 6), nullable=False)
    scenario_carbon_kg: Mapped[float] = mapped_column(DECIMAL(15, 6), nullable=False)
    carbon_reduction_percent: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    
    baseline_cost_usd: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    scenario_cost_usd: Mapped[float] = mapped_column(DECIMAL(15, 2), nullable=False)
    cost_impact_percent: Mapped[float] = mapped_column(DECIMAL(8, 2), nullable=False)
    
    # Additional metrics
    roi_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(8, 2), nullable=True)
    payback_period_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("time_horizon_months > 0", name="positive_time_horizon"),
        CheckConstraint("baseline_carbon_kg >= 0", name="positive_baseline_carbon"),
        CheckConstraint("scenario_carbon_kg >= 0", name="positive_scenario_carbon"),
        CheckConstraint("carbon_reduction_percent BETWEEN -100 AND 100", name="valid_carbon_reduction"),
        CheckConstraint("baseline_cost_usd >= 0", name="positive_baseline_cost"),
        CheckConstraint("scenario_cost_usd >= 0", name="positive_scenario_cost"),
        Index("idx_scenario_type", "scenario_type"),
        Index("idx_scenario_created", "created_at"),
    ) 