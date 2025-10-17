#!/bin/bash

# K6 Performance Testing Runner
# Executes various performance tests with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENV=${ENV:-dev}
SCENARIO=${SCENARIO:-load}
VUS=${VUS:-10}
DURATION=${DURATION:-1m}
OUTPUT_DIR=${OUTPUT_DIR:-./results}

# Create results directory
mkdir -p $OUTPUT_DIR

echo -e "${BLUE}🚀 K6 Performance Testing Framework${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Function to run a test
run_test() {
    local test_name=$1
    local test_file=$2
    local vus=$3
    local duration=$4
    local output_file="$OUTPUT_DIR/k6-${test_name}-$(date +%Y%m%d_%H%M%S).json"
    
    echo -e "${YELLOW}🧪 Running: $test_name${NC}"
    echo -e "${YELLOW}📊 VUs: $vus | Duration: $duration${NC}"
    echo -e "${YELLOW}📁 Output: $output_file${NC}"
    echo ""
    
    k6 run \
        --env ENV=$ENV \
        --env SCENARIO=$SCENARIO \
        --vus $vus \
        --duration $duration \
        --out json=$output_file \
        $test_file
    
    # Generate HTML report
    local html_file="${output_file%.json}.html"
    if [ -f "utils/html-report-generator.js" ]; then
        echo -e "${YELLOW}📊 Generating HTML report...${NC}"
        node utils/html-report-generator.js "$output_file" "$html_file"
        echo -e "${GREEN}✅ HTML report: $html_file${NC}"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $test_name completed successfully${NC}"
    else
        echo -e "${RED}❌ $test_name failed${NC}"
        return 1
    fi
    echo ""
}

# Function to run load test
run_load_test() {
    echo -e "${BLUE}📈 Load Testing${NC}"
    echo -e "${BLUE}==============${NC}"
    
    # Light load
    run_test "load-light" "scenarios/opensearch-api-test.js" 5 "2m"
    
    # Medium load
    run_test "load-medium" "scenarios/opensearch-api-test.js" 20 "5m"
    
    # Heavy load
    run_test "load-heavy" "scenarios/opensearch-api-test.js" 50 "10m"
}

# Function to run stress test
run_stress_test() {
    echo -e "${BLUE}🔥 Stress Testing${NC}"
    echo -e "${BLUE}===============${NC}"
    
    # Gradual stress
    run_test "stress-gradual" "scenarios/stress-test.js" 100 "15s"
    
    # High stress
    run_test "stress-high" "scenarios/stress-test.js" 200 "10s"
}

# Function to run spike test
run_spike_test() {
    echo -e "${BLUE}⚡ Spike Testing${NC}"
    echo -e "${BLUE}==============${NC}"
    
    # Quick spike
    run_test "spike-quick" "scenarios/spike-test.js" 100 "5m"
    
    # Extended spike
    run_test "spike-extended" "scenarios/spike-test.js" 150 "10m"
}

# Function to run volume test
run_volume_test() {
    echo -e "${BLUE}📦 Volume Testing${NC}"
    echo -e "${BLUE}================${NC}"
    
    # High volume test
    run_test "volume-high" "scenarios/volume-test.js" 50 "10m"
}

# Function to run endurance test
run_endurance_test() {
    echo -e "${BLUE}⏰ Endurance Testing${NC}"
    echo -e "${BLUE}===================${NC}"
    
    # Long-term stability test
    run_test "endurance-stability" "scenarios/endurance-test.js" 20 "30m"
}

# Function to run smoke test
run_smoke_test() {
    echo -e "${BLUE}💨 Smoke Testing${NC}"
    echo -e "${BLUE}===============${NC}"
    
    # Basic smoke test
    run_test "smoke-basic" "scenarios/opensearch-api-test.js" 2 "1m"
}

# Function to run all tests
run_all_tests() {
    echo -e "${BLUE}🎯 Running All Performance Tests${NC}"
    echo -e "${BLUE}=================================${NC}"
    
    run_smoke_test
    run_load_test
    run_stress_test
    run_spike_test
    run_volume_test
    run_endurance_test
    
    echo -e "${GREEN}🎉 All tests completed!${NC}"
    echo -e "${GREEN}📁 Results saved in: $OUTPUT_DIR${NC}"
}

# Function to show help
show_help() {
    echo -e "${BLUE}K6 Performance Testing Framework${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "Options:"
    echo "  -e, --env ENV        Environment (dev|staging|prod) [default: dev]"
    echo "  -v, --vus VUS        Virtual Users [default: 10]"
    echo "  -d, --duration TIME  Test duration [default: 1m]"
    echo "  -o, --output DIR     Output directory [default: ./results]"
    echo "  -h, --help           Show this help"
    echo ""
    echo "Test Types:"
    echo "  smoke               Quick smoke test (2 VUs, 1m)"
    echo "  load                Load testing (5-50 VUs, 2-10m)"
    echo "  stress              Stress testing (100-200 VUs, 10-15m)"
    echo "  spike               Spike testing (100-150 VUs, 5-10m)"
    echo "  volume              Volume testing (30-50 VUs, 10m)"
    echo "  endurance           Endurance testing (10-20 VUs, 30m)"
    echo "  all                 Run all test types"
    echo ""
    echo "Examples:"
    echo "  $0 smoke                    # Run smoke test"
    echo "  $0 load                    # Run load tests"
    echo "  $0 -v 50 -d 5m stress      # Run stress test with 50 VUs for 5 minutes"
    echo "  $0 -e prod all              # Run all tests against production"
    echo ""
}

# Parse command line arguments
TEST_TYPE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -v|--vus)
            VUS="$2"
            shift 2
            ;;
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        smoke|load|stress|spike|volume|endurance|all)
            TEST_TYPE="$1"
            shift
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Set default test type if none specified
if [ -z "$TEST_TYPE" ]; then
    TEST_TYPE="smoke"
fi

# Check if K6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}❌ K6 is not installed. Please install K6 first.${NC}"
    echo "Visit: https://k6.io/docs/getting-started/installation/"
    exit 1
fi

# Display configuration
echo -e "${BLUE}Configuration:${NC}"
echo -e "Environment: $ENV"
echo -e "Test Type: $TEST_TYPE"
echo -e "VUs: $VUS"
echo -e "Duration: $DURATION"
echo -e "Output: $OUTPUT_DIR"
echo ""

# Run selected test
case $TEST_TYPE in
    smoke)
        run_smoke_test
        ;;
    load)
        run_load_test
        ;;
    stress)
        run_stress_test
        ;;
    spike)
        run_spike_test
        ;;
    volume)
        run_volume_test
        ;;
    endurance)
        run_endurance_test
        ;;
    all)
        run_all_tests
        ;;
    *)
        echo -e "${RED}❌ Unknown test type: $TEST_TYPE${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Performance testing completed!${NC}"
