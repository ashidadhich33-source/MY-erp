#!/bin/bash

# Production Testing Script for Loyalty & Affiliate System

set -e

echo "🚀 Starting Production Readiness Tests..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check directory
if [ ! -f "backend/requirements.txt" ]; then
    print_error "Please run from project root"
    exit 1
fi

# Check files exist
echo "🔍 Checking core files..."
[ -f "backend/requirements.txt" ] && print_status "Backend dependencies file exists" || print_error "Missing requirements.txt"
[ -f "frontend/package.json" ] && print_status "Frontend dependencies file exists" || print_error "Missing package.json"
[ -f "docker-compose.yml" ] && print_status "Docker configuration exists" || print_error "Missing docker-compose.yml"
[ -f "backend/.env.example" ] && print_status "Backend environment template exists" || print_error "Missing backend .env.example"
[ -f "frontend/.env.example" ] && print_status "Frontend environment template exists" || print_error "Missing frontend .env.example"

# Check services
echo "🔧 Checking required services..."
services=("AuthService" "CustomerService" "LoyaltyService" "AffiliateService" "WhatsAppService" "RewardService" "AnalyticsService")
for service in "${services[@]}"; do
    if [ -f "backend/app/services/${service,,}.py" ]; then
        print_status "$service exists"
    else
        print_error "$service missing"
    fi
done

# Check models
echo "📊 Checking required models..."
models=("User" "Customer" "LoyaltyTransaction" "Affiliate" "WhatsAppMessage")
for model in "${models[@]}"; do
    if [ -f "backend/app/models/${model,,}.py" ]; then
        print_status "$model model exists"
    else
        print_error "$model model missing"
    fi
done

echo ""
echo "=========================================="
echo "🎉 Production Readiness Tests Completed!"
echo "=========================================="