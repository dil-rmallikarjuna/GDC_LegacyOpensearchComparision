#!/bin/bash

# Test script that works without K6 installed
# Demonstrates the framework structure and provides installation guidance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 K6 Performance Testing Framework${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check if K6 is installed
if command -v k6 &> /dev/null; then
    echo -e "${GREEN}✅ K6 is installed and ready!${NC}"
    k6 version
    echo ""
    echo -e "${CYAN}🚀 You can now run the actual tests:${NC}"
    echo "  ./run-tests.sh smoke"
    echo "  ./demo.sh"
    exit 0
fi

echo -e "${YELLOW}⚠️  K6 is not installed. Let's set it up!${NC}"
echo ""

# Show installation options
echo -e "${CYAN}📋 Installation Options:${NC}"
echo -e "${CYAN}========================${NC}"
echo ""
echo "1. Using Homebrew (Recommended):"
echo "   brew install k6"
echo ""
echo "2. Manual Download:"
echo "   Visit: https://k6.io/docs/getting-started/installation/"
echo "   Download for macOS ARM64"
echo ""
echo "3. Using npm:"
echo "   npm install -g k6"
echo ""

# Show framework structure
echo -e "${CYAN}📁 Framework Structure:${NC}"
echo -e "${CYAN}======================${NC}"
echo ""
echo "k6-tests/"
echo "├── config/"
echo "│   └── k6-config.js          # Configuration"
echo "├── data/"
echo "│   └── name-generators.js    # Test data generators"
echo "├── scenarios/"
echo "│   ├── opensearch-api-test.js    # Main API test"
echo "│   ├── load-test.js              # Load testing"
echo "│   ├── stress-test.js            # Stress testing"
echo "│   ├── spike-test.js             # Spike testing"
echo "│   ├── volume-test.js            # Volume testing"
echo "│   ├── endurance-test.js         # Endurance testing"
echo "│   └── example-test.js           # Simple example"
echo "├── utils/"
echo "│   └── test-helpers.js       # Utility functions"
echo "├── run-tests.sh              # Test runner"
echo "├── demo.sh                   # Framework demo"
echo "├── install-k6.sh             # K6 installer"
echo "├── test-without-k6.sh         # This script"
echo "├── INSTALLATION.md            # Installation guide"
echo "└── README.md                  # Documentation"
echo ""

# Show available test scenarios
echo -e "${CYAN}🧪 Available Test Scenarios:${NC}"
echo -e "${CYAN}============================${NC}"
echo ""
echo "1. Smoke Test (scenarios/opensearch-api-test.js)"
echo "   - Quick validation test"
echo "   - 2-5 VUs, 1-2 minutes"
echo "   - Command: ./run-tests.sh smoke"
echo ""
echo "2. Load Test (scenarios/load-test.js)"
echo "   - Normal production load"
echo "   - 10-50 VUs, 5-10 minutes"
echo "   - Command: ./run-tests.sh load"
echo ""
echo "3. Stress Test (scenarios/stress-test.js)"
echo "   - High load testing"
echo "   - 50-200 VUs, 10-15 minutes"
echo "   - Command: ./run-tests.sh stress"
echo ""
echo "4. Spike Test (scenarios/spike-test.js)"
echo "   - Sudden traffic spikes"
echo "   - 100-150 VUs, 5-10 minutes"
echo "   - Command: ./run-tests.sh spike"
echo ""
echo "5. Volume Test (scenarios/volume-test.js)"
echo "   - High data volume"
echo "   - 30-50 VUs, 10 minutes"
echo "   - Command: ./run-tests.sh volume"
echo ""
echo "6. Endurance Test (scenarios/endurance-test.js)"
echo "   - Long-term stability"
echo "   - 10-20 VUs, 30+ minutes"
echo "   - Command: ./run-tests.sh endurance"
echo ""

# Show configuration
echo -e "${CYAN}⚙️  Configuration:${NC}"
echo -e "${CYAN}==================${NC}"
echo ""
echo "Environment settings in config/k6-config.js:"
echo "- Development: dev"
echo "- Staging: staging"
echo "- Production: prod"
echo ""
echo "Test scenarios can be customized:"
echo "- VU counts (Virtual Users)"
echo "- Test duration"
echo "- Performance thresholds"
echo "- API endpoints and authentication"
echo ""

# Show usage examples
echo -e "${CYAN}🚀 Usage Examples:${NC}"
echo -e "${CYAN}==================${NC}"
echo ""
echo "Once K6 is installed:"
echo ""
echo "# Quick smoke test"
echo "./run-tests.sh smoke"
echo ""
echo "# Load test with custom VUs and duration"
echo "./run-tests.sh -v 20 -d 5m load"
echo ""
echo "# Stress test against production"
echo "./run-tests.sh -e prod stress"
echo ""
echo "# All tests with custom output directory"
echo "./run-tests.sh -o ./results all"
echo ""
echo "# Run the demo"
echo "./demo.sh"
echo ""

# Show next steps
echo -e "${CYAN}📋 Next Steps:${NC}"
echo -e "${CYAN}==============${NC}"
echo ""
echo "1. Install K6 using one of the methods above"
echo "2. Verify installation: k6 version"
echo "3. Run the demo: ./demo.sh"
echo "4. Run your first test: ./run-tests.sh smoke"
echo "5. Read the documentation: README.md"
echo ""

echo -e "${GREEN}🎉 Framework is ready! Just install K6 to start testing.${NC}"
echo ""
echo -e "${BLUE}For detailed installation instructions, see: INSTALLATION.md${NC}"
