# Loyalty & Affiliate Management System

A comprehensive loyalty program and affiliate management system with WhatsApp integration and Logic ERP connectivity, built with FastAPI, React, PostgreSQL (loyalty system), and MSSQL (Logic ERP data source).

## 🚀 Features

### Core Features
- **Customer Management**: Complete customer lifecycle management with tier progression
- **Loyalty Program**: Points-based rewards system with customizable tiers
- **Affiliate System**: Referral tracking, commission management, and performance analytics
- **WhatsApp Integration**: Automated messaging, templates, and delivery tracking
- **Logic ERP Integration**: Seamless data synchronization from Logic ERP MSSQL (Customers, SalesOrders, Products) to PostgreSQL loyalty system
- **Analytics & Reporting**: Comprehensive dashboards and custom report generation

### Technical Features
- **Real-time Sync**: Automatic data synchronization between systems
- **API-First Architecture**: RESTful APIs with comprehensive documentation
- **Local Development**: Direct PostgreSQL and MSSQL integration for local development
- **Security**: JWT authentication, role-based access control, data encryption
- **Testing**: Comprehensive test suite with unit and integration tests

## 📋 Prerequisites

- **Python 3.11+** (for backend development)
- **Node.js 18+** (for frontend development)
- **PostgreSQL 15+** (for loyalty system database - installed locally)
- **Microsoft SQL Server** (for Logic ERP data source - running locally)
- **Git** (for version control)

## 🛠️ Quick Start

### Local Development Setup

1. **Install PostgreSQL locally**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib

   # Create database and user
   sudo -u postgres psql
   CREATE DATABASE loyalty_db;
   CREATE USER loyalty_user WITH PASSWORD 'loyalty_password';
   GRANT ALL PRIVILEGES ON DATABASE loyalty_db TO loyalty_user;
   \q
   ```

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd loyalty-affiliate-system
   ```

3. **Set up environment variables**
   ```bash
   # Frontend environment is already created
   # Backend .env.example should be copied and configured
   cp backend/.env.example backend/.env
   # Edit backend/.env with your local database settings
   ```

4. **Install Python dependencies**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   ```

5. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

6. **Run database migrations**
   ```bash
   cd backend
   source venv/bin/activate
   alembic upgrade head
   cd ..
   ```

7. **Start the backend server**
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

8. **Start the frontend development server**
   ```bash
   # New terminal
   cd frontend
   npm run dev
   ```

9. **Access the applications**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## 🧪 Testing

### Run Tests

```bash
# Activate virtual environment and run tests
cd backend
source venv/bin/activate
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
- **Integration Tests**: Component interaction testing with real databases
- **Performance Tests**: Load and stress testing
- **Security Tests**: Authentication and authorization testing

### Test Database Setup

For running tests, you may want to use a separate test database:

```bash
# Create test database
sudo -u postgres psql
CREATE DATABASE loyalty_test_db;
CREATE USER loyalty_test_user WITH PASSWORD 'loyalty_test_password';
GRANT ALL PRIVILEGES ON DATABASE loyalty_test_db TO loyalty_test_user;
\q

# Update .env for testing
DATABASE_URL=postgresql://loyalty_test_user:loyalty_test_password@localhost:5432/loyalty_test_db
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `backend/.env`:

```bash
# Database (Local PostgreSQL)
DATABASE_URL=postgresql://loyalty_user:loyalty_password@localhost:5432/loyalty_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development

# Logic ERP Integration (Local MSSQL)
ERP_HOST=localhost
ERP_PORT=1433
ERP_DATABASE=master
ERP_USERNAME=sa
ERP_PASSWORD=ATPL@123
ERP_DRIVER=ODBC Driver 17 for SQL Server

# WhatsApp Integration (optional)
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
WHATSAPP_VERIFY_TOKEN=your-verify-token

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourcompany.com

# Redis (optional - for caching)
REDIS_URL=redis://localhost:6379
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

## 🛠️ Development

### Project Structure

```
loyalty-affiliate-system/
├── backend/                 # FastAPI backend (PostgreSQL)
│   ├── app/                # Main application with Logic ERP integration
│   ├── tests/              # Test files
│   ├── requirements.txt    # Python dependencies
│   ├── alembic/            # Database migrations
│   └── venv/               # Python virtual environment
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── .env               # Frontend environment variables
└── updated-project-instructions.md
```

### Development Workflow

1. **Backend Development**:
   - Edit Python files in `backend/app/`
   - Add new API endpoints in `backend/app/api/v1/endpoints/`
   - Update database models in `backend/app/models/`
   - Add business logic in `backend/app/services/`

2. **Frontend Development**:
   - Edit React components in `frontend/src/components/`
   - Add new pages in `frontend/src/pages/`
   - Update API calls in `frontend/src/services/api.js`
   - Modify state management in `frontend/src/store/`

3. **Testing**:
   - Add unit tests in `backend/tests/`
   - Run tests: `cd backend && source venv/bin/activate && pytest`
   - Test API endpoints using the documentation at `/docs`

4. **Database Changes**:
   - Create new migrations: `cd backend && source venv/bin/activate && alembic revision --autogenerate -m "description"`
   - Apply migrations: `alembic upgrade head`

### Code Style

- **Python**: PEP 8 with Black formatting
- **JavaScript**: ESLint with Airbnb style guide
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Docstrings for all functions

### Adding New Features

1. **Backend**: Add new endpoints in `app/api/v1/endpoints/`
2. **Frontend**: Create new components in `src/components/`
3. **Tests**: Add tests in `tests/` directory
4. **Documentation**: Update API docs and README

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL configuration in `backend/.env`
   - Ensure PostgreSQL service is running: `sudo systemctl status postgresql`
   - Verify database credentials and database exists

2. **ERP Integration Issues**
   - Verify ERP_HOST is set to `localhost` in `backend/.env`
   - Check Logic ERP MSSQL is running on port 1433
   - Ensure ERP credentials are correct (default: sa/ATPL@123)

3. **WhatsApp API Errors**
   - Validate WHATSAPP_ACCESS_TOKEN in `backend/.env`
   - Check API quotas and limits
   - Verify phone number format

4. **Port Already in Use**
   - Backend: Change port in uvicorn command or kill process using port 8000
   - Frontend: Use `npm run dev -- --port 3001` to use different port

5. **Python Dependencies Issues**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Reinstall requirements: `pip install -r requirements.txt`
   - Check Python version: `python --version` (should be 3.11+)

6. **Node.js Dependencies Issues**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules: `rm -rf node_modules package-lock.json`
   - Reinstall: `npm install`

### Support and Logs

- **Backend Logs**: Check console output when running uvicorn server
- **Database Logs**: Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-15-main.log`
- **API Documentation**: Review API docs at `http://localhost:8000/docs`
- **Health Check**: Test system health at `http://localhost:8000/health`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and test them thoroughly
4. Add tests for new functionality
5. Run the test suite: `cd backend && source venv/bin/activate && pytest`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write comprehensive tests for new features
- Update documentation for API changes
- Use meaningful commit messages
- Ensure all tests pass before submitting PR

## 📞 Contact & Support

For support and questions:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Documentation**: Check this README and the `/docs` endpoint
- **Issues**: Report bugs and request features on GitHub

### Getting Help

1. **Check the logs**: Review console output and database logs
2. **API Documentation**: Use the interactive docs at `/docs`
3. **Health Check**: Verify system status at `/health/detailed`
4. **Test Environment**: Create a separate test database for debugging

---

## 🎉 **Getting Started**

Your Loyalty & Affiliate Management System is now ready for local development!

### **Next Steps:**

1. **Start Development**: Follow the setup instructions above
2. **Explore Features**: Check out the API documentation at `/docs`
3. **Customize**: Modify the system to fit your business needs
4. **Test Thoroughly**: Use the comprehensive test suite
5. **Deploy**: When ready, consider containerized deployment for production

**Happy coding! 🚀**