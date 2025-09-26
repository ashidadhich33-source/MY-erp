# Production Testing Guide

This guide provides comprehensive instructions for testing the Loyalty & Affiliate Management System before production deployment.

## 🚀 Quick Start

### Automated Testing

Run the automated production readiness tests:

```bash
./run_tests.sh
```

This script performs basic checks on all critical components.

### Manual Testing Steps

Follow these steps to thoroughly test your system:

## 1. Environment Setup

### 1.1 Backend Environment

1. **Copy environment template:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Update environment variables:**
   ```bash
   # Database
   DATABASE_URL=postgresql://loyalty_user:loyalty_password@localhost:5432/loyalty_db

   # Security
   SECRET_KEY=your-super-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Demo credentials (change in production!)
   DEMO_ADMIN_EMAIL=admin@yourcompany.com
   DEMO_ADMIN_PASSWORD=your_secure_admin_password
   DEMO_USER_EMAIL=user@yourcompany.com
   DEMO_USER_PASSWORD=your_secure_user_password
   ```

### 1.2 Frontend Environment

1. **Copy environment template:**
   ```bash
   cp frontend/.env.example frontend/.env
   ```

2. **Update API configuration:**
   ```bash
   REACT_APP_API_BASE_URL=http://your-backend-url/api/v1
   REACT_APP_ENVIRONMENT=production
   ```

## 2. Database Testing

### 2.1 Database Migration

1. **Run database migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Verify database schema:**
   ```bash
   # Check if all tables were created
   psql $DATABASE_URL -c "\dt"
   ```

### 2.2 Data Integrity Tests

1. **Test database connections:**
   ```python
   from app.core.database import get_db
   from sqlalchemy.orm import Session

   db: Session = next(get_db())
   print("Database connection successful")
   ```

2. **Test model relationships:**
   ```python
   from app.models import User, Customer, LoyaltyTransaction
   # Test creating related objects
   ```

## 3. API Testing

### 3.1 Authentication Tests

#### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "password": "test123",
    "role": "customer"
  }'
```

#### Login User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

#### Get Current User
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3.2 Customer Management Tests

#### Create Customer
```bash
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "tier": "bronze"
  }'
```

#### Get Customer Details
```bash
curl -X GET http://localhost:8000/api/v1/customers/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3.3 Loyalty Program Tests

#### Award Points
```bash
curl -X POST http://localhost:8000/api/v1/loyalty/points/award \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "customer_id": 1,
    "points": 100,
    "description": "Purchase bonus",
    "source": "purchase"
  }'
```

#### Check Points Balance
```bash
curl -X GET http://localhost:8000/api/v1/loyalty/points/1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 4. Integration Testing

### 4.1 Frontend-Backend Integration

1. **Start the backend:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test complete user journey:**
   - Register new user
   - Login
   - Access dashboard
   - Manage customers
   - Award/redeem points
   - Check analytics

### 4.2 External Service Integration

#### WhatsApp Integration Test
```bash
curl -X POST http://localhost:8000/api/v1/whatsapp/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "recipient_phone": "+1234567890",
    "message_type": "text",
    "content": "Test message from production testing"
  }'
```

#### ERP Integration Test
```bash
curl -X POST http://localhost:8000/api/v1/erp/sync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "sync_type": "customers",
    "since": "2024-01-01T00:00:00Z"
  }'
```

## 5. Performance Testing

### 5.1 Load Testing

1. **Install load testing tools:**
   ```bash
   pip install locust
   ```

2. **Create load test script:**
   ```python
   # load_test.py
   from locust import HttpUser, task, between

   class LoyaltyUser(HttpUser):
       wait_time = between(1, 3)

       @task
       def get_dashboard(self):
           self.client.get("/api/v1/analytics/dashboard")

       @task
       def award_points(self):
           self.client.post("/api/v1/loyalty/points/award",
                           json={"customer_id": 1, "points": 10, "source": "test"})
   ```

3. **Run load test:**
   ```bash
   locust -f load_test.py --host http://localhost:8000
   ```

### 5.2 Database Performance

1. **Check slow queries:**
   ```sql
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```

2. **Index optimization:**
   ```sql
   CREATE INDEX CONCURRENTLY idx_loyalty_transactions_customer_created
   ON loyalty_transactions(customer_id, created_at);
   ```

## 6. Security Testing

### 6.1 Authentication Security

1. **Test SQL injection protection:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -d "username=admin' OR '1'='1&password=anything"
   ```

2. **Test rate limiting:**
   ```bash
   for i in {1..20}; do
       curl -X POST http://localhost:8000/api/v1/auth/login \
         -d "username=wrong&password=wrong"
   done
   ```

### 6.2 Data Validation

1. **Test input validation:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/customers/ \
     -H "Content-Type: application/json" \
     -d '{"name": "", "email": "invalid-email"}'
   ```

2. **Test XSS protection:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/customers/ \
     -H "Content-Type: application/json" \
     -d '{"name": "<script>alert(\"xss\")</script>", "email": "test@example.com"}'
   ```

## 7. Monitoring & Health Checks

### 7.1 Health Endpoints

1. **API Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Database Health Check:**
   ```bash
   curl http://localhost:8000/api/v1/health/db
   ```

3. **External Services Health:**
   ```bash
   curl http://localhost:8000/api/v1/health/external
   ```

### 7.2 Logging Verification

1. **Check application logs:**
   ```bash
   tail -f backend/logs/app.log
   ```

2. **Check error logs:**
   ```bash
   tail -f backend/logs/error.log
   ```

## 8. Production Deployment Tests

### 8.1 Docker Deployment

1. **Build and test containers:**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Test container health:**
   ```bash
   docker-compose ps
   docker-compose logs backend
   docker-compose logs frontend
   ```

### 8.2 Kubernetes Deployment (if applicable)

1. **Deploy to staging:**
   ```bash
   kubectl apply -f k8s/
   kubectl rollout status deployment/loyalty-backend
   ```

2. **Test in staging environment:**
   ```bash
   curl https://staging.yourapp.com/health
   ```

## 9. Regression Testing

### 9.1 Automated Regression Tests

1. **Run all unit tests:**
   ```bash
   cd backend
   python -m pytest tests/ -v
   ```

2. **Run integration tests:**
   ```bash
   python -m pytest tests/test_integration.py -v
   ```

### 9.2 Manual Regression Tests

1. **Test critical user flows:**
   - User registration → Login → Dashboard access
   - Customer creation → Points award → Tier upgrade
   - Affiliate registration → Referral creation → Commission calculation
   - WhatsApp message sending → Status tracking

2. **Test error scenarios:**
   - Invalid login attempts
   - Insufficient permissions
   - Network failures
   - Database connection issues

## 10. Documentation Testing

### 10.1 API Documentation

1. **Verify OpenAPI documentation:**
   ```bash
   curl http://localhost:8000/docs
   curl http://localhost:8000/redoc
   ```

2. **Test all documented endpoints:**
   - Verify request/response formats
   - Check authentication requirements
   - Validate error responses

### 10.2 Code Documentation

1. **Check docstrings:**
   ```python
   # All functions should have proper docstrings
   def example_function():
       """This function does something important."""
   ```

2. **Verify README accuracy:**
   - Installation instructions work
   - API examples are correct
   - Configuration steps are complete

## 11. Final Production Checklist

### 11.1 Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] External services configured
- [ ] Monitoring and alerting set up
- [ ] Backup procedures tested
- [ ] Security headers configured
- [ ] SSL certificates installed
- [ ] Load testing completed
- [ ] Documentation updated

### 11.2 Post-Deployment Checklist

- [ ] Application starts successfully
- [ ] All health checks pass
- [ ] Database connections working
- [ ] External integrations functional
- [ ] User authentication working
- [ ] File uploads/downloads working
- [ ] Email notifications working
- [ ] WhatsApp messaging working
- [ ] Analytics dashboard accessible

## 12. Troubleshooting

### Common Issues

1. **Database Connection Errors:**
   ```bash
   # Check database logs
   docker-compose logs db

   # Test database connectivity
   psql $DATABASE_URL -c "SELECT 1;"
   ```

2. **Authentication Issues:**
   ```bash
   # Check JWT token generation
   python -c "from app.core.security import create_access_token; print('JWT working')"
   ```

3. **Frontend-Backend Communication:**
   ```bash
   # Check CORS settings
   # Verify API_BASE_URL in frontend
   # Test network connectivity
   ```

### Getting Help

1. **Check application logs:**
   ```bash
   docker-compose logs -f
   ```

2. **Run diagnostic commands:**
   ```bash
   docker-compose exec backend python -c "from app.core.database import engine; print('DB:', engine.url)"
   ```

3. **Check system resources:**
   ```bash
   docker stats
   ```

## 13. Test Data Management

### Creating Test Data

1. **Use seed data script:**
   ```bash
   cd backend
   python -c "from app.utils.seed_data import seed_test_data; seed_test_data()"
   ```

2. **Manual test data creation:**
   ```python
   from app.services.auth_service import AuthService
   from app.services.customer_service import CustomerService

   auth_service = AuthService(db)
   customer_service = CustomerService(db)

   # Create test users and customers
   ```

### Cleaning Up Test Data

1. **Reset database:**
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```

2. **Clean specific tables:**
   ```sql
   TRUNCATE TABLE loyalty_transactions CASCADE;
   TRUNCATE TABLE whatsapp_messages CASCADE;
   ```

---

**🎉 Congratulations!** Your Loyalty & Affiliate Management System is now thoroughly tested and ready for production deployment.

For any issues or questions, please refer to the troubleshooting section or contact the development team.