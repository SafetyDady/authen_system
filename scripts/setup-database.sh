#!/bin/bash

# Database Setup Script for Authentication System
# This script sets up the PostgreSQL database with schema and seed data

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-auth_system}
DB_USER=${DB_USER:-auth_user}
DB_PASSWORD=${DB_PASSWORD:-auth_password}
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATABASE_DIR="$PROJECT_ROOT/database"

echo -e "${BLUE}=== Authentication System Database Setup ===${NC}"
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

# Function to check if PostgreSQL is running
check_postgres() {
    print_status "Checking PostgreSQL connection..."
    
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
            print_status "PostgreSQL is running and accessible"
            return 0
        else
            print_error "PostgreSQL is not accessible at $DB_HOST:$DB_PORT"
            return 1
        fi
    else
        print_warning "pg_isready not found, skipping connection check"
        return 0
    fi
}

# Function to create database and user
create_database() {
    print_status "Creating database and user..."
    
    # Set PGPASSWORD for postgres user if provided
    if [ -n "$POSTGRES_PASSWORD" ]; then
        export PGPASSWORD="$POSTGRES_PASSWORD"
    fi
    
    # Create user if not exists
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d postgres -c "
        DO \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
                CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
                GRANT CREATEDB TO $DB_USER;
                GRANT CONNECT ON DATABASE postgres TO $DB_USER;
            END IF;
        END
        \$\$;
    " 2>/dev/null || {
        print_warning "Could not create user (may already exist or insufficient permissions)"
    }
    
    # Create database if not exists
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d postgres -c "
        SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
    " 2>/dev/null || {
        print_warning "Could not create database (may already exist or insufficient permissions)"
    }
    
    # Grant privileges
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" -d postgres -c "
        GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
    " 2>/dev/null || {
        print_warning "Could not grant privileges"
    }
    
    unset PGPASSWORD
}

# Function to run migrations
run_migrations() {
    print_status "Running database migrations..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Check if migrations directory exists
    if [ ! -d "$DATABASE_DIR/migrations" ]; then
        print_error "Migrations directory not found: $DATABASE_DIR/migrations"
        return 1
    fi
    
    # Run each migration file in order
    for migration_file in "$DATABASE_DIR/migrations"/*.sql; do
        if [ -f "$migration_file" ]; then
            migration_name=$(basename "$migration_file")
            print_status "Applying migration: $migration_name"
            
            psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file" || {
                print_error "Failed to apply migration: $migration_name"
                return 1
            }
        fi
    done
    
    unset PGPASSWORD
}

# Function to run seeds
run_seeds() {
    print_status "Running database seeds..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Check if seeds directory exists
    if [ ! -d "$DATABASE_DIR/seeds" ]; then
        print_warning "Seeds directory not found: $DATABASE_DIR/seeds"
        return 0
    fi
    
    # Run each seed file in order
    for seed_file in "$DATABASE_DIR/seeds"/*.sql; do
        if [ -f "$seed_file" ]; then
            seed_name=$(basename "$seed_file")
            print_status "Applying seed: $seed_name"
            
            psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$seed_file" || {
                print_error "Failed to apply seed: $seed_name"
                return 1
            }
        fi
    done
    
    unset PGPASSWORD
}

# Function to verify setup
verify_setup() {
    print_status "Verifying database setup..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Check if tables exist
    table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
    " 2>/dev/null | tr -d ' ')
    
    if [ "$table_count" -gt 0 ]; then
        print_status "Database setup verified: $table_count tables created"
        
        # Show user count
        user_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "
            SELECT COUNT(*) FROM users;
        " 2>/dev/null | tr -d ' ')
        
        print_status "Default users created: $user_count"
    else
        print_error "Database setup verification failed: no tables found"
        return 1
    fi
    
    unset PGPASSWORD
}

# Function to show connection info
show_connection_info() {
    echo ""
    echo -e "${BLUE}=== Database Connection Information ===${NC}"
    echo -e "Host: ${GREEN}$DB_HOST${NC}"
    echo -e "Port: ${GREEN}$DB_PORT${NC}"
    echo -e "Database: ${GREEN}$DB_NAME${NC}"
    echo -e "Username: ${GREEN}$DB_USER${NC}"
    echo -e "Password: ${GREEN}$DB_PASSWORD${NC}"
    echo ""
    echo -e "${BLUE}=== Default User Accounts ===${NC}"
    echo -e "SuperAdmin: ${GREEN}admin@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Admin1: ${GREEN}admin1@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Admin2: ${GREEN}admin2@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Admin3: ${GREEN}admin3@example.com${NC} / ${GREEN}admin123456${NC}"
    echo -e "Test User: ${GREEN}john.doe@example.com${NC} / ${GREEN}user123456${NC}"
    echo ""
    echo -e "${YELLOW}Note: Change default passwords in production!${NC}"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  --host HOST             Database host (default: localhost)"
    echo "  --port PORT             Database port (default: 5432)"
    echo "  --db-name NAME          Database name (default: auth_system)"
    echo "  --db-user USER          Database user (default: auth_user)"
    echo "  --db-password PASS      Database password (default: auth_password)"
    echo "  --postgres-user USER    PostgreSQL admin user (default: postgres)"
    echo "  --postgres-password PASS PostgreSQL admin password"
    echo "  --skip-create           Skip database and user creation"
    echo "  --skip-migrations       Skip running migrations"
    echo "  --skip-seeds            Skip running seeds"
    echo "  --verify-only           Only verify existing setup"
    echo ""
    echo "Environment variables:"
    echo "  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
    echo "  POSTGRES_USER, POSTGRES_PASSWORD"
}

# Parse command line arguments
SKIP_CREATE=false
SKIP_MIGRATIONS=false
SKIP_SEEDS=false
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        --host)
            DB_HOST="$2"
            shift 2
            ;;
        --port)
            DB_PORT="$2"
            shift 2
            ;;
        --db-name)
            DB_NAME="$2"
            shift 2
            ;;
        --db-user)
            DB_USER="$2"
            shift 2
            ;;
        --db-password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --postgres-user)
            POSTGRES_USER="$2"
            shift 2
            ;;
        --postgres-password)
            POSTGRES_PASSWORD="$2"
            shift 2
            ;;
        --skip-create)
            SKIP_CREATE=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --skip-seeds)
            SKIP_SEEDS=true
            shift
            ;;
        --verify-only)
            VERIFY_ONLY=true
            shift
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
    # Check PostgreSQL connection
    if ! check_postgres; then
        print_error "Cannot connect to PostgreSQL. Please ensure it's running and accessible."
        exit 1
    fi
    
    if [ "$VERIFY_ONLY" = true ]; then
        verify_setup
        show_connection_info
        exit 0
    fi
    
    # Create database and user
    if [ "$SKIP_CREATE" = false ]; then
        create_database
    fi
    
    # Run migrations
    if [ "$SKIP_MIGRATIONS" = false ]; then
        run_migrations
    fi
    
    # Run seeds
    if [ "$SKIP_SEEDS" = false ]; then
        run_seeds
    fi
    
    # Verify setup
    verify_setup
    
    # Show connection info
    show_connection_info
    
    print_status "Database setup completed successfully!"
}

# Run main function
main "$@"

