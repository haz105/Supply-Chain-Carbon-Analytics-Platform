"""
Machine Learning Models for Carbon Analytics
Predictive analytics and optimization for supply chain carbon emissions.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import joblib
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_session
from database.models import Shipment, CarbonEmission
from sqlalchemy import func, and_

class CarbonEmissionsPredictor:
    """Machine learning model for predicting carbon emissions."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = [
            'distance_km', 'weight_kg', 'transport_mode_encoded',
            'package_type_encoded', 'origin_lat', 'origin_lng',
            'destination_lat', 'destination_lng'
        ]
        self.target_column = 'co2_kg'
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training."""
        # Create a copy to avoid modifying original
        data = df.copy()
        
        # Encode categorical variables
        if 'transport_mode' in data.columns:
            if 'transport_mode' not in self.label_encoders:
                self.label_encoders['transport_mode'] = LabelEncoder()
                data['transport_mode_encoded'] = self.label_encoders['transport_mode'].fit_transform(data['transport_mode'])
            else:
                data['transport_mode_encoded'] = self.label_encoders['transport_mode'].transform(data['transport_mode'])
        
        if 'package_type' in data.columns:
            if 'package_type' not in self.label_encoders:
                self.label_encoders['package_type'] = LabelEncoder()
                data['package_type_encoded'] = self.label_encoders['package_type'].fit_transform(data['package_type'])
            else:
                data['package_type_encoded'] = self.label_encoders['package_type'].transform(data['package_type'])
        
        # Select features and target
        X = data[self.feature_columns]
        y = data[self.target_column]
        
        return X, y
    
    def train(self, df: pd.DataFrame, model_type: str = 'random_forest') -> Dict:
        """Train the model."""
        X, y = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Choose model
        if model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_type == 'linear':
            self.model = LinearRegression()
        elif model_type == 'ridge':
            self.model = Ridge(alpha=1.0)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'model_type': model_type
        }
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='r2')
        metrics['cv_r2_mean'] = cv_scores.mean()
        metrics['cv_r2_std'] = cv_scores.std()
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X, _ = self.prepare_data(df)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance (for tree-based models)."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if hasattr(self.model, 'feature_importances_'):
            importance_dict = dict(zip(self.feature_columns, self.model.feature_importances_))
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        else:
            return {"model_type": "Feature importance not available for this model type"}
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_columns,
            'target_column': self.target_column
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoders = model_data['label_encoders']
        self.feature_columns = model_data['feature_columns']
        self.target_column = model_data['target_column']

class RouteOptimizer:
    """Optimize routes for minimal carbon emissions."""
    
    def __init__(self):
        self.predictor = CarbonEmissionsPredictor()
        self.is_trained = False
    
    def train_optimizer(self, df: pd.DataFrame) -> Dict:
        """Train the route optimizer."""
        metrics = self.predictor.train(df, model_type='random_forest')
        self.is_trained = True
        return metrics
    
    def optimize_route(self, 
                      origin_lat: float, 
                      origin_lng: float,
                      destination_lat: float, 
                      destination_lng: float,
                      weight_kg: float,
                      package_type: str = 'Large Package',
                      transport_modes: List[str] = None) -> Dict:
        """Optimize route for minimal emissions."""
        if not self.is_trained:
            raise ValueError("Optimizer not trained. Call train_optimizer() first.")
        
        if transport_modes is None:
            transport_modes = ['air', 'ground', 'sea']
        
        # Calculate distance
        distance_km = self._calculate_distance(origin_lat, origin_lng, destination_lat, destination_lng)
        
        # Test different transport modes
        results = []
        for mode in transport_modes:
            # Create test data
            test_data = pd.DataFrame([{
                'distance_km': distance_km,
                'weight_kg': weight_kg,
                'transport_mode': mode,
                'package_type': package_type,
                'origin_lat': origin_lat,
                'origin_lng': origin_lng,
                'destination_lat': destination_lat,
                'destination_lng': destination_lng
            }])
            
            # Predict emissions
            predicted_emissions = self.predictor.predict(test_data)[0]
            
            results.append({
                'transport_mode': mode,
                'distance_km': distance_km,
                'predicted_emissions_kg': predicted_emissions,
                'efficiency_score': distance_km / predicted_emissions if predicted_emissions > 0 else 0
            })
        
        # Sort by emissions (ascending)
        results.sort(key=lambda x: x['predicted_emissions_kg'])
        
        return {
            'recommended_mode': results[0]['transport_mode'],
            'all_options': results,
            'distance_km': distance_km,
            'weight_kg': weight_kg
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers
        
        lat1, lng1, lat2, lng2 = map(np.radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return R * c

class EmissionsAnomalyDetector:
    """Detect anomalies in carbon emissions data."""
    
    def __init__(self, threshold: float = 2.0):
        self.threshold = threshold
        self.mean = None
        self.std = None
    
    def fit(self, emissions_data: pd.Series):
        """Fit the anomaly detector."""
        self.mean = emissions_data.mean()
        self.std = emissions_data.std()
    
    def detect_anomalies(self, emissions_data: pd.Series) -> List[Dict]:
        """Detect anomalies in emissions data."""
        if self.mean is None or self.std is None:
            raise ValueError("Detector not fitted. Call fit() first.")
        
        z_scores = np.abs((emissions_data - self.mean) / self.std)
        anomalies = []
        
        for i, z_score in enumerate(z_scores):
            if z_score > self.threshold:
                anomalies.append({
                    'index': i,
                    'value': emissions_data.iloc[i],
                    'z_score': z_score,
                    'is_anomaly': True
                })
        
        return anomalies

class SupplyChainClusterer:
    """Cluster supply chain data for pattern analysis."""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.pca = PCA(n_components=2)
        self.is_fitted = False
    
    def fit(self, df: pd.DataFrame) -> Dict:
        """Fit the clustering model."""
        # Prepare features for clustering
        features = df[['distance_km', 'weight_kg', 'co2_kg']].copy()
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Apply PCA for visualization
        features_pca = self.pca.fit_transform(features_scaled)
        
        # Fit K-means
        clusters = self.kmeans.fit_predict(features_scaled)
        
        # Add cluster labels to data
        df_clustered = df.copy()
        df_clustered['cluster'] = clusters
        df_clustered['pca_1'] = features_pca[:, 0]
        df_clustered['pca_2'] = features_pca[:, 1]
        
        # Calculate cluster statistics
        cluster_stats = []
        for i in range(self.n_clusters):
            cluster_data = df_clustered[df_clustered['cluster'] == i]
            cluster_stats.append({
                'cluster_id': i,
                'size': len(cluster_data),
                'avg_distance': cluster_data['distance_km'].mean(),
                'avg_weight': cluster_data['weight_kg'].mean(),
                'avg_emissions': cluster_data['co2_kg'].mean(),
                'dominant_mode': cluster_data['transport_mode'].mode().iloc[0] if len(cluster_data) > 0 else 'unknown'
            })
        
        self.is_fitted = True
        
        return {
            'df_clustered': df_clustered,
            'cluster_stats': cluster_stats,
            'pca_explained_variance': self.pca.explained_variance_ratio_
        }
    
    def predict_cluster(self, df: pd.DataFrame) -> np.ndarray:
        """Predict clusters for new data."""
        if not self.is_fitted:
            raise ValueError("Clusterer not fitted. Call fit() first.")
        
        features = df[['distance_km', 'weight_kg', 'co2_kg']].copy()
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        return self.kmeans.predict(features_scaled)

def get_training_data(days_back: int = 90) -> pd.DataFrame:
    """Get training data from database."""
    try:
        session = get_db_session()
        
        # Get data from the last N days
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = session.query(
            Shipment.shipment_id,
            Shipment.origin_lat,
            Shipment.origin_lng,
            Shipment.destination_lat,
            Shipment.destination_lng,
            Shipment.transport_mode,
            Shipment.weight_kg,
            Shipment.distance_km,
            Shipment.package_type,
            CarbonEmission.co2_kg,
            CarbonEmission.co2_equivalent_kg
        ).join(CarbonEmission, Shipment.shipment_id == CarbonEmission.shipment_id).filter(
            Shipment.departure_time >= start_date
        )
        
        results = query.all()
        
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=[
            'shipment_id', 'origin_lat', 'origin_lng', 'destination_lat', 'destination_lng',
            'transport_mode', 'weight_kg', 'distance_km', 'package_type', 'co2_kg', 'co2_equivalent_kg'
        ])
        
        session.close()
        return df
        
    except Exception as e:
        print(f"Error getting training data: {e}")
        return pd.DataFrame()

def train_all_models() -> Dict:
    """Train all ML models and return performance metrics."""
    print("🔄 Training machine learning models...")
    
    # Get training data
    df = get_training_data()
    
    if df.empty:
        return {"error": "No training data available"}
    
    print(f"📊 Training on {len(df)} records")
    
    results = {}
    
    # Train emissions predictor
    try:
        predictor = CarbonEmissionsPredictor()
        predictor_metrics = predictor.train(df, model_type='random_forest')
        results['predictor'] = predictor_metrics
        
        # Save model
        os.makedirs('models', exist_ok=True)
        predictor.save_model('models/emissions_predictor.pkl')
        
        print(f"✅ Emissions predictor trained - R²: {predictor_metrics['r2']:.3f}")
        
    except Exception as e:
        results['predictor'] = {"error": str(e)}
        print(f"❌ Emissions predictor training failed: {e}")
    
    # Train route optimizer
    try:
        optimizer = RouteOptimizer()
        optimizer_metrics = optimizer.train_optimizer(df)
        results['optimizer'] = optimizer_metrics
        
        # Save optimizer
        with open('models/route_optimizer.pkl', 'wb') as f:
            pickle.dump(optimizer, f)
        
        print(f"✅ Route optimizer trained - R²: {optimizer_metrics['r2']:.3f}")
        
    except Exception as e:
        results['optimizer'] = {"error": str(e)}
        print(f"❌ Route optimizer training failed: {e}")
    
    # Train anomaly detector
    try:
        detector = EmissionsAnomalyDetector()
        detector.fit(df['co2_kg'])
        
        # Save detector
        with open('models/anomaly_detector.pkl', 'wb') as f:
            pickle.dump(detector, f)
        
        results['anomaly_detector'] = {"status": "trained", "threshold": detector.threshold}
        print("✅ Anomaly detector trained")
        
    except Exception as e:
        results['anomaly_detector'] = {"error": str(e)}
        print(f"❌ Anomaly detector training failed: {e}")
    
    # Train clusterer
    try:
        clusterer = SupplyChainClusterer()
        clustering_results = clusterer.fit(df)
        results['clusterer'] = clustering_results['cluster_stats']
        
        # Save clusterer
        with open('models/supply_chain_clusterer.pkl', 'wb') as f:
            pickle.dump(clusterer, f)
        
        print(f"✅ Supply chain clusterer trained - {len(clustering_results['cluster_stats'])} clusters")
        
    except Exception as e:
        results['clusterer'] = {"error": str(e)}
        print(f"❌ Supply chain clusterer training failed: {e}")
    
    return results

if __name__ == "__main__":
    # Train all models
    results = train_all_models()
    print("\n📊 Training Results:")
    for model_name, metrics in results.items():
        print(f"{model_name}: {metrics}") 