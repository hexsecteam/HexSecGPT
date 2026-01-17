#!/bin/bash

# HexSecGPT Installer for Linux and Termux

echo "======================================"
echo "    HexSecGPT Installer Script"
echo "======================================"

# Function to detect package manager
detect_pkg_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v pkg &> /dev/null; then
        echo "pkg"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_pkg_manager)

# Update and install dependencies
echo "[+] Updating package lists..."
if [ "$PKG_MANAGER" = "apt" ]; then
    sudo apt-get update -y
    echo "[+] Installing git, python, and pip..."
    sudo apt-get install git python3 python3-pip -y
elif [ "$PKG_MANAGER" = "pkg" ]; then
    pkg update -y
    echo "[+] Installing git and python..."
    pkg install git python -y
else
    echo "[!] Unsupported package manager. Please install git, python3, and pip manually."
    exit 1
fi

# Clone the repository
if [ -d "HexSecGPT" ]; then
    echo "[!] HexSecGPT directory already exists. Skipping clone."
else
    echo "[+] Cloning HexSecGPT repository..."
    git clone https://github.com/hexsecteam/HexSecGPT.git
fi

cd HexSecGPT

# Install Python requirements
echo "[+] Installing required python packages..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi

echo ""
echo "======================================"
echo "      Installation Complete!"
echo "======================================"
echo "To run HexSecGPT:"
echo "1. cd HexSecGPT"
echo "2. python3 HexSecGPT.py"
echo ""
echo "Don't forget to get your API key from OpenRouter or DeepSeek!"
echo "======================================"
