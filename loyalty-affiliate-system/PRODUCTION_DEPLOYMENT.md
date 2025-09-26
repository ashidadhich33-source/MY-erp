# Production Deployment Guide

This comprehensive guide covers everything you need to know to deploy the Loyalty & Affiliate Management System to production.

## 🎯 Production Readiness Checklist

### ✅ Completed Tasks

- [x] **Database Configuration**: Migrated from MSSQL/MySQL to PostgreSQL
- [x] **Environment Files**: Created comprehensive .env.example files
- [x] **API Compatibility**: Fixed frontend-backend endpoint mismatches
- [x] **Service Layer**: Implemented all required service classes
- [x] **Database Schema**: Updated to PostgreSQL syntax
- [x] **Docker Configuration**: Standardized on PostgreSQL across all services
- [x] **Test Suite**: Created comprehensive integration and production tests
- [x] **CORS Configuration**: Set up production-ready CORS with security
- [x] **Logging & Monitoring**: Implemented comprehensive logging system
- [x] **Health Checks**: Added detailed health monitoring endpoints

## 🚀 Quick Deployment

### 1. Environment Setup

```bash
# Copy and configure environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit environment files with your production values
nano backend/.env
nano frontend/.env
```

### 2. Production Deployment

```bash
# Run production deployment
./deploy.sh deploy

# Or manually:
docker-compose -f docker-compose.yml up -d
docker-compose exec backend alembic upgrade head
```

### 3. Verify Deployment

```bash
# Run health checks
./deploy.sh test

# Check application logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📋 Detailed Deployment Steps

### Step 1: Pre-Deployment Preparation

#### 1.1 System Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+ (for development)
- **Node.js**: 18+ (for development)
- **PostgreSQL**: 15+ (production database)

#### 1.2 Environment Configuration

**Backend Environment Variables (.env):**
```bash
# Database
DATABASE_URL=postgresql://loyalty_user:your_secure_password@db:5432/loyalty_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (comma-separated domains)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# WhatsApp Integration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# ERP Integration (optional)
ERP_HOST=your-erp-host.com
ERP_API_KEY=your-erp-api-key

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourcompany.com

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend Environment Variables (.env):**
```bash
REACT_APP_API_BASE_URL=https://your-backend-domain.com/api/v1
REACT_APP_ENVIRONMENT=production
```

#### 1.3 Database Setup

1. **Initialize Database:**
   ```bash
   docker-compose up -d db
   sleep 30  # Wait for database to be ready
   ```

2. **Run Migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. **Verify Database:**
   ```bash
   docker-compose exec db psql -U loyalty_user -d loyalty_db -c "\dt"
   ```

### Step 2: Application Deployment

#### 2.1 Docker Deployment

```bash
# Build and deploy all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 2.2 Health Verification

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Frontend health check
curl http://localhost:3000
```

### Step 3: Post-Deployment Configuration

#### 3.1 SSL Configuration (Nginx)

Update nginx configuration in `docker-compose.yml` or create SSL certificates:

```bash
# Generate SSL certificates (if not using Let's Encrypt)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/private.key \
  -out nginx/ssl/certificate.crt
```

#### 3.2 Monitoring Setup

Access monitoring dashboards:
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

#### 3.3 External Service Configuration

**WhatsApp Business API:**
1. Set up WhatsApp Business Account
2. Generate access token
3. Configure webhook URL: `https://yourdomain.com/api/v1/whatsapp/webhook`

**Logic ERP Integration:**
1. Ensure Logic ERP MSSQL is accessible (username: sa, password: ATPL@123)
2. Verify the following tables exist:
   - Customers (CustomerID, CustomerName, EmailAddress, PhoneNumber, Status)
   - SalesOrders (OrderID, CustomerID, OrderDate, TotalAmount, PaymentStatus)
   - Products (ProductID, ProductName)
3. Test data synchronization from MSSQL to PostgreSQL

## 🧪 Production Testing

### Automated Testing

```bash
# Run production readiness tests
./run_tests.sh

# Run specific tests
cd backend && python -m pytest tests/test_integration.py -v
```

### Manual Testing Checklist

#### 1. Authentication Flow
- [ ] User registration works
- [ ] User login works
- [ ] Password reset works
- [ ] JWT token refresh works
- [ ] Logout works

#### 2. Customer Management
- [ ] Customer creation works
- [ ] Customer data retrieval works
- [ ] Customer updates work
- [ ] Customer tier progression works

#### 3. Loyalty Program
- [ ] Points awarding works
- [ ] Points redemption works
- [ ] Transaction history works
- [ ] Tier upgrades trigger correctly

#### 4. External Integrations
- [ ] WhatsApp messaging works
- [ ] ERP data sync works
- [ ] Email notifications work

#### 5. Performance Testing
- [ ] API response times are acceptable
- [ ] Database queries are optimized
- [ ] Application handles concurrent users

## 🔍 Monitoring & Health Checks

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with database and external services
curl http://localhost:8000/health/detailed
```

### Log Monitoring

```bash
# Application logs
docker-compose logs -f backend

# Access logs
docker-compose logs -f nginx

# Error logs
tail -f backend/logs/error.log
```

### System Monitoring

```bash
# Container resource usage
docker stats

# Service health
docker-compose ps

# Database performance
docker-compose exec db psql -U loyalty_user -d loyalty_db -c \
  "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database logs
docker-compose logs db

# Test database connectivity
docker-compose exec db pg_isready -U loyalty_user -d loyalty_db

# Reset database
docker-compose down
docker volume rm loyalty-affiliate-system_postgres_data
docker-compose up -d db
```

#### 2. Authentication Issues
```bash
# Check JWT configuration
python -c "from app.core.security import create_access_token; print('JWT working')"

# Verify user credentials
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

#### 3. CORS Issues
```bash
# Check CORS configuration in backend logs
# Verify BACKEND_CORS_ORIGINS in environment file
# Test from different domains
```

#### 4. External Service Issues
```bash
# Check WhatsApp API connectivity
curl -X GET "https://graph.facebook.com/v17.0/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check ERP connectivity
curl -X GET "https://your-erp-host.com/health"
```

### Emergency Procedures

#### Quick Service Restart
```bash
docker-compose restart
```

#### Database Backup & Restore
```bash
# Create backup
docker-compose exec db pg_dump -U loyalty_user loyalty_db > backup.sql

# Restore from backup
docker-compose exec -T db psql -U loyalty_user -d loyalty_db < backup.sql
```

#### Rollback Deployment
```bash
./deploy.sh rollback
```

## 📊 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_loyalty_transactions_customer_created
ON loyalty_transactions(customer_id, created_at);

CREATE INDEX CONCURRENTLY idx_customers_tier_status
ON customers(tier, status);

CREATE INDEX CONCURRENTLY idx_whatsapp_messages_status
ON whatsapp_messages(status, created_at);
```

### Application Optimization
- Enable Redis caching for session management
- Configure database connection pooling
- Set up CDN for static assets
- Implement rate limiting for API endpoints

### Monitoring & Alerts
- Set up alerts for high response times
- Monitor database connection pool usage
- Track error rates and 500 responses
- Monitor external API call failures

## 🔒 Security Considerations

### Production Security Checklist
- [ ] SSL certificates are properly configured
- [ ] Environment variables contain no secrets
- [ ] Database passwords are strong and unique
- [ ] API keys are stored securely
- [ ] CORS is restricted to specific domains
- [ ] Rate limiting is enabled
- [ ] Input validation is implemented
- [ ] SQL injection protection is in place
- [ ] XSS protection is enabled
- [ ] CSRF protection is configured

### Security Headers
The application includes these security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- [ ] Monitor application logs daily
- [ ] Check system resource usage
- [ ] Update SSL certificates before expiry
- [ ] Review and optimize slow database queries
- [ ] Update dependencies regularly
- [ ] Test backup and restore procedures monthly
- [ ] Review security logs for suspicious activity

### Backup Strategy
- **Database**: Daily automated backups
- **Application**: Version control + container images
- **Configuration**: Environment files in secure storage
- **Logs**: Centralized log aggregation

### Scaling Considerations
- **Horizontal Scaling**: Use multiple backend instances
- **Database Scaling**: Implement read replicas
- **Caching**: Redis cluster for high availability
- **Load Balancing**: Nginx or cloud load balancer

## 🚀 Advanced Deployment Options

### Kubernetes Deployment
```yaml
# Example K8s deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loyalty-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: loyalty-backend
  template:
    metadata:
      labels:
        app: loyalty-backend
    spec:
      containers:
      - name: backend
        image: your-registry/loyalty-backend:latest
        ports:
        - containerPort: 8000
```

### Cloud Deployment (AWS/GCP/Azure)
1. Use managed PostgreSQL (RDS/Aurora/Cloud SQL)
2. Implement auto-scaling groups
3. Set up load balancers
4. Configure monitoring with CloudWatch/Stackdriver
5. Use managed Redis (ElastiCache/Memorystore)

## 🎉 Deployment Complete!

Congratulations! Your Loyalty & Affiliate Management System is now deployed to production.

### What's Next?
1. Monitor system performance
2. Set up alerting for critical issues
3. Train your team on system usage
4. Plan for regular updates and maintenance
5. Monitor user feedback and system usage

### Getting Help
- **Documentation**: Check the TESTING_GUIDE.md for troubleshooting
- **Logs**: Review application and system logs
- **Health Checks**: Use the /health/detailed endpoint
- **Community**: Check GitHub issues for common problems

---

**🎯 Success!** Your production deployment is complete and ready for users!