#!/bin/bash
# GPIO Fix Script for Raspberry Pi Phone System

echo "Raspberry Pi GPIO Fix Script"
echo "============================"

# Update package list
echo "Updating package list..."
sudo apt update

# Install system GPIO packages
echo "Installing system GPIO packages..."
sudo apt install -y python3-lgpio python3-gpiozero python3-rpi.gpio

# Install pip GPIO packages
echo "Installing pip GPIO packages..."
pip install rpi-lgpio lgpio RPi.GPIO gpiozero

# Test GPIO
echo "Testing GPIO libraries..."
python3 gpio_test.py

echo ""
echo "GPIO setup complete!"
echo "If you still get errors, try running the phone system with:"
echo "  python3 phone_system.py"
echo ""
echo "The system will automatically fall back to keyboard input if GPIO fails."