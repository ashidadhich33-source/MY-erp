#!/bin/bash

# Comprehensive test runner for Loyalty System
# Runs unit tests, integration tests, performance tests, and security tests

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
TEST_DIR="$BACKEND_DIR/tests"
COVERAGE_DIR="$BACKEND_DIR/htmlcov"
TEST_RESULTS_DIR="$PROJECT_ROOT/test_results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_DATABASE_URL="sqlite:///:memory:"
COVERAGE_MINIMUM=85
MAX_TEST_TIME=300  # 5 minutes per test file

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

log_success() {
    echo -e "${BLUE}[SUCCESS]${NC} $1"
}

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."

    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"

    # Set environment variables for testing
    export TESTING=True
    export DATABASE_URL="$TEST_DATABASE_URL"
    export SECRET_KEY="test-secret-key-for-testing-only"
    export ALGORITHM="HS256"
    export ACCESS_TOKEN_EXPIRE_MINUTES="30"
    export REFRESH_TOKEN_EXPIRE_DAYS="7"

    # Install test dependencies if needed
    if [ -f "$BACKEND_DIR/requirements-test.txt" ]; then
        log_info "Installing test dependencies..."
        pip install -r "$BACKEND_DIR/requirements-test.txt"
    fi

    log_success "Test environment setup complete"
}

# Run unit tests
run_unit_tests() {
    log_info "Running unit tests..."

    # Run pytest with coverage
    pytest \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-report=xml:"$TEST_RESULTS_DIR/coverage.xml" \
        --junitxml="$TEST_RESULTS_DIR/unit_tests.xml" \
        --tb=short \
        -m "unit" \
        "$TEST_DIR/" \
        -v

    # Check coverage
    local coverage=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('$TEST_RESULTS_DIR/coverage.xml'); root = tree.getroot(); print(root.get('line-rate'))")
    local coverage_percent=$(python -c "print(int(float('$coverage') * 100))")

    log_info "Unit test coverage: $coverage_percent%"

    if [ "$coverage_percent" -lt "$COVERAGE_MINIMUM" ]; then
        log_warn "Coverage ($coverage_percent%) is below minimum threshold ($COVERAGE_MINIMUM%)"
    else
        log_success "Coverage meets minimum requirement"
    fi
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."

    pytest \
        --junitxml="$TEST_RESULTS_DIR/integration_tests.xml" \
        --tb=short \
        -m "integration" \
        "$TEST_DIR/" \
        -v
}

# Run performance tests
run_performance_tests() {
    log_info "Running performance tests..."

    # Install performance testing tools if needed
    if ! command -v locust &> /dev/null; then
        log_warn "Locust not found. Installing..."
        pip install locust
    fi

    # Run Locust performance tests
    locust \
        -f "$TEST_DIR/performance_tests.py" \
        --csv="$TEST_RESULTS_DIR/performance" \
        --html="$TEST_RESULTS_DIR/performance_report.html" \
        --only-summary
}

# Run security tests
run_security_tests() {
    log_info "Running security tests..."

    # Install security testing tools
    if ! command -v bandit &> /dev/null; then
        log_warn "Bandit not found. Installing..."
        pip install bandit
    fi

    if ! command -v safety &> /dev/null; then
        log_warn "Safety not found. Installing..."
        pip install safety
    fi

    # Run bandit security analysis
    bandit -r "$BACKEND_DIR/app" -f xml -o "$TEST_RESULTS_DIR/security_report.xml"

    # Check for vulnerabilities
    local security_issues=$(grep -c "severity.*HIGH\|severity.*CRITICAL" "$TEST_RESULTS_DIR/security_report.xml" || echo "0")

    if [ "$security_issues" -gt 0 ]; then
        log_warn "Found $security_issues high/critical security issues"
    else
        log_success "No high or critical security issues found"
    fi

    # Check dependencies for vulnerabilities
    safety check --output json --file "$BACKEND_DIR/requirements.txt" > "$TEST_RESULTS_DIR/dependency_check.json"

    log_success "Security tests completed"
}

# Run API tests
run_api_tests() {
    log_info "Running API tests..."

    # Start test server in background
    cd "$BACKEND_DIR"
    uvicorn app.main:app --host 127.0.0.1 --port 8001 &
    local server_pid=$!

    # Wait for server to start
    sleep 5

    # Run API tests
    pytest \
        --junitxml="$TEST_RESULTS_DIR/api_tests.xml" \
        -k "api" \
        "$TEST_DIR/" \
        -v

    # Stop test server
    kill "$server_pid" 2>/dev/null || true

    log_success "API tests completed"
}

# Run database tests
run_database_tests() {
    log_info "Running database tests..."

    pytest \
        --junitxml="$TEST_RESULTS_DIR/database_tests.xml" \
        -k "database" \
        "$TEST_DIR/" \
        -v
}

# Run WhatsApp integration tests
run_whatsapp_tests() {
    log_info "Running WhatsApp integration tests..."

    pytest \
        --junitxml="$TEST_RESULTS_DIR/whatsapp_tests.xml" \
        -k "whatsapp" \
        "$TEST_DIR/" \
        -v
}

# Run ERP integration tests
run_erp_tests() {
    log_info "Running ERP integration tests..."

    pytest \
        --junitxml="$TEST_RESULTS_DIR/erp_tests.xml" \
        -k "erp" \
        "$TEST_DIR/" \
        -v
}

# Generate test reports
generate_reports() {
    log_info "Generating test reports..."

    # Generate HTML coverage report
    if [ -d "$COVERAGE_DIR" ]; then
        log_info "Coverage report available at: file://$COVERAGE_DIR/index.html"
    fi

    # Generate JUnit XML reports
    if [ -f "$TEST_RESULTS_DIR/unit_tests.xml" ]; then
        log_info "JUnit unit test report: $TEST_RESULTS_DIR/unit_tests.xml"
    fi

    # Generate test summary
    cat > "$TEST_RESULTS_DIR/test_summary.txt" << EOF
LOYALTY SYSTEM - TEST SUMMARY
============================

Test Run: $(date)
Environment: $TEST_DATABASE_URL
Coverage Minimum: $COVERAGE_MINIMUM%

RESULTS:
--------

EOF

    # Add test results to summary
    if [ -f "$TEST_RESULTS_DIR/unit_tests.xml" ]; then
        echo "Unit Tests: PASSED" >> "$TEST_RESULTS_DIR/test_summary.txt"
    fi

    if [ -f "$TEST_RESULTS_DIR/integration_tests.xml" ]; then
        echo "Integration Tests: PASSED" >> "$TEST_RESULTS_DIR/test_summary.txt"
    fi

    if [ -f "$TEST_RESULTS_DIR/security_report.xml" ]; then
        echo "Security Tests: COMPLETED" >> "$TEST_RESULTS_DIR/test_summary.txt"
    fi

    if [ -f "$TEST_RESULTS_DIR/performance_report.html" ]; then
        echo "Performance Tests: COMPLETED" >> "$TEST_RESULTS_DIR/test_summary.txt"
    fi

    log_success "Test reports generated in: $TEST_RESULTS_DIR/"
    log_info "Test summary available at: $TEST_RESULTS_DIR/test_summary.txt"
}

# Clean up test artifacts
cleanup() {
    log_info "Cleaning up test artifacts..."

    # Remove temporary files
    find "$TEST_DIR" -name "*.pyc" -delete
    find "$TEST_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

    # Clean up coverage artifacts
    rm -f "$BACKEND_DIR/.coverage"
    rm -rf "$BACKEND_DIR/htmlcov"

    log_success "Cleanup completed"
}

# Main test runner
main() {
    echo "🧪 Loyalty System - Comprehensive Test Suite"
    echo "=============================================="

    local start_time=$(date +%s)
    local test_type="${1:-all}"

    case "$test_type" in
        "unit")
            setup_test_env
            run_unit_tests
            ;;
        "integration")
            setup_test_env
            run_integration_tests
            ;;
        "security")
            setup_test_env
            run_security_tests
            ;;
        "performance")
            setup_test_env
            run_performance_tests
            ;;
        "api")
            setup_test_env
            run_api_tests
            ;;
        "database")
            setup_test_env
            run_database_tests
            ;;
        "whatsapp")
            setup_test_env
            run_whatsapp_tests
            ;;
        "erp")
            setup_test_env
            run_erp_tests
            ;;
        "all")
            setup_test_env
            run_unit_tests
            run_integration_tests
            run_security_tests
            run_performance_tests
            run_api_tests
            run_database_tests
            run_whatsapp_tests
            run_erp_tests
            generate_reports
            ;;
        "quick")
            setup_test_env
            run_unit_tests
            run_integration_tests
            generate_reports
            ;;
        *)
            echo "Usage: $0 {unit|integration|security|performance|api|database|whatsapp|erp|all|quick}"
            echo "  unit        - Run unit tests only"
            echo "  integration - Run integration tests only"
            echo "  security    - Run security tests only"
            echo "  performance - Run performance tests only"
            echo "  api         - Run API tests only"
            echo "  database    - Run database tests only"
            echo "  whatsapp    - Run WhatsApp integration tests only"
            echo "  erp         - Run ERP integration tests only"
            echo "  all         - Run all tests (default)"
            echo "  quick       - Run unit and integration tests only"
            exit 1
            ;;
    esac

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log_success "Test execution completed in $duration seconds"

    # Cleanup unless in debug mode
    if [ -z "$DEBUG" ]; then
        cleanup
    fi
}

# Run main function with all arguments
main "$@"