"""
Advanced Analytics for Supply Chain Carbon Analytics Platform
Real-time streaming, supplier analytics, and predictive insights.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import asyncio
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func, and_, desc

class RealTimeAnalytics:
    """Real-time analytics for live data processing."""
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def detect_real_time_anomalies(self, recent_data: pd.DataFrame) -> List[Dict]:
        """Detect anomalies in real-time data."""
        if recent_data.empty:
            return []
        
        # Prepare features for anomaly detection
        features = recent_data[['co2_kg', 'distance_km', 'weight_kg']].copy()
        features = features.fillna(features.mean())
        
        # Fit detector if not already fitted
        if not self.is_fitted:
            self.anomaly_detector.fit(features)
            self.is_fitted = True
        
        # Predict anomalies
        predictions = self.anomaly_detector.predict(features)
        anomaly_scores = self.anomaly_detector.decision_function(features)
        
        # Find anomalies (predictions == -1)
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
            if pred == -1:  # Anomaly detected
                anomalies.append({
                    'shipment_id': str(recent_data.iloc[i]['shipment_id']),
                    'anomaly_score': float(score),
                    'co2_kg': float(recent_data.iloc[i]['co2_kg']),
                    'distance_km': float(recent_data.iloc[i]['distance_km']),
                    'transport_mode': recent_data.iloc[i]['transport_mode'],
                    'detected_at': datetime.now().isoformat()
                })
        
        return anomalies
    
    def get_real_time_metrics(self, hours_back: int = 24) -> Dict:
        """Get real-time metrics for the last N hours."""
        try:
            session = get_db_session()
            
            # Get data from last N hours
            start_time = datetime.now() - timedelta(hours=hours_back)
            
            query = session.query(
                func.count(Shipment.shipment_id).label('shipment_count'),
                func.sum(CarbonEmission.co2_kg).label('total_emissions'),
                func.avg(CarbonEmission.co2_kg).label('avg_emissions'),
                func.sum(Shipment.distance_km).label('total_distance')
            ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).filter(
                Shipment.departure_time >= start_time
            )
            
            result = query.first()
            
            # Get recent shipments for anomaly detection
            recent_shipments = session.query(
                Shipment.shipment_id,
                Shipment.transport_mode,
                Shipment.distance_km,
                Shipment.weight_kg,
                CarbonEmission.co2_kg
            ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).filter(
                Shipment.departure_time >= start_time
            ).order_by(desc(Shipment.departure_time)).limit(100).all()
            
            session.close()
            
            # Convert to DataFrame for anomaly detection
            recent_df = pd.DataFrame(recent_shipments, columns=[
                'shipment_id', 'transport_mode', 'distance_km', 'weight_kg', 'co2_kg'
            ])
            
            # Detect anomalies
            anomalies = self.detect_real_time_anomalies(recent_df)
            
            return {
                'shipment_count': int(result[0] or 0),
                'total_emissions_kg': float(result[1] or 0),
                'avg_emissions_kg': float(result[2] or 0),
                'total_distance_km': float(result[3] or 0),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'time_window_hours': hours_back,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting real-time metrics: {e}")
            return {}

class SupplierAnalytics:
    """Advanced supplier sustainability analytics."""
    
    def __init__(self):
        self.sustainability_weights = {
            'emissions_efficiency': 0.4,
            'transport_optimization': 0.3,
            'package_efficiency': 0.2,
            'consistency': 0.1
        }
    
    def calculate_supplier_sustainability_score(self, supplier_id: str) -> Dict:
        """Calculate comprehensive sustainability score for a supplier."""
        try:
            session = get_db_session()
            
            # Get supplier data
            supplier_data = session.query(
                Shipment.supplier_id,
                func.count(Shipment.shipment_id).label('total_shipments'),
                func.avg(CarbonEmission.co2_kg).label('avg_emissions'),
                func.sum(CarbonEmission.co2_kg).label('total_emissions'),
                func.avg(Shipment.distance_km).label('avg_distance'),
                func.sum(Shipment.distance_km).label('total_distance')
            ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).filter(
                Shipment.supplier_id == supplier_id
            ).group_by(Shipment.supplier_id).first()
            
            if not supplier_data:
                return {'error': 'Supplier not found'}
            
            # Calculate efficiency metrics
            emissions_efficiency = 1 / (supplier_data[3] / supplier_data[5]) if supplier_data[5] > 0 else 0
            transport_optimization = self._calculate_transport_optimization(session, supplier_id)
            package_efficiency = self._calculate_package_efficiency(session, supplier_id)
            consistency = self._calculate_consistency(session, supplier_id)
            
            # Calculate weighted sustainability score
            sustainability_score = (
                emissions_efficiency * self.sustainability_weights['emissions_efficiency'] +
                transport_optimization * self.sustainability_weights['transport_optimization'] +
                package_efficiency * self.sustainability_weights['package_efficiency'] +
                consistency * self.sustainability_weights['consistency']
            ) * 100
            
            # Normalize score to 0-100 range
            sustainability_score = max(0, min(100, sustainability_score))
            
            session.close()
            
            return {
                'supplier_id': supplier_id,
                'sustainability_score': round(sustainability_score, 2),
                'total_shipments': int(supplier_data[1]),
                'avg_emissions_kg': float(supplier_data[2] or 0),
                'total_emissions_kg': float(supplier_data[3] or 0),
                'avg_distance_km': float(supplier_data[4] or 0),
                'total_distance_km': float(supplier_data[5] or 0),
                'metrics': {
                    'emissions_efficiency': round(emissions_efficiency, 4),
                    'transport_optimization': round(transport_optimization, 4),
                    'package_efficiency': round(package_efficiency, 4),
                    'consistency': round(consistency, 4)
                },
                'improvement_opportunities': self._get_improvement_opportunities(sustainability_score)
            }
            
        except Exception as e:
            print(f"Error calculating supplier sustainability: {e}")
            return {'error': str(e)}
    
    def _calculate_transport_optimization(self, session, supplier_id: str) -> float:
        """Calculate transport optimization score."""
        # Get transport mode distribution
        transport_data = session.query(
            Shipment.transport_mode,
            func.count(Shipment.shipment_id)
        ).filter(Shipment.supplier_id == supplier_id).group_by(Shipment.transport_mode).all()
        
        if not transport_data:
            return 0
        
        # Calculate optimization score (prefer ground over air)
        total_shipments = sum(count for _, count in transport_data)
        ground_shipments = sum(count for mode, count in transport_data if mode == 'ground')
        
        return ground_shipments / total_shipments if total_shipments > 0 else 0
    
    def _calculate_package_efficiency(self, session, supplier_id: str) -> float:
        """Calculate package efficiency score."""
        # Get package type distribution
        package_data = session.query(
            Shipment.package_type,
            func.avg(CarbonEmission.co2_kg)
        ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).filter(
            Shipment.supplier_id == supplier_id
        ).group_by(Shipment.package_type).all()
        
        if not package_data:
            return 0
        
        # Calculate efficiency (lower emissions per package type = higher score)
        avg_emissions = [emissions for _, emissions in package_data]
        min_emissions = min(avg_emissions) if avg_emissions else 0
        
        return 1 / (sum(avg_emissions) / len(avg_emissions) / min_emissions) if min_emissions > 0 else 0
    
    def _calculate_consistency(self, session, supplier_id: str) -> float:
        """Calculate consistency score based on emission variance."""
        emissions_data = session.query(CarbonEmission.co2_kg).join(
            Shipment, Shipment.shipment_id == CarbonEmission.shipment_id
        ).filter(Shipment.supplier_id == supplier_id).all()
        
        if len(emissions_data) < 2:
            return 0
        
        emissions = [float(e[0]) for e in emissions_data]
        variance = np.var(emissions)
        mean_emissions = np.mean(emissions)
        
        # Lower variance = higher consistency
        consistency = 1 / (1 + variance / mean_emissions) if mean_emissions > 0 else 0
        return min(1, consistency)
    
    def _get_improvement_opportunities(self, score: float) -> List[str]:
        """Get improvement opportunities based on sustainability score."""
        opportunities = []
        
        if score < 30:
            opportunities.extend([
                "Implement carbon tracking system",
                "Switch to renewable energy sources",
                "Optimize transport routes"
            ])
        elif score < 60:
            opportunities.extend([
                "Improve package efficiency",
                "Increase ground transport usage",
                "Standardize shipping processes"
            ])
        elif score < 80:
            opportunities.extend([
                "Fine-tune route optimization",
                "Implement real-time monitoring",
                "Consider electric vehicles"
            ])
        else:
            opportunities.append("Maintain current sustainability practices")
        
        return opportunities

class PredictiveAnalytics:
    """Predictive analytics for emissions forecasting and optimization."""
    
    def __init__(self):
        self.forecast_model = None
        self.trend_analyzer = None
    
    def forecast_emissions(self, days_ahead: int = 30) -> Dict:
        """Forecast emissions for the next N days."""
        try:
            session = get_db_session()
            
            # Get historical daily emissions
            daily_emissions = session.query(
                func.date(Shipment.departure_time).label('date'),
                func.sum(CarbonEmission.co2_kg).label('daily_emissions')
            ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).group_by(
                func.date(Shipment.departure_time)
            ).order_by(func.date(Shipment.departure_time)).all()
            
            session.close()
            
            if len(daily_emissions) < 7:  # Need at least a week of data
                return {'error': 'Insufficient historical data for forecasting'}
            
            # Convert to DataFrame
            df = pd.DataFrame(daily_emissions, columns=['date', 'emissions'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Simple moving average forecast
            window_size = min(7, len(df) // 2)
            forecast_values = []
            
            for i in range(days_ahead):
                # Use last window_size days to predict next day
                recent_avg = df['emissions'].tail(window_size).mean()
                forecast_values.append(recent_avg)
            
            # Generate forecast dates
            last_date = df.index[-1]
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_ahead)]
            
            return {
                'forecast_dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
                'forecast_emissions': [float(v) for v in forecast_values],
                'total_forecast_emissions': float(sum(forecast_values)),
                'avg_daily_forecast': float(np.mean(forecast_values)),
                'confidence_interval': {
                    'lower': float(np.mean(forecast_values) * 0.8),
                    'upper': float(np.mean(forecast_values) * 1.2)
                },
                'method': 'Moving Average',
                'window_size': window_size
            }
            
        except Exception as e:
            print(f"Error forecasting emissions: {e}")
            return {'error': str(e)}
    
    def analyze_trends(self, days_back: int = 90) -> Dict:
        """Analyze emission trends over time."""
        try:
            session = get_db_session()
            
            # Get daily emissions for trend analysis
            start_date = datetime.now() - timedelta(days=days_back)
            
            daily_data = session.query(
                func.date(Shipment.departure_time).label('date'),
                func.sum(CarbonEmission.co2_kg).label('emissions'),
                func.count(Shipment.shipment_id).label('shipments')
            ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).filter(
                Shipment.departure_time >= start_date
            ).group_by(func.date(Shipment.departure_time)).order_by(
                func.date(Shipment.departure_time)
            ).all()
            
            session.close()
            
            if len(daily_data) < 7:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Convert to DataFrame
            df = pd.DataFrame(daily_data, columns=['date', 'emissions', 'shipments'])
            df['date'] = pd.to_datetime(df['date'])
            
            # Calculate trends
            emissions_trend = np.polyfit(range(len(df)), df['emissions'], 1)[0]
            shipments_trend = np.polyfit(range(len(df)), df['shipments'], 1)[0]
            
            # Calculate efficiency trend (emissions per shipment)
            df['efficiency'] = df['emissions'] / df['shipments']
            efficiency_trend = np.polyfit(range(len(df)), df['efficiency'], 1)[0]
            
            # Determine trend direction
            def get_trend_direction(trend_value):
                if trend_value > 0.01:
                    return 'increasing'
                elif trend_value < -0.01:
                    return 'decreasing'
                else:
                    return 'stable'
            
            return {
                'analysis_period_days': days_back,
                'trends': {
                    'emissions': {
                        'direction': get_trend_direction(emissions_trend),
                        'slope': float(emissions_trend),
                        'interpretation': 'Daily emissions trend'
                    },
                    'shipments': {
                        'direction': get_trend_direction(shipments_trend),
                        'slope': float(shipments_trend),
                        'interpretation': 'Daily shipment volume trend'
                    },
                    'efficiency': {
                        'direction': get_trend_direction(efficiency_trend),
                        'slope': float(efficiency_trend),
                        'interpretation': 'Emissions per shipment trend'
                    }
                },
                'summary': {
                    'total_emissions': float(df['emissions'].sum()),
                    'total_shipments': int(df['shipments'].sum()),
                    'avg_daily_emissions': float(df['emissions'].mean()),
                    'avg_daily_shipments': float(df['shipments'].mean()),
                    'avg_efficiency': float(df['efficiency'].mean())
                }
            }
            
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return {'error': str(e)}

def get_advanced_analytics_summary() -> Dict:
    """Get comprehensive advanced analytics summary."""
    print("🔍 Generating Advanced Analytics Summary...")
    
    # Initialize analytics components
    real_time = RealTimeAnalytics()
    supplier_analytics = SupplierAnalytics()
    predictive = PredictiveAnalytics()
    
    # Get real-time metrics
    real_time_metrics = real_time.get_real_time_metrics(hours_back=24)
    
    # Get trend analysis
    trend_analysis = predictive.analyze_trends(days_back=30)
    
    # Get emissions forecast
    emissions_forecast = predictive.forecast_emissions(days_ahead=7)
    
    return {
        'real_time_metrics': real_time_metrics,
        'trend_analysis': trend_analysis,
        'emissions_forecast': emissions_forecast,
        'generated_at': datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Test advanced analytics
    summary = get_advanced_analytics_summary()
    print(json.dumps(summary, indent=2, default=str)) 