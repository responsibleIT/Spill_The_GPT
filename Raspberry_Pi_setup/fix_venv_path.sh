#!/bin/bash
# Fix script for correcting virtual environment path from phone_env to env

echo "=== Fixing Virtual Environment Path ==="
echo "Updating systemd service to use 'env' instead of 'phone_env'"

SERVICE_NAME="phone-gossip"
CURRENT_USER=$(whoami)
SCRIPT_DIR=$(pwd)

# Check if service exists
if systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
    echo "📝 Service found. Updating configuration..."
    
    # Stop the service if running
    sudo systemctl stop $SERVICE_NAME
    
    # Recreate the service file with correct paths
    sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Phone Gossip System
After=network.target sound.service
Wants=network.target

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/env/bin
ExecStart=$SCRIPT_DIR/env/bin/python $SCRIPT_DIR/phone_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Audio environment
Environment="PULSE_RUNTIME_PATH=/run/user/1000/pulse"
Environment="XDG_RUNTIME_DIR=/run/user/1000"

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and restart service
    sudo systemctl daemon-reload
    
    echo "✅ Service updated with correct virtual environment path"
    echo "📁 Using: $SCRIPT_DIR/env/bin/python"
    
    # Test the configuration
    echo "🧪 Testing virtual environment..."
    if [ -d "env" ]; then
        echo "✅ Virtual environment 'env' found"
        
        if [ -f "env/bin/python" ]; then
            echo "✅ Python executable found in env"
            
            # Test if required packages are installed
            if env/bin/python -c "import openai, elevenlabs, pygame, pyaudio" 2>/dev/null; then
                echo "✅ Required packages available in env"
            else
                echo "⚠️  Some packages may be missing in env"
                echo "   Run: source env/bin/activate && pip install -r requirements_phone.txt"
            fi
        else
            echo "❌ Python executable not found in env/bin/"
        fi
    else
        echo "❌ Virtual environment 'env' not found"
        echo "   Create it with: python3 -m venv env"
    fi
    
    # Restart the service
    echo "🚀 Restarting service..."
    sudo systemctl start $SERVICE_NAME
    
    # Show status
    echo "📊 Service status:"
    sudo systemctl status $SERVICE_NAME --no-pager -l
    
else
    echo "📝 No existing service found. Run setup_kiosk_mode.sh to create it."
fi

echo
echo "=== Fix Complete ==="
echo
echo "Control commands:"
echo "  sudo systemctl status phone-gossip    # Check status"
echo "  sudo journalctl -u phone-gossip -f    # View logs"
echo "  sudo systemctl restart phone-gossip   # Restart service"