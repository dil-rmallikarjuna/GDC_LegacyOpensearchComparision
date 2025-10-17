#!/bin/bash

# K6 Installation Script for macOS
# This script installs K6 using the official method

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Installing K6 Performance Testing Tool${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if K6 is already installed
if command -v k6 &> /dev/null; then
    echo -e "${GREEN}✅ K6 is already installed!${NC}"
    k6 version
    exit 0
fi

# Detect system architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    K6_ARCH="arm64"
elif [[ "$ARCH" == "x86_64" ]]; then
    K6_ARCH="amd64"
else
    echo -e "${RED}❌ Unsupported architecture: $ARCH${NC}"
    exit 1
fi

echo -e "${YELLOW}📊 Detected architecture: $ARCH ($K6_ARCH)${NC}"
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo -e "${YELLOW}📥 Downloading K6...${NC}"

# Download K6
K6_VERSION="v0.47.0"
K6_URL="https://github.com/grafana/k6/releases/download/${K6_VERSION}/k6-${K6_VERSION}-macos-${K6_ARCH}.tar.gz"

echo "Downloading from: $K6_URL"

if curl -L "$K6_URL" -o k6.tar.gz; then
    echo -e "${GREEN}✅ Download successful${NC}"
else
    echo -e "${RED}❌ Download failed${NC}"
    echo "Please try installing manually:"
    echo "1. Visit: https://k6.io/docs/getting-started/installation/"
    echo "2. Download the appropriate version for your system"
    exit 1
fi

echo -e "${YELLOW}📦 Extracting K6...${NC}"

# Extract K6
if tar -xzf k6.tar.gz; then
    echo -e "${GREEN}✅ Extraction successful${NC}"
else
    echo -e "${RED}❌ Extraction failed${NC}"
    exit 1
fi

# Find the k6 binary
K6_BINARY=$(find . -name "k6" -type f -executable | head -1)

if [[ -z "$K6_BINARY" ]]; then
    echo -e "${RED}❌ K6 binary not found in archive${NC}"
    exit 1
fi

echo -e "${YELLOW}📁 Installing K6 to /usr/local/bin...${NC}"

# Install K6
sudo cp "$K6_BINARY" /usr/local/bin/k6
sudo chmod +x /usr/local/bin/k6

# Clean up
cd /
rm -rf "$TEMP_DIR"

# Verify installation
if command -v k6 &> /dev/null; then
    echo -e "${GREEN}✅ K6 installed successfully!${NC}"
    echo ""
    k6 version
    echo ""
    echo -e "${BLUE}🎉 K6 is ready to use!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Navigate to the k6-tests directory"
    echo "2. Run: ./run-tests.sh smoke"
    echo "3. Or run: ./demo.sh"
else
    echo -e "${RED}❌ K6 installation failed${NC}"
    echo "Please try installing manually:"
    echo "1. Visit: https://k6.io/docs/getting-started/installation/"
    echo "2. Download the appropriate version for your system"
    exit 1
fi
