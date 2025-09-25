# Loyalty & Affiliate Management System

A comprehensive loyalty and affiliate management system built with Python FastAPI backend and React.js frontend.

## 🚀 Features

- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Frontend**: React.js with JavaScript, Tailwind CSS, and Redux Toolkit
- **Authentication**: JWT-based authentication system
- **Database**: Microsoft SQL Server integration ready
- **WhatsApp Integration**: Ready for WhatsApp Business API
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **State Management**: Redux Toolkit for complex state management

## 📋 Phase 1 Complete ✅

- ✅ Project structure setup
- ✅ FastAPI backend with basic endpoints
- ✅ React.js frontend with Vite
- ✅ Tailwind CSS styling
- ✅ Redux Toolkit setup
- ✅ Basic authentication UI
- ✅ CORS configuration
- ✅ Development servers running

## 🛠 Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PyODBC** - Microsoft SQL Server connector
- **JWT** - JSON Web Tokens for authentication
- **Bcrypt** - Password hashing

### Frontend
- **React 18** - JavaScript library for building user interfaces
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **Redux Toolkit** - State management
- **React Router** - Client-side routing
- **React Hook Form** - Form management
- **Axios** - HTTP client
- **Chart.js** - Data visualization
- **Lucide React** - Icon library

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** and **npm** (for frontend)
- **Python 3.11+** and **pip** (for backend)
- **Microsoft SQL Server** (for database)

### Installation & Setup

1. **Clone and navigate to the project directory:**
   ```bash
   cd loyalty-affiliate-system
   ```

2. **Backend Setup:**
   ```bash
   cd backend
   python3 -m pip install --break-system-packages -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend server:**
   ```bash
   cd backend
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the frontend server:**
   ```bash
   cd ../frontend
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
loyalty-affiliate-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── main.py
│   │   └── models/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── auth/
│   │   │   └── layouts/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   └── utils/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── docs/
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory based on `.env.example`:

```env
# Database Configuration
DATABASE_URL=DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=loyalty_system;UID=sa;PWD=your_password

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WhatsApp Configuration
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Application Settings
APP_NAME=Loyalty & Affiliate Management System
DEBUG=True
API_V1_STR=/api/v1
```

## 📱 Available Pages

- **Login Page** (`/login`) - User authentication
- **Register Page** (`/register`) - User registration
- **Dashboard** (`/`) - Main dashboard with overview
- **API Documentation** (`/docs`) - Swagger UI for API testing

## 🔄 Next Steps

Phase 1 is complete! Ready to proceed with:

- **Phase 2**: Authentication & User Management
- **Phase 3**: Database Models & Core Tables
- **Phase 4**: Loyalty System Core
- **Phase 5**: Affiliate Management System
- **Phase 6**: WhatsApp Integration
- **Phase 7**: Customer & Kids Management
- **Phase 8**: Analytics & Reporting
- **Phase 9**: Logic ERP Integration Preparation
- **Phase 10**: Testing & Deployment

## 🤝 Contributing

1. Follow the project structure and coding standards
2. Use meaningful commit messages
3. Test your changes thoroughly
4. Update documentation as needed

## 📄 License

This project is proprietary software developed for loyalty and affiliate management.

---

**Status**: Phase 1 Complete ✅
**Next**: Ready for Phase 2 (Authentication & User Management)

Comment "PHASE 1 DONE" to proceed to the next phase!