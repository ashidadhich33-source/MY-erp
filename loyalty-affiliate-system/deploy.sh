#!/bin/bash

# Deployment script for Loyalty System
# This script handles deployment to production environment

set -e  # Exit on any error

# Configuration
PROJECT_NAME="loyalty-affiliate-system"
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
check_requirements() {
    log_info "Checking deployment requirements..."

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    if [ ! -f "$ENV_FILE" ]; then
        log_warn "Environment file not found: $ENV_FILE"
        log_info "Creating template environment file..."
        create_env_template
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi

    log_info "All requirements met!"
}

# Create environment template
create_env_template() {
    cat > "$ENV_FILE" << 'EOF'
# Production Environment Configuration
# Copy this file and update with your actual values

# Database Configuration
DATABASE_URL=postgresql://loyalty_user:your_password_here@db:5432/loyalty_db

# Redis Configuration
REDIS_URL=redis://redis:6379

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ERP Integration (Optional)
ERP_HOST=your-erp-host.com
ERP_PORT=8080
ERP_DATABASE=logic_erp
ERP_USERNAME=erp_user
ERP_PASSWORD=erp_password
ERP_API_KEY=your_erp_api_key

# WhatsApp Integration (Optional)
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourcompany.com

# Application Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=production

# Monitoring
GRAFANA_ADMIN_PASSWORD=admin
EOF
}

# Create backup
create_backup() {
    log_info "Creating backup..."

    mkdir -p "$BACKUP_DIR"

    # Backup database if running
    if docker-compose ps db | grep -q "Up"; then
        log_info "Backing up database..."
        docker-compose exec -T db pg_dump -U loyalty_user loyalty_db > "$BACKUP_DIR/database_backup.sql"
    fi

    # Backup environment file (excluding secrets)
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$BACKUP_DIR/.env.backup"
    fi

    log_info "Backup created in: $BACKUP_DIR"
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        log_warn "Some services are currently running. Consider stopping them first."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled by user"
            exit 0
        fi
    fi

    # Validate environment file
    if [ -f "$ENV_FILE" ]; then
        log_info "Validating environment configuration..."
        # Add validation logic here
    fi

    log_info "Pre-deployment checks completed"
}

# Deploy application
deploy() {
    log_info "Starting deployment..."

    # Create backup
    create_backup

    # Pull latest images
    log_info "Pulling Docker images..."
    docker-compose pull

    # Build services
    log_info "Building services..."
    docker-compose build --no-cache

    # Start services
    log_info "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    log_info "Waiting for services to be ready..."
    wait_for_services

    # Run database migrations
    run_migrations

    # Run health checks
    run_health_checks

    log_info "Deployment completed successfully!"
}

# Wait for services to be healthy
wait_for_services() {
    local retries=30
    local count=0

    log_info "Waiting for all services to be healthy..."

    while [ $count -lt $retries ]; do
        if docker-compose ps | grep -q "healthy\|Up"; then
            log_info "Services are ready!"
            return 0
        fi

        count=$((count + 1))
        sleep 10
    done

    log_error "Services failed to become healthy within expected time"
    exit 1
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."

    # Run Alembic migrations
    docker-compose exec -T backend alembic upgrade head

    # Run any additional setup scripts
    if [ -f "./backend/scripts/post_deploy.py" ]; then
        docker-compose exec -T backend python scripts/post_deploy.py
    fi
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."

    # Check backend health
    if curl -f http://localhost:8000/health; then
        log_info "Backend health check: PASSED"
    else
        log_error "Backend health check: FAILED"
        exit 1
    fi

    # Check frontend health
    if curl -f http://localhost:3000; then
        log_info "Frontend health check: PASSED"
    else
        log_error "Frontend health check: FAILED"
        exit 1
    fi

    # Check database connectivity
    if docker-compose exec -T db pg_isready -U loyalty_user -d loyalty_db; then
        log_info "Database health check: PASSED"
    else
        log_error "Database health check: FAILED"
        exit 1
    fi
}

# Rollback deployment
rollback() {
    log_warn "Starting rollback..."

    if [ -d "$BACKUP_DIR" ]; then
        log_info "Restoring from backup: $BACKUP_DIR"

        # Stop current deployment
        docker-compose down

        # Restore database if backup exists
        if [ -f "$BACKUP_DIR/database_backup.sql" ]; then
            docker-compose up -d db
            sleep 10
            docker-compose exec -T db psql -U loyalty_user -d loyalty_db < "$BACKUP_DIR/database_backup.sql"
        fi

        # Restore previous environment file
        if [ -f "$BACKUP_DIR/.env.backup" ]; then
            cp "$BACKUP_DIR/.env.backup" "$ENV_FILE"
        fi

        # Restart with previous version
        docker-compose up -d

        log_info "Rollback completed"
    else
        log_error "No backup found for rollback"
        exit 1
    fi
}

# Main deployment function
main() {
    echo "🚀 Loyalty System Deployment Script"
    echo "===================================="

    # Parse command line arguments
    case "${1:-deploy}" in
        "deploy")
            check_requirements
            pre_deployment_checks
            deploy
            ;;
        "rollback")
            rollback
            ;;
        "backup")
            create_backup
            ;;
        "test")
            pre_deployment_checks
            run_health_checks
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|backup|test}"
            echo "  deploy  - Run full deployment"
            echo "  rollback - Rollback to previous version"
            echo "  backup  - Create backup"
            echo "  test    - Run health checks"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"