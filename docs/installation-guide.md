# Installation Guide - Authentication System

This comprehensive guide will walk you through the complete installation and setup process for the Authentication System on your local development environment or production server.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [Database Setup](#database-setup)
4. [Backend Installation](#backend-installation)
5. [Frontend Installation](#frontend-installation)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

## System Requirements

### Minimum System Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Ubuntu 22.04 LTS, macOS 12+, Windows 10+ |
| **CPU** | 2 cores, 2.0 GHz |
| **RAM** | 4 GB |
| **Storage** | 20 GB available space |
| **Network** | Stable internet connection |

### Recommended System Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | Ubuntu 22.04 LTS (preferred) |
| **CPU** | 4+ cores, 3.0 GHz |
| **RAM** | 8 GB or more |
| **Storage** | 50 GB SSD |
| **Network** | 100 Mbps connection |

## Prerequisites Installation

### 1. Node.js and npm

The frontend application requires Node.js version 20.19.3 or higher.

#### Ubuntu/Debian
```bash
# Update package index
sudo apt update

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should output v20.19.3 or higher
npm --version   # Should output 10.8.2 or higher
```

#### macOS
```bash
# Using Homebrew
brew install node@20

# Or using Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20.19.3
nvm use 20.19.3
```

#### Windows
1. Download Node.js installer from [nodejs.org](https://nodejs.org/)
2. Run the installer and follow the setup wizard
3. Verify installation in Command Prompt:
   ```cmd
   node --version
   npm --version
   ```

### 2. Python and pip

The backend service requires Python 3.10.12 or higher.

#### Ubuntu/Debian
```bash
# Install Python 3.10 and pip
sudo apt install python3.10 python3.10-venv python3-pip

# Verify installation
python3 --version  # Should output Python 3.10.12 or higher
pip3 --version     # Should output pip 22.0.2 or higher
```

#### macOS
```bash
# Using Homebrew
brew install python@3.10

# Verify installation
python3 --version
pip3 --version
```

#### Windows
1. Download Python installer from [python.org](https://python.org/)
2. Run installer and ensure "Add Python to PATH" is checked
3. Verify installation in Command Prompt:
   ```cmd
   python --version
   pip --version
   ```

### 3. PostgreSQL Database

The system requires PostgreSQL 14 or higher.

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
sudo -u postgres psql -c "SELECT version();"
```

#### macOS
```bash
# Using Homebrew
brew install postgresql@14
brew services start postgresql@14

# Verify installation
psql --version
```

#### Windows
1. Download PostgreSQL installer from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Run installer and follow setup wizard
3. Remember the password you set for the postgres user
4. Verify installation in Command Prompt:
   ```cmd
   psql --version
   ```

### 4. Git Version Control

#### Ubuntu/Debian
```bash
sudo apt install git
git --version  # Should output 2.34.1 or higher
```

#### macOS
```bash
# Git is usually pre-installed, or install via Homebrew
brew install git
```

#### Windows
1. Download Git from [git-scm.com](https://git-scm.com/)
2. Run installer with default settings
3. Verify in Command Prompt: `git --version`

## Database Setup

### 1. Create Database User and Database

First, create a dedicated database user and database for the authentication system.

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run these commands:
CREATE USER auth_user WITH PASSWORD 'auth_password';
CREATE DATABASE auth_system OWNER auth_user;
GRANT ALL PRIVILEGES ON DATABASE auth_system TO auth_user;

# Exit PostgreSQL
\q
```

### 2. Configure PostgreSQL (Optional)

For development, you might want to configure PostgreSQL to allow local connections:

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/14/main/postgresql.conf

# Uncomment and modify:
listen_addresses = 'localhost'

# Edit authentication configuration
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Add or modify this line for local connections:
local   all             auth_user                               md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. Run Database Setup Script

The project includes an automated database setup script:

```bash
# Navigate to project directory
cd auth-system-monorepo

# Make script executable
chmod +x scripts/setup-database.sh

# Run database setup
./scripts/setup-database.sh
```

If you need to customize database connection parameters:

```bash
./scripts/setup-database.sh \
  --host localhost \
  --port 5432 \
  --db-name auth_system \
  --db-user auth_user \
  --db-password auth_password
```

## Backend Installation

### 1. Navigate to Backend Directory

```bash
cd auth-system-monorepo/backend
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Ubuntu/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Update the `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://auth_user:auth_password@localhost:5432/auth_system

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Security Settings
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
```

### 5. Create Superuser (Optional)

```bash
# Run the create superuser script
python scripts/create_superuser.py
```

## Frontend Installation

### 1. Navigate to Frontend Directory

```bash
cd ../frontend  # From backend directory
# Or: cd auth-system-monorepo/frontend
```

### 2. Install Node.js Dependencies

```bash
# Install dependencies
npm install

# Or using yarn if preferred
yarn install
```

### 3. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

Update the `.env` file:

```env
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=10000

# Application Configuration
VITE_APP_NAME=Authentication System
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=Enterprise Authentication System - Admin Dashboard

# Environment
VITE_NODE_ENV=development

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_MOCK_API=false

# UI Configuration
VITE_DEFAULT_THEME=light
VITE_ENABLE_DARK_MODE=true
VITE_SIDEBAR_DEFAULT_OPEN=true
```

## Configuration

### Backend Configuration Details

The backend uses environment variables for configuration. Here are the key settings:

#### Database Settings
- `DATABASE_URL`: Complete PostgreSQL connection string
- `DB_ECHO`: Set to `true` for SQL query logging (development only)

#### JWT Settings
- `JWT_SECRET_KEY`: Secret key for JWT token signing (must be secure in production)
- `JWT_ALGORITHM`: Algorithm for JWT signing (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time

#### Security Settings
- `MAX_LOGIN_ATTEMPTS`: Maximum failed login attempts before lockout
- `LOCKOUT_DURATION_MINUTES`: Duration of account lockout
- `PASSWORD_MIN_LENGTH`: Minimum password length
- `REQUIRE_EMAIL_VERIFICATION`: Whether to require email verification

#### CORS Settings
- `CORS_ORIGINS`: List of allowed origins for CORS

### Frontend Configuration Details

The frontend uses Vite environment variables (prefixed with `VITE_`):

#### API Settings
- `VITE_API_URL`: Backend API base URL
- `VITE_API_TIMEOUT`: Request timeout in milliseconds

#### Application Settings
- `VITE_APP_NAME`: Application name displayed in UI
- `VITE_APP_VERSION`: Application version
- `VITE_NODE_ENV`: Environment (development/production)

#### Feature Flags
- `VITE_ENABLE_DEBUG`: Enable debug mode
- `VITE_ENABLE_MOCK_API`: Use mock API instead of real backend

## Running the Application

### 1. Start Backend Service

```bash
# Navigate to backend directory
cd auth-system-monorepo/backend

# Activate virtual environment
source venv/bin/activate  # On Ubuntu/macOS
# venv\Scripts\activate   # On Windows

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 2. Start Frontend Application

Open a new terminal window:

```bash
# Navigate to frontend directory
cd auth-system-monorepo/frontend

# Start the development server
npm run dev

# Or using yarn
yarn dev
```

The frontend will be available at:
- Application: http://localhost:3000 (or http://localhost:5173 with Vite)

### 3. Using Docker (Alternative)

If you prefer using Docker:

```bash
# Navigate to project root
cd auth-system-monorepo

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Verification

### 1. Check Backend Health

```bash
# Test API health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2025-01-29T..."}
```

### 2. Test Database Connection

```bash
# Test database connection
curl http://localhost:8000/api/v1/health/db

# Expected response:
# {"status": "healthy", "database": "connected"}
```

### 3. Test Authentication

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123456"}'

# Expected response should include access_token and refresh_token
```

### 4. Access Frontend Application

1. Open browser and navigate to http://localhost:3000
2. You should see the login page
3. Try logging in with default credentials:
   - Email: `admin@example.com`
   - Password: `admin123456`

### 5. Verify Default Accounts

The system comes with these default accounts:

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| SuperAdmin | admin@example.com | admin123456 | Full system access |
| Admin1 | admin1@example.com | admin123456 | User management |
| Admin2 | admin2@example.com | admin123456 | User management |
| Admin3 | admin3@example.com | admin123456 | User management |
| User | john.doe@example.com | user123456 | Limited access |

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues

**Problem**: Cannot connect to PostgreSQL database

**Solutions**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Check if database exists
sudo -u postgres psql -l | grep auth_system

# Check user permissions
sudo -u postgres psql -c "\du auth_user"
```

#### 2. Python Dependencies Issues

**Problem**: Error installing Python packages

**Solutions**:
```bash
# Update pip
pip install --upgrade pip

# Install system dependencies (Ubuntu)
sudo apt install python3-dev libpq-dev

# Clear pip cache
pip cache purge

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### 3. Node.js Dependencies Issues

**Problem**: npm install fails

**Solutions**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install

# Or try with legacy peer deps
npm install --legacy-peer-deps
```

#### 4. Port Already in Use

**Problem**: Port 8000 or 3000 already in use

**Solutions**:
```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :3000

# Kill process (replace PID with actual process ID)
kill -9 PID

# Or use different ports
uvicorn app.main:app --port 8001
npm run dev -- --port 3001
```

#### 5. CORS Issues

**Problem**: Frontend cannot connect to backend

**Solutions**:
1. Check CORS_ORIGINS in backend .env file
2. Ensure frontend URL is included in CORS_ORIGINS
3. Restart backend after changing CORS settings

#### 6. JWT Token Issues

**Problem**: Authentication not working

**Solutions**:
1. Check JWT_SECRET_KEY in backend .env
2. Ensure JWT_SECRET_KEY is not empty
3. Clear browser local storage
4. Check browser console for errors

### Log Files and Debugging

#### Backend Logs
```bash
# View backend logs
cd backend
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
# Then run your application
"
```

#### Frontend Logs
- Open browser Developer Tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API request/response issues

#### Database Logs
```bash
# View PostgreSQL logs (Ubuntu)
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Or check systemd logs
sudo journalctl -u postgresql -f
```

## Production Deployment

### Security Considerations

Before deploying to production, ensure you:

1. **Change Default Passwords**
   ```bash
   # Update all default user passwords
   # Use the admin interface or database directly
   ```

2. **Update JWT Secret**
   ```bash
   # Generate a secure JWT secret
   python -c "
   import secrets
   print(secrets.token_urlsafe(32))
   "
   ```

3. **Configure HTTPS**
   - Use SSL certificates
   - Update CORS_ORIGINS to use HTTPS URLs
   - Set secure cookie flags

4. **Database Security**
   - Use strong database passwords
   - Enable SSL for database connections
   - Restrict database access to application servers only

5. **Environment Variables**
   - Never commit .env files to version control
   - Use environment-specific configurations
   - Consider using secret management services

### Production Environment Setup

#### 1. System Dependencies
```bash
# Install production dependencies
sudo apt update
sudo apt install nginx postgresql redis-server supervisor

# Configure firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

#### 2. Database Configuration
```bash
# Create production database
sudo -u postgres createdb auth_system_prod
sudo -u postgres createuser auth_prod_user

# Run migrations
cd auth-system-monorepo
./scripts/setup-database.sh \
  --db-name auth_system_prod \
  --db-user auth_prod_user \
  --skip-seeds  # Don't load test data in production
```

#### 3. Backend Deployment
```bash
# Install production WSGI server
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/auth-backend.service
```

Service file content:
```ini
[Unit]
Description=Authentication System Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/auth-system-monorepo/backend
Environment=PATH=/path/to/auth-system-monorepo/backend/venv/bin
ExecStart=/path/to/auth-system-monorepo/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. Frontend Deployment
```bash
# Build frontend for production
cd frontend
npm run build

# Copy build files to web server directory
sudo cp -r dist/* /var/www/html/
```

#### 5. Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/auth-system
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/auth-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Monitoring and Maintenance

#### 1. Log Rotation
```bash
# Configure log rotation
sudo nano /etc/logrotate.d/auth-system
```

#### 2. Backup Strategy
```bash
# Create backup script
sudo nano /usr/local/bin/backup-auth-system.sh
```

#### 3. Health Monitoring
- Set up monitoring for API endpoints
- Monitor database performance
- Set up alerts for system issues

### Performance Optimization

#### 1. Database Optimization
- Configure PostgreSQL for production workload
- Set up connection pooling
- Optimize queries and add indexes

#### 2. Caching
- Implement Redis for session storage
- Cache frequently accessed data
- Use CDN for static assets

#### 3. Application Optimization
- Use production WSGI server (Gunicorn)
- Configure proper worker processes
- Enable gzip compression

---

This completes the comprehensive installation guide. For additional help, refer to the [troubleshooting section](#troubleshooting) or contact support.

