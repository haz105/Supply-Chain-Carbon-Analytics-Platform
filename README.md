# Supply Chain Carbon Analytics Platform

A comprehensive supply chain sustainability analytics platform demonstrating advanced business intelligence, data engineering, and machine learning capabilities for carbon footprint tracking and optimization.

## 🎯 Project Overview

This platform provides end-to-end carbon analytics for supply chain operations, featuring:
- Real-time carbon emission tracking across transportation networks
- Machine learning-powered emission prediction and route optimization
- Supplier sustainability scoring and ESG analytics
- Interactive dashboards for executive decision-making
- AWS cloud-native architecture with scalable data processing

## 🏗️ Architecture

```
Data Sources (APIs) → Python ETL Pipeline → PostgreSQL/Timestream → 
ML Models → FastAPI Backend → Dashboard Frontend → Tableau Integration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Docker & Docker Compose
- AWS Account (for cloud deployment)

### Local Development Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd Supply-Chain-Carbon-Analytics-Platform
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup**
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# Run database migrations
alembic upgrade head
```

4. **Data Generation**
```bash
python scripts/generate_sample_data.py
```

5. **Start the Application**
```bash
# Start FastAPI backend
uvicorn api.main:app --reload

# Start Dashboard (in separate terminal)
python dashboards/main.py
```

## 📊 Key Features

### Data Engineering
- **ETL Pipeline**: Automated data ingestion from multiple sources
- **Data Quality**: Comprehensive validation and monitoring
- **Real-time Processing**: Stream processing for live carbon tracking

### Analytics & ML
- **Carbon Prediction**: ML models for emission forecasting
- **Route Optimization**: Multi-objective optimization (cost vs. carbon)
- **Supplier Scoring**: ESG-based sustainability rankings
- **Scenario Analysis**: What-if modeling for sustainability initiatives

### Visualization
- **Executive Dashboard**: High-level KPIs and trends
- **Operational Views**: Real-time monitoring and alerts
- **Strategic Planning**: Investment ROI and target tracking
- **Tableau Integration**: Enterprise-grade reporting

## 🗄️ Database Schema

### Core Tables
- **shipments**: Transportation data with geospatial coordinates
- **carbon_emissions**: Calculated emission metrics
- **suppliers**: ESG and sustainability information
- **weather_data**: Environmental impact factors
- **optimization_results**: Route and scenario analysis

## 🔧 API Endpoints

### Emissions Analytics
- `GET /emissions/summary` - Aggregated carbon data
- `GET /emissions/trends` - Time series analysis
- `POST /emissions/calculate` - Real-time calculation

### Route Optimization
- `POST /optimization/routes` - Multi-objective route planning
- `GET /optimization/scenarios` - What-if analysis
- `GET /optimization/recommendations` - AI-powered suggestions

### Supplier Management
- `GET /suppliers/sustainability` - ESG scoring
- `GET /suppliers/rankings` - Performance comparisons
- `POST /suppliers/audit` - Assessment tracking

## 🤖 Machine Learning Models

### Carbon Footprint Prediction
- **Features**: Distance, weight, transport mode, weather, fuel efficiency
- **Algorithm**: Gradient Boosting with feature engineering
- **Accuracy**: <5% error rate on test data

### Route Optimization
- **Algorithm**: Genetic Algorithm with multi-objective optimization
- **Objectives**: Minimize cost, carbon emissions, delivery time
- **Constraints**: Weather, traffic, capacity limits

### Supplier Scoring
- **Factors**: Renewable energy, carbon intensity, certifications
- **Method**: Weighted composite scoring with normalization
- **Output**: 1-100 sustainability score

## 📈 Performance Metrics

- **Data Processing**: 100K+ shipments/day
- **Query Response**: <1 second for dashboard queries
- **ML Inference**: 1000+ predictions/second
- **Uptime**: 99.9% availability target

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test categories
pytest tests/test_analytics/
pytest tests/test_ml_models/
pytest tests/test_api/
```

## 🚀 Deployment

### AWS Deployment
```bash
# Deploy infrastructure
terraform init
terraform plan
terraform apply

# Deploy application
docker build -t carbon-analytics .
docker push <ecr-repository>
```

### Docker Compose (Local)
```bash
docker-compose up -d
```

## 📊 Dashboard Access

- **Executive Dashboard**: http://localhost:8050
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔐 Security

- Environment-based configuration
- API key authentication
- Database connection encryption
- Input validation and sanitization
- Rate limiting and monitoring

## 📝 Development Guidelines

- Follow PEP 8 style guidelines
- Use type hints throughout
- Include comprehensive docstrings
- Write unit tests for all functions
- Use pre-commit hooks for code quality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🎯 Success Metrics

- **Accuracy**: <5% error rate in carbon calculations
- **Efficiency**: 10-15% emission reduction through optimization
- **Insights**: 20+ actionable sustainability KPIs
- **Performance**: Sub-second dashboard response times

---

**Built for Amazon Business Intelligence Engineer Internship Application**
*Demonstrating advanced SQL, Python, AWS, ML, and BI capabilities*