#!/bin/bash
# Quick script to set and maintain audio levels on Raspberry Pi

echo "=== Raspberry Pi Audio Level Setup ==="

# Function to set audio level
set_audio_level() {
    local volume=$1
    local control=$2
    
    echo "Setting $control to $volume%..."
    
    # Try with specific card first (USB audio)
    if amixer -c 1 set "$control" "${volume}%" 2>/dev/null; then
        echo "  ✓ Set $control on card 1"
    elif amixer -c 0 set "$control" "${volume}%" 2>/dev/null; then
        echo "  ✓ Set $control on card 0"
    elif amixer set "$control" "${volume}%" 2>/dev/null; then
        echo "  ✓ Set $control on default card"
    else
        echo "  ✗ Could not set $control"
    fi
}

# Function to show current levels
show_audio_levels() {
    echo "Current audio levels:"
    
    # Show levels for different cards
    for card in 0 1 2; do
        if amixer -c $card info >/dev/null 2>&1; then
            echo "  Card $card:"
            for control in PCM Master Speaker Headphone Digital Capture; do
                level=$(amixer -c $card get "$control" 2>/dev/null | grep -o '\[.*%\]' | head -1)
                if [ -n "$level" ]; then
                    echo "    $control: $level"
                fi
            done
        fi
    done
}

# Set target volume (default 85%)
TARGET_VOLUME=${1:-85}

echo "Target volume: $TARGET_VOLUME%"
echo

# Show current levels
show_audio_levels
echo

# Set levels for common controls
echo "Setting audio levels to $TARGET_VOLUME%..."
for control in PCM Master Speaker Headphone Digital; do
    set_audio_level $TARGET_VOLUME "$control"
done

echo

# Set capture level (for microphone)
echo "Setting microphone capture level..."
for control in Capture Mic; do
    set_audio_level 90 "$control"  # Higher for microphone
done

echo

# Show final levels
show_audio_levels

echo
echo "=== Audio Setup Complete ==="
echo
echo "To maintain levels automatically, run:"
echo "  python3 audio_level_controller.py $TARGET_VOLUME"
echo
echo "To check levels manually:"
echo "  alsamixer"
echo "  amixer"