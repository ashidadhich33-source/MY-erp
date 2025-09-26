# 🚀 Backend Setup Guide

## Prerequisites

- Python 3.11+
- Microsoft SQL Server
- ODBC Driver for SQL Server

## Installation

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Database Setup

### Option 1: Using CLI Commands

1. **Initialize database:**
```bash
python run_cli.py init-db
```

2. **Seed with sample data:**
```bash
python run_cli.py seed-data
```

### Option 2: Using Alembic (Recommended for production)

1. **Create initial migration:**
```bash
python run_cli.py create-migration
```

2. **Upgrade database:**
```bash
python run_cli.py upgrade-db
```

3. **Seed data:**
```bash
python run_cli.py seed-data
```

## Environment Configuration

Update your `.env` file with the following settings:

```env
# Database Settings
DATABASE_URL=mssql+pyodbc://username:password@localhost:1433/loyalty_db?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes

# API Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# WhatsApp Settings (optional)
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token
WHATSAPP_VERIFY_TOKEN=your-whatsapp-verify-token
```

## Available CLI Commands

- `python run_cli.py init-db` - Create all database tables
- `python run_cli.py seed-data` - Populate with sample data
- `python run_cli.py reset-db` - Drop and recreate all tables
- `python run_cli.py create-migration` - Create new Alembic migration
- `python run_cli.py upgrade-db` - Upgrade to latest migration

## Running the API

```bash
# Development mode
python -m uvicorn app.main:app --reload

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Database Schema

The system includes the following main entities:

### Core Models
- **Users** - Admin, customer, and affiliate accounts
- **Customers** - Customer profiles with loyalty information
- **CustomerKids** - Children's information for birthday promotions
- **CustomerTierHistory** - Tier upgrade tracking

### Loyalty System
- **LoyaltyTransactions** - Point transactions and history
- **Rewards** - Reward catalog and management
- **RewardRedemptions** - Redemption tracking
- **TierBenefits** - Benefits for different customer tiers

### Affiliate System
- **Affiliates** - Affiliate profiles and settings
- **CustomerReferrals** - Referral tracking
- **AffiliateCommissions** - Commission calculations
- **PayoutRequests** - Commission payout management

### WhatsApp Integration
- **WhatsAppMessages** - Message history and status
- **NotificationTemplates** - Reusable message templates
- **WhatsAppWebhooks** - Incoming webhook handling

### Birthday Promotions
- **BirthdayPromotions** - Birthday campaign management
- **BirthdaySchedules** - Automated birthday scheduling

## Security

- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Rate limiting ready for implementation

## Development Notes

- All models use SQLAlchemy ORM
- Database migrations managed with Alembic
- Comprehensive logging and error handling
- Ready for horizontal scaling

## Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```