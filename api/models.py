"""
Pydantic models for API request/response validation.
Defines schemas for emissions data, route optimization, and supplier information.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from uuid import UUID


class ShipmentBase(BaseModel):
    """Base shipment model."""
    origin_lat: float = Field(..., ge=-90, le=90, description="Origin latitude")
    origin_lng: float = Field(..., ge=-180, le=180, description="Origin longitude")
    destination_lat: float = Field(..., ge=-90, le=90, description="Destination latitude")
    destination_lng: float = Field(..., ge=-180, le=180, description="Destination longitude")
    transport_mode: str = Field(..., pattern="^(air|ground|sea)$", description="Transport mode")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    package_type: str = Field(..., description="Package type")


class ShipmentCreate(ShipmentBase):
    """Model for creating a new shipment."""
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    carrier_id: Optional[str] = Field(None, description="Carrier ID")
    supplier_id: Optional[str] = Field(None, description="Supplier ID")


class ShipmentResponse(ShipmentBase):
    """Model for shipment response."""
    shipment_id: str = Field(..., description="Shipment ID")
    distance_km: float = Field(..., description="Distance in kilometers")
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    carrier_id: Optional[str] = Field(None, description="Carrier ID")
    supplier_id: Optional[str] = Field(None, description="Supplier ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class CarbonEmissionResponse(BaseModel):
    """Model for carbon emission response."""
    emission_id: str = Field(..., description="Emission ID")
    shipment_id: str = Field(..., description="Shipment ID")
    co2_kg: float = Field(..., description="CO2 emissions in kg")
    ch4_kg: float = Field(..., description="CH4 emissions in kg")
    n2o_kg: float = Field(..., description="N2O emissions in kg")
    co2_equivalent_kg: float = Field(..., description="CO2 equivalent in kg")
    emission_factor_source: str = Field(..., description="Emission factor source")
    calculation_method: str = Field(..., description="Calculation method")
    weather_impact_factor: float = Field(..., description="Weather impact factor")
    calculated_at: datetime = Field(..., description="Calculation timestamp")
    
    class Config:
        from_attributes = True


class EmissionsSummaryRequest(BaseModel):
    """Model for emissions summary request."""
    start_date: date = Field(..., description="Start date for summary")
    end_date: date = Field(..., description="End date for summary")
    transport_mode: Optional[str] = Field(None, pattern="^(air|ground|sea)$", description="Filter by transport mode")
    supplier_id: Optional[str] = Field(None, description="Filter by supplier ID")


class EmissionsSummaryResponse(BaseModel):
    """Model for emissions summary response."""
    total_co2_kg: float = Field(..., description="Total CO2 emissions")
    total_co2_equivalent_kg: float = Field(..., description="Total CO2 equivalent emissions")
    shipment_count: int = Field(..., description="Number of shipments")
    average_co2_per_shipment: float = Field(..., description="Average CO2 per shipment")
    transport_mode_breakdown: Dict[str, float] = Field(..., description="Emissions by transport mode")
    date_range: str = Field(..., description="Date range of summary")


class RouteOptimizationRequest(BaseModel):
    """Model for route optimization request."""
    origin_lat: float = Field(..., ge=-90, le=90, description="Origin latitude")
    origin_lng: float = Field(..., ge=-180, le=180, description="Origin longitude")
    destination_lat: float = Field(..., ge=-90, le=90, description="Destination latitude")
    destination_lng: float = Field(..., ge=-180, le=180, description="Destination longitude")
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    priority: str = Field(..., pattern="^(cost|carbon|balanced)$", description="Optimization priority")
    constraints: Optional[Dict[str, Any]] = Field(None, description="Additional constraints")


class RouteOptimizationResponse(BaseModel):
    """Model for route optimization response."""
    optimization_id: str = Field(..., description="Optimization ID")
    optimal_route: List[Dict[str, float]] = Field(..., description="Route waypoints")
    total_distance_km: float = Field(..., description="Total distance")
    estimated_cost_usd: float = Field(..., description="Estimated cost")
    estimated_carbon_kg: float = Field(..., description="Estimated carbon emissions")
    estimated_duration_hours: float = Field(..., description="Estimated duration")
    algorithm_used: str = Field(..., description="Algorithm used")
    optimization_time_seconds: float = Field(..., description="Optimization time")
    alternative_routes: Optional[List[Dict[str, Any]]] = Field(None, description="Alternative routes")


class SupplierBase(BaseModel):
    """Base supplier model."""
    name: str = Field(..., min_length=1, max_length=255, description="Supplier name")
    location_lat: float = Field(..., ge=-90, le=90, description="Location latitude")
    location_lng: float = Field(..., ge=-180, le=180, description="Location longitude")
    sustainability_score: int = Field(..., ge=1, le=100, description="Sustainability score (1-100)")
    renewable_energy_percent: float = Field(..., ge=0, le=100, description="Renewable energy percentage")
    carbon_intensity_kg_per_dollar: float = Field(..., ge=0, description="Carbon intensity")
    certification_level: str = Field(..., pattern="^(None|Bronze|Silver|Gold)$", description="Certification level")


class SupplierCreate(SupplierBase):
    """Model for creating a new supplier."""
    waste_reduction_percent: float = Field(0, ge=0, le=100, description="Waste reduction percentage")
    water_efficiency_score: int = Field(0, ge=1, le=100, description="Water efficiency score")
    social_responsibility_score: int = Field(0, ge=1, le=100, description="Social responsibility score")


class SupplierResponse(SupplierBase):
    """Model for supplier response."""
    supplier_id: str = Field(..., description="Supplier ID")
    last_audit_date: Optional[date] = Field(None, description="Last audit date")
    audit_score: Optional[int] = Field(None, ge=1, le=100, description="Audit score")
    waste_reduction_percent: float = Field(..., description="Waste reduction percentage")
    water_efficiency_score: int = Field(..., description="Water efficiency score")
    social_responsibility_score: int = Field(..., description="Social responsibility score")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SupplierSustainabilityResponse(BaseModel):
    """Model for supplier sustainability response."""
    supplier_id: str = Field(..., description="Supplier ID")
    name: str = Field(..., description="Supplier name")
    sustainability_score: int = Field(..., description="Overall sustainability score")
    emissions_breakdown: Dict[str, float] = Field(..., description="Emissions by category")
    improvement_opportunities: List[str] = Field(..., description="Suggested improvements")
    certification_status: str = Field(..., description="Current certification status")
    last_audit_date: Optional[date] = Field(None, description="Last audit date")


class ScenarioAnalysisRequest(BaseModel):
    """Model for scenario analysis request."""
    scenario_name: str = Field(..., description="Scenario name")
    scenario_type: str = Field(..., pattern="^(carbon_reduction|cost_optimization|supplier_optimization)$", description="Scenario type")
    parameters: Dict[str, Any] = Field(..., description="Scenario parameters")
    time_horizon_months: int = Field(..., gt=0, le=120, description="Time horizon in months")
    description: Optional[str] = Field(None, description="Scenario description")


class ScenarioAnalysisResponse(BaseModel):
    """Model for scenario analysis response."""
    scenario_id: str = Field(..., description="Scenario ID")
    scenario_name: str = Field(..., description="Scenario name")
    scenario_type: str = Field(..., description="Scenario type")
    baseline_carbon_kg: float = Field(..., description="Baseline carbon emissions")
    scenario_carbon_kg: float = Field(..., description="Scenario carbon emissions")
    carbon_reduction_percent: float = Field(..., description="Carbon reduction percentage")
    baseline_cost_usd: float = Field(..., description="Baseline cost")
    scenario_cost_usd: float = Field(..., description="Scenario cost")
    cost_impact_percent: float = Field(..., description="Cost impact percentage")
    roi_percent: Optional[float] = Field(None, description="Return on investment")
    payback_period_months: Optional[int] = Field(None, description="Payback period")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    """Model for health check response."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    database_status: str = Field(..., description="Database connection status")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Model for error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking") 