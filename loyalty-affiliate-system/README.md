# Loyalty & Affiliate Management System

A comprehensive loyalty program and affiliate management system with WhatsApp integration and ERP connectivity, built with FastAPI, React, and PostgreSQL.

## 🚀 Features

### Core Features
- **Customer Management**: Complete customer lifecycle management with tier progression
- **Loyalty Program**: Points-based rewards system with customizable tiers
- **Affiliate System**: Referral tracking, commission management, and performance analytics
- **WhatsApp Integration**: Automated messaging, templates, and delivery tracking
- **ERP Integration**: Seamless integration with Logic ERP for data synchronization
- **Analytics & Reporting**: Comprehensive dashboards and custom report generation

### Technical Features
- **Real-time Sync**: Automatic data synchronization between systems
- **API-First Architecture**: RESTful APIs with comprehensive documentation
- **Scalable Design**: Docker-based deployment with load balancing
- **Security**: JWT authentication, role-based access control, data encryption
- **Monitoring**: Real-time monitoring with Prometheus and Grafana
- **Testing**: Comprehensive test suite with unit and integration tests

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for development)
- Node.js 18+ (for development)
- PostgreSQL 15+ (for production)
- Redis 7+ (for caching and sessions)

## 🛠️ Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd loyalty-affiliate-system
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # Edit the environment files with your configuration
   ```

3. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access the applications**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Production Deployment

1. **Configure environment**
   ```bash
   cp .env.example .env.production
   # Edit with your production settings
   ```

2. **Deploy to production**
   ```bash
   ./deploy.sh deploy
   ```

3. **Monitor deployment**
   ```bash
   docker-compose logs -f
   ```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_loyalty_service.py

# Run integration tests
pytest tests/ -m integration

# Run performance tests
pytest tests/ -m performance
```

### Test Categories

- **Unit Tests**: Individual function and method testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Authentication and authorization testing

## 📊 Monitoring

### Access Monitoring Dashboards

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Application Health**: http://localhost:8000/health

### Key Metrics

- Customer acquisition and retention rates
- Loyalty points issued and redeemed
- Affiliate conversion rates
- WhatsApp message delivery and read rates
- System performance and error rates

## 🔧 Configuration

### Environment Variables

Key configuration options:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/loyalty_db

# Security
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ERP Integration
ERP_HOST=your-erp-host.com
ERP_API_KEY=your-erp-api-key

# WhatsApp
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_USERNAME=your-email@gmail.com
```

### Data Mapping

Configure field mappings between systems:

```bash
# Configure customer data mapping
curl -X POST http://localhost:8000/api/v1/erp/mappings \
  -H "Content-Type: application/json" \
  -d '{
    "mapping_type": "customer",
    "mappings": [
      {
        "source_field": "customer_id",
        "target_field": "erp_id",
        "transformation": null,
        "is_required": true
      }
    ]
  }'
```

## 🚀 API Documentation

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Customer Management

```bash
# Get customers
curl http://localhost:8000/api/v1/customers/

# Create customer
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }'
```

### Loyalty Operations

```bash
# Award points
curl -X POST http://localhost:8000/api/v1/loyalty/award \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "points": 100,
    "description": "Purchase bonus"
  }'
```

## 🔒 Security

- JWT-based authentication with refresh tokens
- Password hashing using bcrypt
- Rate limiting on API endpoints
- CORS configuration for cross-origin requests
- Input validation and sanitization
- SQL injection protection
- XSS protection

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Scale frontend services
docker-compose up -d --scale frontend=2
```

### Database Scaling

```bash
# Enable read replicas
# Configure connection pooling
# Set up database sharding for large datasets
```

## 🛠️ Development

### Project Structure

```
loyalty-affiliate-system/
├── backend/                 # FastAPI backend
│   ├── app/                # Main application
│   ├── tests/              # Test files
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/               # Source code
│   └── package.json       # Node dependencies
├── monitoring/             # Monitoring configuration
├── docker-compose.yml      # Production deployment
└── deploy.sh              # Deployment script
```

### Adding New Features

1. **Backend**: Add new endpoints in `app/api/v1/endpoints/`
2. **Frontend**: Create new components in `src/components/`
3. **Tests**: Add tests in `tests/` directory
4. **Documentation**: Update API docs and README

### Code Style

- **Python**: PEP 8 with Black formatting
- **JavaScript**: ESLint with Airbnb style guide
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstrings for all functions

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL configuration
   - Ensure PostgreSQL is running
   - Verify database credentials

2. **ERP Integration Issues**
   - Verify ERP_HOST and ERP_API_KEY
   - Check network connectivity
   - Review error logs in monitoring

3. **WhatsApp API Errors**
   - Validate WHATSAPP_ACCESS_TOKEN
   - Check API quotas and limits
   - Verify phone number format

4. **Performance Issues**
   - Check system resources
   - Review slow queries in logs
   - Consider database optimization

### Support

- Check the logs: `docker-compose logs -f`
- Monitor metrics: Grafana dashboard
- Review documentation: API docs at `/docs`
- Community support: GitHub issues

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📞 Contact

For support and questions:
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com
- API Documentation: http://localhost:8000/docs

---

**Happy coding! 🎉**