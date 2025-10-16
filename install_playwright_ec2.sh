#!/bin/bash
# Install Playwright and dependencies on EC2

echo "Installing Playwright..."
cd ~/Kaggle-competition-assist
source venv/bin/activate

pip install playwright
playwright install chromium
playwright install-deps

echo "Playwright installation complete!"

