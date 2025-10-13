#!/bin/bash
# Setup script for persistent audio level control

echo "=== Audio Level Control Setup ==="

CURRENT_USER=$(whoami)
SCRIPT_DIR=$(pwd)
SERVICE_NAME="audio-level-control"

echo "Setting up persistent audio level control..."
echo "User: $CURRENT_USER"
echo "Directory: $SCRIPT_DIR"
echo

# Create systemd service for audio level control
echo "Creating systemd service for audio level control..."

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Audio Level Control for Phone System
After=sound.service
Wants=sound.service

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
Environment=PATH=$SCRIPT_DIR/env/bin
ExecStart=$SCRIPT_DIR/env/bin/python $SCRIPT_DIR/audio_level_controller.py 85 60
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"

# Reload systemd and enable service
echo "Enabling audio level control service..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}

echo "✅ Service enabled for auto-start"

# Set initial audio levels
echo "Setting initial audio levels..."
chmod +x set_audio_levels.sh
./set_audio_levels.sh 85

# Start the service
echo "Starting audio level control service..."
sudo systemctl start ${SERVICE_NAME}

# Show status
echo "Service status:"
sudo systemctl status ${SERVICE_NAME} --no-pager -l

echo
echo "=== Setup Complete ==="
echo
echo "Audio level control is now running and will:"
echo "  • Maintain volume at 85%"
echo "  • Check levels every 60 seconds"
echo "  • Start automatically on boot"
echo "  • Restart if it crashes"
echo
echo "Control commands:"
echo "  sudo systemctl status audio-level-control    # Check status"
echo "  sudo systemctl restart audio-level-control   # Restart service"
echo "  sudo systemctl stop audio-level-control      # Stop service"
echo "  sudo journalctl -u audio-level-control -f    # View logs"
echo
echo "Manual commands:"
echo "  ./set_audio_levels.sh 90                     # Set levels to 90%"
echo "  python3 audio_level_controller.py 80 30      # Run with custom settings"