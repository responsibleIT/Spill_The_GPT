#!/bin/bash
# Quick setup script for clean Raspberry Pi installation

echo "=== Raspberry Pi Phone System Setup ==="
echo

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Setup will continue but GPIO features may not work"
    echo
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio alsa-utils python3-venv git curl

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "phone_env" ]; then
    python3 -m venv phone_env
fi

# Activate environment
source phone_env/bin/activate

# Install Python requirements
echo "📋 Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements_phone.txt

# Check for API keys
echo "🔑 Checking API keys..."
if [ ! -f ".env" ]; then
    echo "❌ No .env file found!"
    echo "   Please create .env file with your API keys:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo "   ELEVENLABS_API_KEY=your_key_here"
    echo
    read -p "Press Enter when you've created the .env file..."
fi

# Generate welcome messages
echo "🎵 Generating welcome audio messages..."
if [ ! -f "welcome.mp3" ] || [ ! -f "transition.mp3" ]; then
    python create_welcome.py
    if [ $? -eq 0 ]; then
        echo "✅ Audio messages generated successfully"
    else
        echo "❌ Failed to generate audio messages - check your ElevenLabs API key"
    fi
else
    echo "✅ Audio messages already exist"
fi

# Set up audio permissions
echo "🔊 Setting up audio permissions..."
sudo usermod -a -G audio $USER

# Test audio devices
echo "🎤 Testing audio devices..."
python fix_audio.py

echo
echo "=== Setup Complete! ==="
echo
echo "Next steps:"
echo "1. Log out and back in (for audio group permissions)"
echo "2. Run: source phone_env/bin/activate"
echo "3. Run: python phone_system.py"
echo
echo "If you have issues, check CLEAN_PI_SETUP.md for detailed troubleshooting"