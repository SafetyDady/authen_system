#!/bin/bash

# Deployment Script for Authentication System
# This script handles deployment to various environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${ENVIRONMENT:-development}
BUILD_FRONTEND=${BUILD_FRONTEND:-true}
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
BACKUP_DB=${BACKUP_DB:-false}
DOCKER_COMPOSE=${DOCKER_COMPOSE:-false}

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}=== Authentication System Deployment ===${NC}"
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "Project Root: ${GREEN}$PROJECT_ROOT${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if required commands exist
    local required_commands=("node" "npm" "python3" "pip3")
    
    if [ "$DOCKER_COMPOSE" = true ]; then
        required_commands+=("docker" "docker-compose")
    fi
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            print_error "$cmd is not installed or not in PATH"
            exit 1
        fi
    done
    
    print_status "Prerequisites check passed"
}

# Function to load environment variables
load_environment() {
    print_status "Loading environment configuration..."
    
    # Load environment-specific variables
    if [ -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
        print_status "Loading .env.$ENVIRONMENT"
        export $(cat "$PROJECT_ROOT/.env.$ENVIRONMENT" | grep -v '^#' | xargs)
    elif [ -f "$PROJECT_ROOT/.env" ]; then
        print_status "Loading .env"
        export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
    else
        print_warning "No environment file found"
    fi
}

# Function to backup database
backup_database() {
    if [ "$BACKUP_DB" = true ]; then
        print_status "Creating database backup..."
        
        local backup_dir="$PROJECT_ROOT/backups"
        local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
        
        mkdir -p "$backup_dir"
        
        if [ -n "$DATABASE_URL" ]; then
            pg_dump "$DATABASE_URL" > "$backup_dir/$backup_file"
            print_status "Database backup created: $backup_file"
        else
            print_warning "DATABASE_URL not set, skipping backup"
        fi
    fi
}

# Function to run database migrations
run_migrations() {
    if [ "$RUN_MIGRATIONS" = true ]; then
        print_status "Running database migrations..."
        
        cd "$PROJECT_ROOT"
        
        if [ -f "scripts/setup-database.sh" ]; then
            ./scripts/setup-database.sh --skip-create --skip-seeds
        else
            print_warning "Database setup script not found"
        fi
    fi
}

# Function to build frontend
build_frontend() {
    if [ "$BUILD_FRONTEND" = true ]; then
        print_status "Building frontend application..."
        
        cd "$PROJECT_ROOT/frontend"
        
        # Install dependencies
        print_status "Installing frontend dependencies..."
        npm ci
        
        # Build application
        print_status "Building frontend for $ENVIRONMENT..."
        if [ "$ENVIRONMENT" = "production" ]; then
            npm run build
        else
            npm run build:dev
        fi
        
        print_status "Frontend build completed"
    fi
}

# Function to deploy with Docker Compose
deploy_docker() {
    print_status "Deploying with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    # Build and start services
    docker-compose down --remove-orphans
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if docker-compose ps | grep -q "unhealthy\|Exit"; then
        print_error "Some services are not healthy"
        docker-compose logs
        exit 1
    fi
    
    print_status "Docker deployment completed"
}

# Function to deploy manually
deploy_manual() {
    print_status "Deploying manually..."
    
    # Backend deployment
    print_status "Deploying backend..."
    cd "$PROJECT_ROOT/backend"
    
    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    pip install -r requirements.txt
    
    # Start backend service (in background for development)
    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "Starting backend in development mode..."
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        echo $BACKEND_PID > "$PROJECT_ROOT/backend.pid"
    else
        print_status "Backend ready for production deployment"
        print_status "Use: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
    fi
    
    # Frontend deployment
    if [ "$BUILD_FRONTEND" = true ]; then
        print_status "Deploying frontend..."
        cd "$PROJECT_ROOT/frontend"
        
        if [ "$ENVIRONMENT" = "development" ]; then
            print_status "Starting frontend in development mode..."
            npm run dev &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > "$PROJECT_ROOT/frontend.pid"
        else
            print_status "Frontend built and ready for production deployment"
            print_status "Serve the 'dist' directory with your web server"
        fi
    fi
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    local backend_url="http://localhost:8000"
    local frontend_url="http://localhost:3000"
    
    # Check backend health
    print_status "Checking backend health..."
    if curl -f "$backend_url/health" >/dev/null 2>&1; then
        print_status "Backend is healthy"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend (if built)
    if [ "$BUILD_FRONTEND" = true ]; then
        print_status "Checking frontend..."
        if curl -f "$frontend_url" >/dev/null 2>&1; then
            print_status "Frontend is accessible"
        else
            print_warning "Frontend health check failed (may be normal in development)"
        fi
    fi
    
    # Test API endpoints
    print_status "Testing API endpoints..."
    
    # Test login endpoint
    local login_response=$(curl -s -X POST "$backend_url/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email": "admin@example.com", "password": "admin123456"}')
    
    if echo "$login_response" | grep -q "access_token"; then
        print_status "API authentication test passed"
    else
        print_error "API authentication test failed"
        return 1
    fi
    
    print_status "Deployment verification completed successfully"
}

# Function to show deployment info
show_deployment_info() {
    echo ""
    echo -e "${BLUE}=== Deployment Information ===${NC}"
    echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
    echo -e "Backend URL: ${GREEN}http://localhost:8000${NC}"
    echo -e "API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
    
    if [ "$BUILD_FRONTEND" = true ]; then
        echo -e "Frontend URL: ${GREEN}http://localhost:3000${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}=== Default Accounts ===${NC}"
    echo -e "SuperAdmin: ${GREEN}admin@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Admin1: ${GREEN}admin1@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Admin2: ${GREEN}admin2@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Admin3: ${GREEN}admin3@example.com${NC} / ${GREEN}admin123456${NC}"
    echo ""
    echo -e "${YELLOW}Remember to change default passwords in production!${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Deployment environment (development, staging, production)"
    echo "  -d, --docker            Use Docker Compose for deployment"
    echo "  -b, --build-frontend    Build frontend application (default: true)"
    echo "  -m, --run-migrations    Run database migrations (default: true)"
    echo "  -B, --backup-db         Create database backup before deployment"
    echo "  -v, --verify-only       Only verify existing deployment"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  ENVIRONMENT, BUILD_FRONTEND, RUN_MIGRATIONS, BACKUP_DB, DOCKER_COMPOSE"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy to development"
    echo "  $0 -e production -B                  # Deploy to production with backup"
    echo "  $0 -d                                # Deploy using Docker Compose"
    echo "  $0 -v                                # Verify existing deployment"
}

# Parse command line arguments
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--docker)
            DOCKER_COMPOSE=true
            shift
            ;;
        -b|--build-frontend)
            BUILD_FRONTEND=true
            shift
            ;;
        --no-build-frontend)
            BUILD_FRONTEND=false
            shift
            ;;
        -m|--run-migrations)
            RUN_MIGRATIONS=true
            shift
            ;;
        --no-migrations)
            RUN_MIGRATIONS=false
            shift
            ;;
        -B|--backup-db)
            BACKUP_DB=true
            shift
            ;;
        -v|--verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Check prerequisites
    check_prerequisites
    
    # Load environment
    load_environment
    
    if [ "$VERIFY_ONLY" = true ]; then
        verify_deployment
        show_deployment_info
        exit 0
    fi
    
    # Create database backup if requested
    backup_database
    
    # Run database migrations
    run_migrations
    
    # Deploy based on method
    if [ "$DOCKER_COMPOSE" = true ]; then
        deploy_docker
    else
        # Build frontend
        build_frontend
        
        # Deploy manually
        deploy_manual
    fi
    
    # Verify deployment
    if verify_deployment; then
        print_status "Deployment completed successfully!"
        show_deployment_info
    else
        print_error "Deployment verification failed"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Kill background processes if they exist
    if [ -f "$PROJECT_ROOT/backend.pid" ]; then
        kill $(cat "$PROJECT_ROOT/backend.pid") 2>/dev/null || true
        rm "$PROJECT_ROOT/backend.pid"
    fi
    
    if [ -f "$PROJECT_ROOT/frontend.pid" ]; then
        kill $(cat "$PROJECT_ROOT/frontend.pid") 2>/dev/null || true
        rm "$PROJECT_ROOT/frontend.pid"
    fi
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Run main function
main "$@"

