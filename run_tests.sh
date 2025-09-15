#!/bin/bash

# DOM Analyzer Test Suite Runner
# Comprehensive test execution with reporting and CI/CD integration

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_DIR="$PROJECT_ROOT/venv"
REPORTS_DIR="$PROJECT_ROOT/test_reports"
COVERAGE_DIR="$PROJECT_ROOT/htmlcov"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
RUN_UNIT_TESTS=true
RUN_E2E_TESTS=true
RUN_BENCHMARKS=false
GENERATE_COVERAGE=true
VERBOSE=false
HEADLESS=true
PARALLEL=true
TIMEOUT=300
BROWSER="chrome"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
DOM Analyzer Test Suite Runner

Usage: $0 [OPTIONS]

Options:
    -u, --unit-only         Run only unit tests
    -e, --e2e-only          Run only end-to-end tests
    -b, --benchmarks        Run performance benchmarks
    -c, --no-coverage       Skip coverage reporting
    -v, --verbose           Verbose output
    -h, --headed            Run browser tests in headed mode
    -s, --sequential        Run tests sequentially (not in parallel)
    -t, --timeout SECONDS   Test timeout (default: 300)
    --browser BROWSER       Browser for E2E tests (chrome, firefox)
    --help                  Show this help message

Examples:
    $0                      # Run all tests with coverage
    $0 --unit-only         # Run only unit tests
    $0 --benchmarks        # Include performance benchmarks
    $0 --headed --verbose  # Run with browser visible and verbose output
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit-only)
            RUN_UNIT_TESTS=true
            RUN_E2E_TESTS=false
            shift
            ;;
        -e|--e2e-only)
            RUN_UNIT_TESTS=false
            RUN_E2E_TESTS=true
            shift
            ;;
        -b|--benchmarks)
            RUN_BENCHMARKS=true
            shift
            ;;
        -c|--no-coverage)
            GENERATE_COVERAGE=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--headed)
            HEADLESS=false
            shift
            ;;
        -s|--sequential)
            PARALLEL=false
            shift
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --browser)
            BROWSER="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements.txt"
    fi
    
    # Install test dependencies
    pip install pytest pytest-cov pytest-html pytest-xdist responses selenium psutil
    
    print_success "Dependencies installed"
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION="3.8"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8+ required, found $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION found"
    
    # Check for browser if running E2E tests
    if [ "$RUN_E2E_TESTS" = true ]; then
        if [ "$BROWSER" = "chrome" ]; then
            if ! command_exists google-chrome && ! command_exists chromium-browser && ! command_exists google-chrome-stable; then
                print_warning "Chrome browser not found. E2E tests may fail."
                print_warning "Install Chrome or use --browser firefox"
            fi
        elif [ "$BROWSER" = "firefox" ]; then
            if ! command_exists firefox; then
                print_warning "Firefox browser not found. E2E tests may fail."
            fi
        fi
    fi
}

# Function to create report directories
setup_reports() {
    print_status "Setting up report directories..."
    
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$COVERAGE_DIR"
    
    # Clean old reports
    rm -f "$REPORTS_DIR"/*.xml
    rm -f "$REPORTS_DIR"/*.html
    rm -f "$REPORTS_DIR"/*.json
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    cd "$PROJECT_ROOT"
    
    # Build pytest command
    PYTEST_ARGS=()
    
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS+=("-v")
    else
        PYTEST_ARGS+=("-q")
    fi
    
    if [ "$PARALLEL" = true ]; then
        PYTEST_ARGS+=("-n" "auto")
    fi
    
    if [ "$GENERATE_COVERAGE" = true ]; then
        PYTEST_ARGS+=("--cov=core_analyzer" "--cov=cli" "--cov-report=html:$COVERAGE_DIR" "--cov-report=xml:$REPORTS_DIR/coverage.xml")
    fi
    
    # Add JUnit XML report
    PYTEST_ARGS+=("--junitxml=$REPORTS_DIR/unit_tests.xml")
    
    # Add HTML report
    PYTEST_ARGS+=("--html=$REPORTS_DIR/unit_tests.html" "--self-contained-html")
    
    # Add timeout
    PYTEST_ARGS+=("--timeout=$TIMEOUT")
    
    # Run tests
    if pytest "${PYTEST_ARGS[@]}" test_analyzer.py; then
        print_success "Unit tests passed"
        return 0
    else
        print_error "Unit tests failed"
        return 1
    fi
}

# Function to run E2E tests
run_e2e_tests() {
    print_status "Running end-to-end tests..."
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables for E2E tests
    export BROWSER="$BROWSER"
    export HEADLESS="$HEADLESS"
    
    # Build pytest command
    PYTEST_ARGS=()
    
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS+=("-v" "-s")
    else
        PYTEST_ARGS+=("-q")
    fi
    
    # E2E tests should not run in parallel due to browser instances
    PYTEST_ARGS+=("--junitxml=$REPORTS_DIR/e2e_tests.xml")
    PYTEST_ARGS+=("--html=$REPORTS_DIR/e2e_tests.html" "--self-contained-html")
    PYTEST_ARGS+=("--timeout=$TIMEOUT")
    
    # Run tests
    if pytest "${PYTEST_ARGS[@]}" test_e2e.py; then
        print_success "E2E tests passed"
        return 0
    else
        print_error "E2E tests failed"
        return 1
    fi
}

# Function to run benchmarks
run_benchmarks() {
    print_status "Running performance benchmarks..."
    
    cd "$PROJECT_ROOT"
    
    # Build pytest command
    PYTEST_ARGS=()
    
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS+=("-v" "-s")
    fi
    
    PYTEST_ARGS+=("--junitxml=$REPORTS_DIR/benchmarks.xml")
    PYTEST_ARGS+=("--html=$REPORTS_DIR/benchmarks.html" "--self-contained-html")
    PYTEST_ARGS+=("--timeout=$((TIMEOUT * 2))")  # Benchmarks need more time
    
    # Run benchmarks
    if pytest "${PYTEST_ARGS[@]}" test_benchmarks.py; then
        print_success "Benchmarks completed"
        return 0
    else
        print_error "Benchmarks failed"
        return 1
    fi
}

# Function to test CLI directly
test_cli() {
    print_status "Testing CLI functionality..."
    
    cd "$PROJECT_ROOT"
    
    # Test CLI help
    if ! python3 cli.py --help > /dev/null 2>&1; then
        print_warning "CLI help command failed"
        return 1
    fi
    
    # Test CLI version
    if ! python3 cli.py --version > /dev/null 2>&1; then
        print_warning "CLI version command failed"
        return 1
    fi
    
    # Test CLI with mock URL (quick test)
    print_status "Testing CLI with sample analysis..."
    if timeout 30 python3 cli.py https://httpbin.org/html --format json --timeout 10 > /dev/null 2>&1; then
        print_success "CLI integration test passed"
    else
        print_warning "CLI integration test failed (network may be required)"
    fi
    
    return 0
}

# Function to generate summary report
generate_summary() {
    print_status "Generating test summary..."
    
    SUMMARY_FILE="$REPORTS_DIR/test_summary.txt"
    
    cat > "$SUMMARY_FILE" << EOF
DOM Analyzer Test Suite Summary
===============================
Run Date: $(date)
Test Configuration:
- Unit Tests: $RUN_UNIT_TESTS
- E2E Tests: $RUN_E2E_TESTS
- Benchmarks: $RUN_BENCHMARKS
- Coverage: $GENERATE_COVERAGE
- Browser: $BROWSER
- Parallel: $PARALLEL
- Timeout: ${TIMEOUT}s

EOF
    
    # Add results from XML files if they exist
    if [ -f "$REPORTS_DIR/unit_tests.xml" ]; then
        echo "Unit Test Results:" >> "$SUMMARY_FILE"
        if command_exists xmlstarlet; then
            xmlstarlet sel -t -v "//testsuite/@tests" -o " tests, " -v "//testsuite/@failures" -o " failures, " -v "//testsuite/@errors" -o " errors" "$REPORTS_DIR/unit_tests.xml" >> "$SUMMARY_FILE"
        else
            echo "XML parsing not available (install xmlstarlet)" >> "$SUMMARY_FILE"
        fi
        echo "" >> "$SUMMARY_FILE"
    fi
    
    if [ -f "$REPORTS_DIR/e2e_tests.xml" ]; then
        echo "E2E Test Results:" >> "$SUMMARY_FILE"
        if command_exists xmlstarlet; then
            xmlstarlet sel -t -v "//testsuite/@tests" -o " tests, " -v "//testsuite/@failures" -o " failures, " -v "//testsuite/@errors" -o " errors" "$REPORTS_DIR/e2e_tests.xml" >> "$SUMMARY_FILE"
        fi
        echo "" >> "$SUMMARY_FILE"
    fi
    
    # Add coverage summary if available
    if [ -f "$REPORTS_DIR/coverage.xml" ] && command_exists xmlstarlet; then
        echo "Coverage Summary:" >> "$SUMMARY_FILE"
        xmlstarlet sel -t -v "//coverage/@line-rate" "$REPORTS_DIR/coverage.xml" | awk '{print $1 * 100 "% line coverage"}' >> "$SUMMARY_FILE"
        echo "" >> "$SUMMARY_FILE"
    fi
    
    echo "Reports generated in: $REPORTS_DIR" >> "$SUMMARY_FILE"
    
    cat "$SUMMARY_FILE"
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up..."
    
    # Kill any remaining processes
    pkill -f "python.*app\.py" 2>/dev/null || true
    pkill -f "flask" 2>/dev/null || true
    
    # Clean temporary files
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
}

# Trap cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    print_status "Starting DOM Analyzer Test Suite"
    print_status "Project Root: $PROJECT_ROOT"
    
    # Check requirements
    check_requirements
    
    # Setup environment
    setup_venv
    setup_reports
    
    # Track test results
    UNIT_RESULT=0
    E2E_RESULT=0
    BENCHMARK_RESULT=0
    CLI_RESULT=0
    
    # Run unit tests
    if [ "$RUN_UNIT_TESTS" = true ]; then
        run_unit_tests
        UNIT_RESULT=$?
    fi
    
    # Run E2E tests
    if [ "$RUN_E2E_TESTS" = true ]; then
        run_e2e_tests
        E2E_RESULT=$?
    fi
    
    # Run benchmarks
    if [ "$RUN_BENCHMARKS" = true ]; then
        run_benchmarks
        BENCHMARK_RESULT=$?
    fi
    
    # Test CLI
    test_cli
    CLI_RESULT=$?
    
    # Generate summary
    generate_summary
    
    # Final status
    TOTAL_FAILURES=$((UNIT_RESULT + E2E_RESULT + BENCHMARK_RESULT + CLI_RESULT))
    
    if [ $TOTAL_FAILURES -eq 0 ]; then
        print_success "All tests passed successfully!"
        
        if [ "$GENERATE_COVERAGE" = true ] && [ -d "$COVERAGE_DIR" ]; then
            print_success "Coverage report: file://$COVERAGE_DIR/index.html"
        fi
        
        exit 0
    else
        print_error "Tests failed. Check reports in $REPORTS_DIR"
        exit 1
    fi
}

# Check if running directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi