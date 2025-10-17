#!/bin/bash

# K6 Performance Testing Demo
# Demonstrates the framework capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 K6 Performance Testing Framework Demo${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check if K6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}❌ K6 is not installed. Please install K6 first.${NC}"
    echo "Visit: https://k6.io/docs/getting-started/installation/"
    exit 1
fi

echo -e "${GREEN}✅ K6 is installed and ready!${NC}"
echo ""

# Demo 1: Quick smoke test
echo -e "${CYAN}🧪 Demo 1: Quick Smoke Test${NC}"
echo -e "${CYAN}===========================${NC}"
echo "Running a quick smoke test with 2 VUs for 30 seconds..."
echo ""

k6 run --vus 2 --duration 30s scenarios/example-test.js

echo ""
echo -e "${GREEN}✅ Smoke test completed!${NC}"
echo ""

# Demo 2: Load test
echo -e "${CYAN}🧪 Demo 2: Load Test${NC}"
echo -e "${CYAN}===================${NC}"
echo "Running a load test with 5 VUs for 1 minute..."
echo ""

k6 run --vus 5 --duration 1m scenarios/load-test.js

echo ""
echo -e "${GREEN}✅ Load test completed!${NC}"
echo ""

# Demo 3: Show available test scenarios
echo -e "${CYAN}📋 Available Test Scenarios${NC}"
echo -e "${CYAN}============================${NC}"
echo ""
echo "1. Smoke Test (scenarios/opensearch-api-test.js)"
echo "   - Quick validation test"
echo "   - 2-5 VUs, 1-2 minutes"
echo ""
echo "2. Load Test (scenarios/load-test.js)"
echo "   - Normal production load"
echo "   - 10-50 VUs, 5-10 minutes"
echo ""
echo "3. Stress Test (scenarios/stress-test.js)"
echo "   - High load testing"
echo "   - 50-200 VUs, 10-15 minutes"
echo ""
echo "4. Spike Test (scenarios/spike-test.js)"
echo "   - Sudden traffic spikes"
echo "   - 100-150 VUs, 5-10 minutes"
echo ""
echo "5. Volume Test (scenarios/volume-test.js)"
echo "   - High data volume"
echo "   - 30-50 VUs, 10 minutes"
echo ""
echo "6. Endurance Test (scenarios/endurance-test.js)"
echo "   - Long-term stability"
echo "   - 10-20 VUs, 30+ minutes"
echo ""

# Demo 4: Show how to run tests
echo -e "${CYAN}🚀 How to Run Tests${NC}"
echo -e "${CYAN}==================${NC}"
echo ""
echo "Using the test runner script:"
echo ""
echo "  # Quick smoke test"
echo "  ./run-tests.sh smoke"
echo ""
echo "  # Load test with custom VUs and duration"
echo "  ./run-tests.sh -v 20 -d 5m load"
echo ""
echo "  # All tests"
echo "  ./run-tests.sh all"
echo ""
echo "  # Different environment"
echo "  ./run-tests.sh -e prod stress"
echo ""
echo "  # Custom output directory"
echo "  ./run-tests.sh -o ./my-results all"
echo ""

# Demo 5: Show configuration
echo -e "${CYAN}⚙️  Configuration${NC}"
echo -e "${CYAN}================${NC}"
echo ""
echo "Environment configuration in config/k6-config.js:"
echo "- Development: dev"
echo "- Staging: staging"
echo "- Production: prod"
echo ""
echo "Test scenarios can be customized:"
echo "- VU counts"
echo "- Test duration"
echo "- Performance thresholds"
echo "- API endpoints"
echo ""

# Demo 6: Show metrics
echo -e "${CYAN}📊 Metrics and Reporting${NC}"
echo -e "${CYAN}=========================${NC}"
echo ""
echo "Built-in metrics:"
echo "- HTTP Request Duration"
echo "- HTTP Request Rate"
echo "- HTTP Request Failed"
echo "- Checks"
echo ""
echo "Custom metrics:"
echo "- Error Rate"
echo "- Search Latency"
echo "- Response Size"
echo "- High Volume Latency"
echo ""

echo -e "${GREEN}🎉 Demo completed!${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Review the README.md for detailed documentation"
echo "2. Customize the configuration for your environment"
echo "3. Run your first performance test"
echo "4. Analyze the results and adjust thresholds"
echo ""
echo -e "${BLUE}Happy Testing! 🚀${NC}"
