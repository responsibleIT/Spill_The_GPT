#!/bin/bash
# Kiosk Mode Setup Script for Raspberry Pi Phone System
# This script configures the Pi to automatically start the phone system on boot

echo "=== Setting up Raspberry Pi Kiosk Mode ==="
echo "This will configure your Pi to automatically start the phone system on boot"
echo

# Get current user and working directory
CURRENT_USER=$(whoami)
SCRIPT_DIR=$(pwd)
SERVICE_NAME="phone-gossip"

echo "Current user: $CURRENT_USER"
echo "Script directory: $SCRIPT_DIR"
echo "Service name: $SERVICE_NAME"
echo

# 1. Create systemd service file
echo "📝 Creating systemd service..."

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
Environment=PATH=$SCRIPT_DIR/phone_env/bin
ExecStart=$SCRIPT_DIR/phone_env/bin/python $SCRIPT_DIR/phone_system.py
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

echo "✅ Service file created at /etc/systemd/system/${SERVICE_NAME}.service"

# 2. Create startup script with better error handling
echo "📝 Creating startup script..."

tee start_phone_system.sh > /dev/null <<'EOF'
#!/bin/bash
# Startup script for phone gossip system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Phone Gossip System Starting ==="
echo "Directory: $SCRIPT_DIR"
echo "Time: $(date)"

# Wait for audio system to be ready
echo "Waiting for audio system..."
sleep 5

# Check if virtual environment exists
if [ ! -d "phone_env" ]; then
    echo "❌ Virtual environment not found at phone_env"
    exit 1
fi

# Check if main script exists
if [ ! -f "phone_system.py" ]; then
    echo "❌ phone_system.py not found"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found - API keys missing"
    exit 1
fi

# Check if audio files exist
if [ ! -f "welcome.mp3" ] || [ ! -f "transition.mp3" ]; then
    echo "🎵 Generating missing audio files..."
    source phone_env/bin/activate
    python create_welcome.py
    if [ $? -ne 0 ]; then
        echo "❌ Failed to generate audio files"
        exit 1
    fi
fi

# Activate virtual environment and run
echo "🚀 Starting phone system..."
source phone_env/bin/activate
python phone_system.py
EOF

chmod +x start_phone_system.sh
echo "✅ Startup script created: start_phone_system.sh"

# 3. Create a manual control script
echo "📝 Creating control script..."

tee control_phone_system.sh > /dev/null <<EOF
#!/bin/bash
# Control script for phone gossip system service

SERVICE_NAME="$SERVICE_NAME"

case "\$1" in
    start)
        echo "Starting \$SERVICE_NAME..."
        sudo systemctl start \$SERVICE_NAME
        ;;
    stop)
        echo "Stopping \$SERVICE_NAME..."
        sudo systemctl stop \$SERVICE_NAME
        ;;
    restart)
        echo "Restarting \$SERVICE_NAME..."
        sudo systemctl restart \$SERVICE_NAME
        ;;
    status)
        sudo systemctl status \$SERVICE_NAME
        ;;
    logs)
        sudo journalctl -u \$SERVICE_NAME -f
        ;;
    enable)
        echo "Enabling \$SERVICE_NAME to start on boot..."
        sudo systemctl enable \$SERVICE_NAME
        ;;
    disable)
        echo "Disabling \$SERVICE_NAME from starting on boot..."
        sudo systemctl disable \$SERVICE_NAME
        ;;
    *)
        echo "Usage: \$0 {start|stop|restart|status|logs|enable|disable}"
        echo
        echo "Commands:"
        echo "  start    - Start the service now"
        echo "  stop     - Stop the service now"
        echo "  restart  - Restart the service now"
        echo "  status   - Show service status"
        echo "  logs     - Show live logs"
        echo "  enable   - Enable auto-start on boot"
        echo "  disable  - Disable auto-start on boot"
        exit 1
        ;;
esac
EOF

chmod +x control_phone_system.sh
echo "✅ Control script created: control_phone_system.sh"

# 4. Set up the service
echo "🔧 Configuring systemd service..."

# Reload systemd
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable ${SERVICE_NAME}

echo "✅ Service enabled for auto-start on boot"

# 5. Configure auto-login (optional)
echo
read -p "Do you want to enable auto-login for user '$CURRENT_USER'? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔑 Configuring auto-login..."
    
    # Create override directory
    sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
    
    # Create auto-login override
    sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf > /dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $CURRENT_USER --noclear %I \$TERM
EOF
    
    echo "✅ Auto-login configured for $CURRENT_USER"
fi

# 6. Disable unnecessary services for kiosk mode
echo
read -p "Do you want to disable unnecessary services for kiosk mode? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "⚡ Optimizing for kiosk mode..."
    
    # Disable unnecessary services
    sudo systemctl disable bluetooth.service
    sudo systemctl disable wpa_supplicant.service  # Only if using ethernet
    sudo systemctl disable avahi-daemon.service
    sudo systemctl disable triggerhappy.service
    
    echo "✅ Unnecessary services disabled"
fi

echo
echo "=== Kiosk Mode Setup Complete! ==="
echo
echo "The phone system will now start automatically on boot."
echo
echo "Control commands:"
echo "  ./control_phone_system.sh start    - Start now"
echo "  ./control_phone_system.sh stop     - Stop now"
echo "  ./control_phone_system.sh status   - Check status"
echo "  ./control_phone_system.sh logs     - View logs"
echo
echo "To test the setup:"
echo "1. sudo reboot"
echo "2. The system should start automatically after boot"
echo
echo "To disable auto-start:"
echo "  ./control_phone_system.sh disable"
echo
echo "Logs can be viewed with:"
echo "  sudo journalctl -u $SERVICE_NAME -f"
EOF

chmod +x setup_kiosk_mode.sh