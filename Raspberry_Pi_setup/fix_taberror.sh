#!/bin/bash
# Quick fix script for the TabError issue

echo "=== Fixing Phone System TabError ==="
echo

# Stop the service to prevent continuous restart attempts
echo "🛑 Stopping service to prevent restart loop..."
sudo systemctl stop phone-gossip

echo "🔧 Fixing indentation issues..."

# Run the Python indentation fixer
python3 fix_indentation.py

echo "🧪 Testing syntax..."
if python3 -m py_compile phone_system.py; then
    echo "✅ Python syntax is now valid"
    
    echo "🚀 Restarting service..."
    sudo systemctl start phone-gossip
    
    echo "📊 Checking status..."
    sudo systemctl status phone-gossip --no-pager -l
    
    echo
    echo "Monitor logs with:"
    echo "  sudo journalctl -u phone-gossip -f"
    
else
    echo "❌ Syntax errors still exist. Manual fix required."
    echo "   Check the output above for specific error details."
fi