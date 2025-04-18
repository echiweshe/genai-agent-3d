#!/bin/bash

# Exit on any error
#set -e  # Temporarily disable to continue despite errors

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== GenAI Agent 3D - Dependencies Installation Script =====${NC}"
echo "This script will install all the required dependencies for the GenAI Agent 3D project."
echo ""

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Install Git
if ! command_exists git; then
  echo -e "${YELLOW}Installing Git...${NC}"
  sudo apt-get install -y git
  echo -e "${GREEN}Git installed successfully!${NC}"
else
  echo -e "${GREEN}Git is already installed.${NC}"
fi

# Install Python 3.11
if ! command_exists python3.11; then
  echo -e "${YELLOW}Installing Python 3.11...${NC}"
  sudo apt-get install -y software-properties-common
  sudo add-apt-repository -y ppa:deadsnakes/ppa
  sudo apt-get update || true  # Continue even if update fails
  sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
  echo -e "${GREEN}Python 3.11 installed successfully!${NC}"
else
  echo -e "${GREEN}Python 3.11 is already installed.${NC}"
fi

# Install pip
echo -e "${YELLOW}Installing pip for Python 3.11...${NC}"
sudo apt-get install -y python3-pip
python3.11 -m ensurepip --upgrade || true
echo -e "${GREEN}pip installation attempted.${NC}"

# Install Node.js 18
if ! command_exists node || [ "$(node -v 2>/dev/null | grep -c 'v18\.')" -eq 0 ]; then
  echo -e "${YELLOW}Installing Node.js 18...${NC}"
  # Using NVM for more reliable Node.js installation
  echo -e "${YELLOW}Installing NVM (Node Version Manager)...${NC}"
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  
  # Load NVM without restarting terminal
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  
  # Install Node.js 18
  nvm install 18
  nvm use 18
  nvm alias default 18
  
  echo -e "${GREEN}Node.js 18 installed via NVM!${NC}"
  echo "Please run 'source ~/.bashrc' after this script completes to use Node.js."
else
  echo -e "${GREEN}Node.js 18 is already installed.${NC}"
fi

# Install Redis Server
if ! command_exists redis-cli; then
  echo -e "${YELLOW}Installing Redis Server...${NC}"
  sudo apt-get install -y redis-server
  echo -e "${GREEN}Redis Server installed successfully!${NC}"
else
  echo -e "${GREEN}Redis Server is already installed.${NC}"
fi

# Start and enable Redis
echo -e "${YELLOW}Ensuring Redis service is running...${NC}"
sudo systemctl start redis-server 2>/dev/null || sudo service redis-server start
sudo systemctl enable redis-server 2>/dev/null || sudo update-rc.d redis-server defaults
echo -e "${GREEN}Redis service is running.${NC}"

# Install Blender via Snap instead of PPA or Flatpak
if ! command_exists blender; then
  echo -e "${YELLOW}Installing Blender via Snap...${NC}"
  sudo apt-get install -y snapd
  sudo snap install blender --classic
  echo -e "${GREEN}Blender installed via Snap. Please check version after installation.${NC}"
else
  echo -e "${GREEN}Blender is already installed. Please verify version manually.${NC}"
fi

# Install Ollama manually
if ! command_exists ollama; then
  echo -e "${YELLOW}Installing Ollama manually...${NC}"
  OLLAMA_VERSION="0.1.29"
  wget -O ollama "https://github.com/ollama/ollama/releases/download/v${OLLAMA_VERSION}/ollama-linux-amd64"
  chmod +x ollama
  sudo mv ollama /usr/local/bin/
  echo -e "${GREEN}Ollama installed successfully!${NC}"
else
  echo -e "${GREEN}Ollama is already installed.${NC}"
fi

# Install other essential build tools
echo -e "${YELLOW}Installing essential build tools...${NC}"
sudo apt-get install -y build-essential python3-tk
echo -e "${GREEN}Essential build tools installed.${NC}"

# Verify installation
echo -e "${YELLOW}Verifying installations...${NC}"
echo -n "Git version: "
git --version 2>/dev/null || echo "Not installed correctly"

echo -n "Python 3.11 version: "
python3.11 --version 2>/dev/null || echo "Not installed correctly"

echo -n "Node.js version (may require terminal restart): "
node --version 2>/dev/null || echo "Run 'source ~/.bashrc' first"

echo -n "npm version (may require terminal restart): "
npm --version 2>/dev/null || echo "Run 'source ~/.bashrc' first"

echo -n "Redis status: "
redis-cli ping 2>/dev/null || echo "Not running"

echo -n "Blender installation: "
snap list blender 2>/dev/null || echo "Not installed via snap"

echo -n "Ollama version: "
ollama --version 2>/dev/null || echo "Not installed correctly"

# Print final instructions
echo -e "${GREEN}===== Installation process completed! =====${NC}"
echo "Please note the following:"
echo "1. You may need to run 'source ~/.bashrc' to use Node.js via NVM"
echo "2. Verify Blender version with 'blender --version' after restart"
echo "3. Start Ollama service with 'ollama serve'"
echo "4. For any missing components, check the verification output above"