#!/bin/bash
# Simple audio device testing script for Raspberry Pi

echo "=== Audio Device Testing ==="
echo

echo "1. Checking ALSA devices..."
echo "Available capture devices:"
arecord -l 2>/dev/null || echo "arecord not available or no devices found"
echo

echo "Available playback devices:"
aplay -l 2>/dev/null || echo "aplay not available or no devices found"
echo

echo "2. Testing default microphone with arecord..."
echo "Recording 3 seconds of audio..."
if command -v arecord &> /dev/null; then
    arecord -d 3 -f cd -t wav mic_test_alsa.wav 2>/dev/null && echo "✓ ALSA recording successful - saved as mic_test_alsa.wav" || echo "✗ ALSA recording failed"
else
    echo "arecord command not available"
fi
echo

echo "3. Checking PulseAudio (if available)..."
if command -v pactl &> /dev/null; then
    echo "PulseAudio sources:"
    pactl list sources short 2>/dev/null || echo "PulseAudio not running or no sources"
    echo
    echo "PulseAudio sinks:"
    pactl list sinks short 2>/dev/null || echo "PulseAudio not running or no sinks"
else
    echo "PulseAudio not available"
fi
echo

echo "4. Checking USB audio devices..."
echo "USB audio devices in lsusb:"
lsusb | grep -i audio || echo "No USB audio devices found"
echo

echo "5. Checking /proc/asound/cards..."
if [ -f /proc/asound/cards ]; then
    cat /proc/asound/cards
else
    echo "/proc/asound/cards not found"
fi
echo

echo "6. Quick microphone level test..."
echo "If you have a working microphone, you should see activity in:"
echo "  alsamixer (press F4 for capture devices)"
echo "  or run: amixer sget Capture"
echo

if command -v amixer &> /dev/null; then
    echo "Current capture settings:"
    amixer sget Capture 2>/dev/null || echo "No capture controls found"
else
    echo "amixer not available"
fi

echo
echo "=== Recommendations ==="
echo "1. If you see audio devices above, try:"
echo "   - Check alsamixer capture levels (F4 key)"
echo "   - Run: python3 test_microphone.py"
echo
echo "2. If no devices found:"
echo "   - Check USB connections"
echo "   - Run: sudo lsmod | grep snd"
echo "   - Check: dmesg | grep audio"
echo
echo "3. For Raspberry Pi built-in audio:"
echo "   - Enable with: sudo raspi-config → Advanced → Audio"
echo "   - Or add 'dtparam=audio=on' to /boot/config.txt"