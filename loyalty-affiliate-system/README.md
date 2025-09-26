# 🚀 Loyalty & Affiliate Management System

A comprehensive loyalty and affiliate management system built with Python FastAPI backend and React.js frontend, featuring WhatsApp integration and Logic ERP integration capabilities.

## 🏗️ Architecture

- **Backend**: Python 3.11+ + FastAPI + SQLAlchemy + MSSQL
- **Frontend**: React.js + JavaScript + Tailwind CSS + Vite
- **Database**: Microsoft SQL Server
- **WhatsApp**: Direct API integration with webhook support
- **State Management**: Redux Toolkit

## 📦 Project Structure

```
loyalty-affiliate-system/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Main application
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
├── frontend/               # React.js frontend
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── docs/                   # Documentation
└── docker-compose.yml      # Docker configuration
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Features

### Core Features
- ✅ Loyalty points management with tier system
- ✅ Affiliate registration and commission tracking
- ✅ Customer and kids management
- ✅ WhatsApp integration for notifications
- ✅ Analytics and reporting dashboard
- ✅ Logic ERP integration ready

### Advanced Features
- Role-based access control (Admin, Customer, Affiliate)
- Real-time WhatsApp notifications
- Birthday promotions automation
- Referral tracking with attribution
- Comprehensive analytics with Chart.js
- Responsive design with Tailwind CSS

## 📱 API Documentation

Once the backend is running, visit: `http://localhost:8000/docs` for interactive API documentation.

## 🛠️ Development

### Backend Development
- Uses FastAPI with automatic OpenAPI documentation
- SQLAlchemy ORM for database operations
- Alembic for database migrations
- JWT authentication with role-based access

### Frontend Development
- React.js with modern hooks
- Redux Toolkit for state management
- Tailwind CSS for styling
- Vite for fast development and building
- React Hook Form for form validation

## 🔒 Security

- JWT token-based authentication
- Password hashing with bcrypt
- Rate limiting on API endpoints
- Input validation and sanitization
- CORS configuration for cross-origin requests

## 📊 Database Schema

The system uses Microsoft SQL Server with the following main entities:
- Users (customers, affiliates, admins)
- Loyalty points and transactions
- Customer tiers and benefits
- Rewards catalog
- Affiliate commissions and payouts
- Kids information for birthday promotions
- WhatsApp message logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is private and proprietary.

## 🆘 Support

For support and questions, please contact the development team.

---

Built with ❤️ using FastAPI + React.js + Tailwind CSS