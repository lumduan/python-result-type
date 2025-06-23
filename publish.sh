#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Python Result Type - Publishing Script${NC}"
echo "========================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
echo -e "${GREEN}🔍 Checking prerequisites...${NC}"
if ! command_exists python; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

if ! command_exists pip; then
    echo -e "${RED}❌ pip not found${NC}"
    exit 1
fi

# Install/upgrade required packages
echo -e "${GREEN}📦 Installing/upgrading build tools...${NC}"
pip install --upgrade build twine pytest

# Run tests
echo -e "${GREEN}🧪 Running tests...${NC}"
python -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed! Aborting publish.${NC}"
    exit 1
fi

# Clean previous builds
echo -e "${GREEN}🧹 Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/

# Build the package
echo -e "${GREEN}🔨 Building package...${NC}"
python -m build

# Check if dist directory was created and has files
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo -e "${RED}❌ Build failed! No distribution files found.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Package built successfully!${NC}"
echo "Distribution files created:"
ls -la dist/

# Ask user what to do next
echo ""
echo -e "${YELLOW}📤 What would you like to do next?${NC}"
echo "1) Upload to Test PyPI (recommended)"
echo "2) Upload to PyPI"
echo "3) Exit"
read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}📤 Uploading to Test PyPI...${NC}"
        echo "You will need your Test PyPI API token."
        python -m twine upload --repository testpypi dist/*
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Successfully uploaded to Test PyPI!${NC}"
            echo "Check your package at: https://test.pypi.org/project/python-result-type/"
            echo ""
            echo "To test installation:"
            echo "pip install --index-url https://test.pypi.org/simple/ python-result-type"
        fi
        ;;
    2)
        echo -e "${GREEN}📤 Uploading to PyPI...${NC}"
        echo "You will need your PyPI API token."
        echo -e "${YELLOW}⚠️  This will make your package publicly available!${NC}"
        read -p "Are you sure? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            python -m twine upload dist/*
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Successfully uploaded to PyPI!${NC}"
                echo "Your package is now available at: https://pypi.org/project/python-result-type/"
                echo ""
                echo "Users can install it with:"
                echo "pip install python-result-type"
            fi
        else
            echo -e "${YELLOW}Upload cancelled.${NC}"
        fi
        ;;
    3)
        echo -e "${GREEN}👋 Exiting without upload.${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid option.${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Done!${NC}"
