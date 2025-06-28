"""
Main FastAPI application for the Supply Chain Carbon Analytics Platform.
Provides REST API endpoints for emissions analytics, route optimization, and supplier management.
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
import time

from config.settings import get_settings
from database.connection import get_db
from api.models import (
    EmissionsSummaryRequest, EmissionsSummaryResponse,
    RouteOptimizationRequest, RouteOptimizationResponse,
    SupplierSustainabilityResponse, HealthCheckResponse,
    ErrorResponse
)

# Initialize logging
logger = structlog.get_logger(__name__)
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Supply Chain Carbon Analytics API",
    description="Comprehensive API for supply chain sustainability analytics and carbon footprint tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for tracking
start_time = time.time()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Supply Chain Carbon Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database status."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        db_status = "unhealthy"
    
    uptime = time.time() - start_time
    
    return HealthCheckResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        timestamp=datetime.now(),
        version="1.0.0",
        database_status=db_status,
        uptime_seconds=uptime
    )


@app.post("/emissions/summary", response_model=EmissionsSummaryResponse)
async def get_emissions_summary(
    request: EmissionsSummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Get aggregated carbon emissions summary for a date range.
    
    Args:
        request: Emissions summary request with date range and filters
        db: Database session
    
    Returns:
        Emissions summary with totals and breakdowns
    """
    try:
        logger.info(
            "Processing emissions summary request",
            start_date=request.start_date,
            end_date=request.end_date,
            transport_mode=request.transport_mode,
            supplier_id=request.supplier_id
        )
        
        # Build query based on filters
        query = """
            SELECT 
                SUM(ce.co2_kg) as total_co2_kg,
                SUM(ce.co2_equivalent_kg) as total_co2_equivalent_kg,
                COUNT(s.shipment_id) as shipment_count,
                AVG(ce.co2_kg) as average_co2_per_shipment
            FROM shipments s
            JOIN carbon_emissions ce ON s.shipment_id = ce.shipment_id
            WHERE s.departure_time >= :start_date 
            AND s.departure_time <= :end_date
        """
        
        params = {
            "start_date": request.start_date,
            "end_date": request.end_date
        }
        
        if request.transport_mode:
            query += " AND s.transport_mode = :transport_mode"
            params["transport_mode"] = request.transport_mode
        
        if request.supplier_id:
            query += " AND s.supplier_id = :supplier_id"
            params["supplier_id"] = request.supplier_id
        
        # Execute query
        result = db.execute(text(query), params).fetchone()
        
        if not result or result[0] is None:
            # Return empty summary if no data
            return EmissionsSummaryResponse(
                total_co2_kg=0.0,
                total_co2_equivalent_kg=0.0,
                shipment_count=0,
                average_co2_per_shipment=0.0,
                transport_mode_breakdown={},
                date_range=f"{request.start_date} to {request.end_date}"
            )
        
        # Get transport mode breakdown
        breakdown_query = """
            SELECT 
                s.transport_mode,
                SUM(ce.co2_kg) as total_co2
            FROM shipments s
            JOIN carbon_emissions ce ON s.shipment_id = ce.shipment_id
            WHERE s.departure_time >= :start_date 
            AND s.departure_time <= :end_date
        """
        
        if request.transport_mode:
            breakdown_query += " AND s.transport_mode = :transport_mode"
        if request.supplier_id:
            breakdown_query += " AND s.supplier_id = :supplier_id"
        
        breakdown_query += " GROUP BY s.transport_mode"
        
        breakdown_result = db.execute(text(breakdown_query), params).fetchall()
        transport_mode_breakdown = {
            row[0]: float(row[1]) for row in breakdown_result
        }
        
        return EmissionsSummaryResponse(
            total_co2_kg=float(result[0]),
            total_co2_equivalent_kg=float(result[1]),
            shipment_count=int(result[2]),
            average_co2_per_shipment=float(result[3]),
            transport_mode_breakdown=transport_mode_breakdown,
            date_range=f"{request.start_date} to {request.end_date}"
        )
        
    except Exception as e:
        logger.error("Error getting emissions summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emissions summary"
        )


@app.post("/optimization/routes", response_model=RouteOptimizationResponse)
async def optimize_route(
    request: RouteOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize route for a shipment based on cost, carbon, or balanced priorities.
    
    Args:
        request: Route optimization request with origin, destination, and parameters
        db: Database session
    
    Returns:
        Optimized route with cost and carbon estimates
    """
    try:
        logger.info(
            "Processing route optimization request",
            origin=f"({request.origin_lat}, {request.origin_lng})",
            destination=f"({request.destination_lat}, {request.destination_lng})",
            weight_kg=request.weight_kg,
            priority=request.priority
        )
        
        # Calculate distance (simplified - in production, use proper routing API)
        from geopy.distance import geodesic
        distance_km = geodesic(
            (request.origin_lat, request.origin_lng),
            (request.destination_lat, request.destination_lng)
        ).kilometers
        
        # Simple route optimization logic (placeholder for more sophisticated algorithms)
        if request.priority == "carbon":
            # Prefer ground transport for carbon optimization
            transport_mode = "ground"
            cost_multiplier = 1.2
            carbon_multiplier = 0.8
        elif request.priority == "cost":
            # Prefer sea transport for cost optimization
            transport_mode = "sea"
            cost_multiplier = 0.7
            carbon_multiplier = 1.1
        else:  # balanced
            # Use air transport for balanced approach
            transport_mode = "air"
            cost_multiplier = 1.0
            carbon_multiplier = 1.0
        
        # Calculate estimates
        base_cost_per_km = {
            "air": 2.5,
            "ground": 0.8,
            "sea": 0.3
        }
        
        base_carbon_per_km_kg = {
            "air": 1.02,
            "ground": 0.089,
            "sea": 0.014
        }
        
        estimated_cost = base_cost_per_km[transport_mode] * distance_km * cost_multiplier
        estimated_carbon = base_carbon_per_km_kg[transport_mode] * (request.weight_kg / 1000) * distance_km * carbon_multiplier
        estimated_duration = distance_km / {
            "air": 800,
            "ground": 60,
            "sea": 25
        }[transport_mode]
        
        # Create route waypoints (simplified)
        optimal_route = [
            {"lat": request.origin_lat, "lng": request.origin_lng},
            {"lat": request.destination_lat, "lng": request.destination_lng}
        ]
        
        return RouteOptimizationResponse(
            optimization_id=f"opt_{int(time.time())}",
            optimal_route=optimal_route,
            total_distance_km=distance_km,
            estimated_cost_usd=estimated_cost,
            estimated_carbon_kg=estimated_carbon,
            estimated_duration_hours=estimated_duration,
            algorithm_used="simple_heuristic",
            optimization_time_seconds=0.1,
            alternative_routes=None
        )
        
    except Exception as e:
        logger.error("Error optimizing route", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize route"
        )


@app.get("/suppliers/sustainability", response_model=List[SupplierSustainabilityResponse])
async def get_supplier_sustainability(db: Session = Depends(get_db)):
    """
    Get sustainability scores and metrics for all suppliers.
    
    Args:
        db: Database session
    
    Returns:
        List of supplier sustainability information
    """
    try:
        logger.info("Processing supplier sustainability request")
        
        # Query supplier sustainability data
        query = """
            SELECT 
                s.supplier_id,
                s.name,
                s.sustainability_score,
                s.certification_level,
                s.last_audit_date,
                COALESCE(SUM(ce.co2_kg), 0) as total_emissions
            FROM suppliers s
            LEFT JOIN shipments sh ON s.supplier_id = sh.supplier_id
            LEFT JOIN carbon_emissions ce ON sh.shipment_id = ce.shipment_id
            GROUP BY s.supplier_id, s.name, s.sustainability_score, s.certification_level, s.last_audit_date
            ORDER BY s.sustainability_score DESC
        """
        
        result = db.execute(text(query)).fetchall()
        
        suppliers = []
        for row in result:
            # Generate improvement opportunities based on scores
            opportunities = []
            if row[2] < 50:  # sustainability_score
                opportunities.append("Increase renewable energy usage")
                opportunities.append("Improve waste management practices")
            if row[2] < 70:
                opportunities.append("Obtain sustainability certifications")
            
            suppliers.append(SupplierSustainabilityResponse(
                supplier_id=row[0],
                name=row[1],
                sustainability_score=row[2],
                emissions_breakdown={"total_co2_kg": float(row[5])},
                improvement_opportunities=opportunities,
                certification_status=row[3],
                last_audit_date=row[4]
            ))
        
        return suppliers
        
    except Exception as e:
        logger.error("Error getting supplier sustainability", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve supplier sustainability data"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return ErrorResponse(
        error="Internal server error",
        detail=str(exc),
        timestamp=datetime.now(),
        request_id=str(int(time.time()))
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 