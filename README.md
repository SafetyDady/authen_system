# Authentication System - Enterprise Monorepo

A comprehensive, enterprise-grade authentication system built with modern technologies and designed for scalability, security, and ease of use.

## 🚀 Overview

This Authentication System provides a complete solution for user management, role-based access control, and secure authentication for enterprise applications. Built as a monorepo, it includes both backend API services and frontend dashboard applications.

### Key Features

- **🔐 Secure Authentication**: JWT-based authentication with refresh tokens
- **👥 Role-Based Access Control**: Multi-level user roles (SuperAdmin, Admin1-3, User)
- **📊 Enterprise Dashboard**: Modern, responsive admin interface
- **🔍 Audit Logging**: Comprehensive activity tracking and monitoring
- **🛡️ Security Features**: Account lockout, password policies, session management
- **📱 Responsive Design**: Mobile-first, accessible user interface
- **🎨 Modern UI/UX**: Glass morphism design with smooth animations
- **🔧 Developer Friendly**: Well-documented APIs and comprehensive setup guides

## 🏗️ Architecture

```
auth-system-monorepo/
├── backend/                 # FastAPI backend service
├── frontend/               # React + TypeScript frontend
├── database/               # PostgreSQL schema and migrations
├── docs/                   # Documentation and specifications
├── scripts/                # Setup and utility scripts
├── ui-examples/           # UI prototypes and examples
└── docker/                # Docker configuration files
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.116.1
- **Language**: Python 3.10.12
- **Database**: PostgreSQL with SQLAlchemy 2.0.41
- **Authentication**: JWT with PyJWT 2.10.1
- **Password Hashing**: Bcrypt 4.3.0
- **Server**: Uvicorn 0.35.0

### Frontend
- **Framework**: React 19.1.0 with TypeScript 5.8.3
- **Build Tool**: Vite 7.0.4
- **UI Library**: Material-UI 7.2.0 + TailwindCSS 4.1.11
- **State Management**: Zustand 5.0.6
- **Data Fetching**: React Query 5.83.0 + Axios 1.11.0
- **Routing**: React Router 7.7.1

### Database
- **Primary**: PostgreSQL 14+
- **Features**: Row Level Security, Audit Triggers, Views
- **Migration**: Custom SQL migration system

## 🚀 Quick Start

### Prerequisites

- Node.js v20.19.3+
- Python 3.10.12+
- PostgreSQL 14+
- Git 2.34.1+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd auth-system-monorepo
   ```

2. **Setup Database**
   ```bash
   # Configure database connection in .env files
   ./scripts/setup-database.sh
   ```

3. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

6. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 👤 Default Accounts

The system comes with pre-configured accounts for testing:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| SuperAdmin | admin@example.com | admin123456 | Full system access |
| Admin1 | admin1@example.com | admin123456 | User management |
| Admin2 | admin2@example.com | admin123456 | User management |
| Admin3 | admin3@example.com | admin123456 | User management |
| User | john.doe@example.com | user123456 | Regular user |

> ⚠️ **Security Warning**: Change all default passwords before deploying to production!

## 🎨 UI Features

### Multi-Section Dashboard
- **URL-based Navigation**: Clean URLs for each section
- **Role-based Menus**: Dynamic navigation based on user permissions
- **Responsive Design**: Works seamlessly on all devices
- **Glass Morphism**: Modern, professional design language

### Authentication Pages
- **Enterprise Login**: Professional login with security indicators
- **Password Policies**: Configurable password requirements
- **Account Lockout**: Automatic protection against brute force attacks
- **Session Management**: Secure token handling with auto-refresh

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://auth_user:auth_password@localhost:5432/auth_system

# JWT Settings
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Security
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

#### Frontend (.env)
```env
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=10000

# Application
VITE_APP_NAME=Authentication System
VITE_APP_VERSION=1.0.0
```

## 📚 Documentation

- [Installation Guide](docs/installation-guide.md) - Detailed setup instructions
- [API Documentation](docs/api-documentation.md) - Complete API reference
- [User Manual](docs/user-manual.md) - End-user guide
- [Developer Guide](docs/developer-guide.md) - Development guidelines
- [Deployment Guide](docs/deployment-guide.md) - Production deployment
- [UI Specification](docs/ui-specification.md) - Design system and components
- [Technical Specification](docs/technical-specification.md) - Architecture details

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with secure token handling
- Role-based access control with fine-grained permissions
- Session management with automatic token refresh
- Account lockout protection against brute force attacks

### Data Protection
- Row Level Security (RLS) in PostgreSQL
- Password hashing with bcrypt
- Secure session cookies
- CSRF protection
- Input validation and sanitization

### Audit & Monitoring
- Comprehensive audit logging
- Failed login attempt tracking
- User activity monitoring
- System health indicators

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Testing
```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Testing
```bash
# Run full test suite
./scripts/run-tests.sh
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment
1. Setup production database
2. Configure environment variables
3. Build frontend assets
4. Deploy backend service
5. Configure reverse proxy (nginx/apache)

See [Deployment Guide](docs/deployment-guide.md) for detailed instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Create an issue on GitHub
- **Email**: support@example.com

## 🎯 Roadmap

### Version 1.1.0
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 integration (Google, Microsoft)
- [ ] Advanced reporting dashboard
- [ ] Email notifications system

### Version 1.2.0
- [ ] Mobile application
- [ ] API rate limiting
- [ ] Advanced audit analytics
- [ ] Multi-tenant support

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: 10 Mbps

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: 100 Mbps+

## 🔧 Development

### Project Structure
```
auth-system-monorepo/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── db/            # Database models
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── scripts/           # Utility scripts
│   └── tests/             # Test files
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── store/         # State management
│   │   ├── lib/           # Utilities
│   │   └── styles/        # CSS files
│   └── public/            # Static assets
└── database/
    ├── migrations/        # Database migrations
    ├── seeds/             # Seed data
    └── schema.sql         # Complete schema
```

### Code Quality
- **Backend**: Black, isort, flake8, mypy
- **Frontend**: ESLint, Prettier, TypeScript
- **Testing**: pytest, Jest, React Testing Library
- **Documentation**: Sphinx, Storybook

---

**Built with ❤️ by Manus AI**

For more information, visit our [documentation](docs/) or contact our support team.

