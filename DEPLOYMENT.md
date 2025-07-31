# Deployment Guide - Authentication System

This guide provides step-by-step instructions for deploying the Authentication System to various environments.

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd auth-system-monorepo

# Deploy with Docker Compose
./scripts/deploy.sh --docker

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd auth-system-monorepo

# Setup database
./scripts/setup-database.sh

# Deploy manually
./scripts/deploy.sh --environment development

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Deployment Options

### 1. Docker Compose Deployment

**Advantages:**
- Complete environment isolation
- Easy to set up and tear down
- Includes all services (database, cache, web server)
- Production-ready configuration

**Requirements:**
- Docker 20.10+
- Docker Compose 2.0+

**Commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose down && docker-compose up -d --build
```

### 2. Manual Deployment

**Advantages:**
- More control over individual components
- Better for development and debugging
- Can use existing database/services

**Requirements:**
- Node.js 20.19.3+
- Python 3.10.12+
- PostgreSQL 14+

**Commands:**
```bash
# Development deployment
./scripts/deploy.sh --environment development

# Production deployment
./scripts/deploy.sh --environment production --backup-db
```

## Environment Configuration

### Development Environment

Create `.env.development`:
```env
# Database
DATABASE_URL=postgresql://auth_user:auth_password@localhost:5432/auth_system

# JWT Settings
JWT_SECRET_KEY=dev-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Security
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Application
DEBUG=true
LOG_LEVEL=DEBUG
```

### Production Environment

Create `.env.production`:
```env
# Database
DATABASE_URL=postgresql://prod_user:secure_password@db.example.com:5432/auth_system_prod

# JWT Settings (CHANGE THESE!)
JWT_SECRET_KEY=your-super-secure-production-jwt-secret-key-32-chars-minimum
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
MAX_LOGIN_ATTEMPTS=3
LOCKOUT_DURATION_MINUTES=60

# CORS
CORS_ORIGINS=["https://your-domain.com"]

# Application
DEBUG=false
LOG_LEVEL=INFO
```

## Default User Accounts

The system comes with pre-configured accounts:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| SuperAdmin | admin@example.com | admin123456 | Full system access |
| Admin1 | admin1@example.com | admin123456 | User management |
| Admin2 | admin2@example.com | admin123456 | User management |
| Admin3 | admin3@example.com | admin123456 | User management |
| User | john.doe@example.com | user123456 | Regular user |

> ⚠️ **IMPORTANT**: Change all default passwords before production deployment!

## Production Deployment

### Prerequisites

1. **Server Requirements:**
   - Ubuntu 22.04 LTS or similar
   - 4GB RAM minimum (8GB recommended)
   - 50GB storage minimum
   - SSL certificate for HTTPS

2. **Domain Setup:**
   - Domain name pointing to your server
   - SSL certificate (Let's Encrypt recommended)

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx postgresql redis-server supervisor

# Configure firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Step 2: Database Setup

```bash
# Create production database
sudo -u postgres createdb auth_system_prod
sudo -u postgres createuser auth_prod_user

# Set password and permissions
sudo -u postgres psql -c "ALTER USER auth_prod_user PASSWORD 'secure_production_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE auth_system_prod TO auth_prod_user;"

# Run migrations
./scripts/setup-database.sh \
  --db-name auth_system_prod \
  --db-user auth_prod_user \
  --db-password secure_production_password \
  --skip-seeds
```

### Step 3: Application Deployment

```bash
# Clone repository
git clone <repository-url> /opt/auth-system
cd /opt/auth-system

# Set up environment
cp .env.example .env.production
# Edit .env.production with production values

# Deploy application
./scripts/deploy.sh --environment production --backup-db
```

### Step 4: Web Server Configuration

Create `/etc/nginx/sites-available/auth-system`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Frontend
    location / {
        root /opt/auth-system/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Documentation
    location /docs {
        proxy_pass http://127.0.0.1:8000;
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
sudo systemctl reload nginx
```

### Step 5: Process Management

Create `/etc/supervisor/conf.d/auth-backend.conf`:

```ini
[program:auth-backend]
command=/opt/auth-system/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
directory=/opt/auth-system/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/auth-backend.log
environment=PATH="/opt/auth-system/backend/venv/bin"
```

Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start auth-backend
```

## Cloud Deployment

### Railway (Backend)

1. **Connect Repository:**
   - Connect your GitHub repository to Railway
   - Select the `backend` directory as the root

2. **Environment Variables:**
   ```
   DATABASE_URL=postgresql://...
   JWT_SECRET_KEY=your-production-secret
   CORS_ORIGINS=["https://your-frontend-domain.com"]
   ```

3. **Deploy:**
   - Railway will automatically build and deploy
   - Use the provided URL for your backend

### Vercel (Frontend)

1. **Connect Repository:**
   - Connect your GitHub repository to Vercel
   - Select the `frontend` directory as the root

2. **Environment Variables:**
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api/v1
   VITE_APP_NAME=Authentication System
   ```

3. **Build Settings:**
   - Build Command: `npm run build`
   - Output Directory: `dist`

### AWS/GCP/Azure

Refer to the respective cloud provider documentation for:
- Container deployment (ECS, Cloud Run, Container Instances)
- Database services (RDS, Cloud SQL, Azure Database)
- Load balancing and auto-scaling

## Monitoring and Maintenance

### Health Checks

```bash
# Check backend health
curl https://your-domain.com/api/v1/health

# Check database connection
curl https://your-domain.com/api/v1/health/detailed
```

### Log Monitoring

```bash
# Backend logs
sudo tail -f /var/log/auth-backend.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Database logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Database Backup

```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup (add to crontab)
0 2 * * * /opt/auth-system/scripts/backup.sh
```

### Updates and Maintenance

```bash
# Update application
cd /opt/auth-system
git pull origin main

# Run migrations if needed
./scripts/setup-database.sh --skip-create --skip-seeds

# Rebuild and restart
./scripts/deploy.sh --environment production

# Restart services
sudo supervisorctl restart auth-backend
sudo systemctl reload nginx
```

## Security Considerations

### SSL/TLS Configuration

- Use strong SSL/TLS configuration
- Enable HSTS headers
- Use secure cipher suites
- Regularly update SSL certificates

### Database Security

- Use strong passwords
- Enable SSL for database connections
- Restrict database access to application servers
- Regular security updates

### Application Security

- Change all default passwords
- Use strong JWT secrets
- Enable rate limiting
- Configure proper CORS origins
- Regular dependency updates

### Firewall Configuration

```bash
# Basic firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check database credentials
   - Verify database is running
   - Check network connectivity

2. **Frontend Cannot Connect to Backend**
   - Verify CORS configuration
   - Check API URL in frontend environment
   - Ensure backend is accessible

3. **SSL Certificate Issues**
   - Verify certificate paths
   - Check certificate expiration
   - Ensure proper nginx configuration

### Debug Commands

```bash
# Check service status
sudo systemctl status postgresql
sudo systemctl status nginx
sudo supervisorctl status

# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Test API endpoints
curl -X POST https://your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123456"}'
```

## Support

For additional support:
- Check the [Installation Guide](docs/installation-guide.md)
- Review [API Documentation](docs/api-documentation.md)
- Create an issue on GitHub
- Contact: support@example.com

---

**Remember**: Always test deployments in a staging environment before deploying to production!

