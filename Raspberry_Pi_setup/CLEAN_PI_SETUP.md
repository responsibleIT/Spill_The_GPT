# Clean Raspberry Pi Setup Guide

## Prerequisites Checklist

### 1. Required Files
Make sure you have these files on your Pi:
- `phone_system.py` (main application)
- `gossip_database.py` (database handler)
- `el.py` (ElevenLabs TTS functions)
- `create_welcome.py` (to generate welcome messages)
- `requirements_phone.txt` (dependencies)

### 2. API Keys Setup
Create a `.env` file in the same directory with your API keys:

```bash
echo 'OPENAI_API_KEY=your_openai_api_key_here' > .env
echo 'ELEVENLABS_API_KEY=your_elevenlabs_api_key_here' >> .env
```

### 3. System Dependencies
Install system audio packages:
```bash
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio alsa-utils pulseaudio
```

### 4. Python Environment
```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install requirements
pip install -r requirements_phone.txt
```

### 5. Audio Setup
Test your audio devices:
```bash
# List audio devices
aplay -l
arecord -l

# Test microphone
arecord -D plughw:1,0 -d 5 test.wav
aplay test.wav
```

### 6. Generate Welcome Messages
Run this to create the Dutch welcome/transition audio files:
```bash
python create_welcome.py
```

This should create:
- `welcome.mp3`
- `transition.mp3`

### 7. GPIO Setup (if using physical button)
Make sure your button is connected to GPIO pin 4 and ground.

### 8. Test Audio Devices
Run the diagnostic tool:
```bash
python fix_audio.py
```

### 9. Permission Setup
Add your user to audio group:
```bash
sudo usermod -a -G audio $USER
```

Log out and back in for this to take effect.

## Quick Test Run

### Test 1: Audio Devices
```bash
python test_audio_devices.py
```

### Test 2: Microphone
```bash
python test_microphone.py
```

### Test 3: GPIO (if using button)
```bash
python gpio_test.py
```

## Final Launch

### Start the Phone System
```bash
python phone_system.py
```

## Kiosk Mode Setup (Auto-Start on Boot)

### Quick Kiosk Setup
Run the automated setup script:
```bash
chmod +x setup_kiosk_mode.sh
./setup_kiosk_mode.sh
```

This will:
- Create a systemd service for auto-start
- Set up control scripts
- Optionally configure auto-login
- Optimize system for kiosk mode

### Manual Kiosk Configuration

#### 1. Create Systemd Service
```bash
sudo nano /etc/systemd/system/phone-gossip.service
```

Add this content (replace `pi` with your username and adjust paths):
```ini
[Unit]
Description=Phone Gossip System
After=network.target sound.service
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/phone_system
Environment=PATH=/home/pi/phone_system/env/bin
ExecStart=/home/pi/phone_system/env/bin/python /home/pi/phone_system/phone_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### 2. Enable the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable phone-gossip.service
```

#### 3. Control Commands
After setup, use these commands:
```bash
./control_phone_system.sh start    # Start now
./control_phone_system.sh stop     # Stop now
./control_phone_system.sh status   # Check status
./control_phone_system.sh logs     # View live logs
./control_phone_system.sh restart  # Restart service
```

#### 4. Auto-Login (Optional)
```bash
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo nano /etc/systemd/system/getty@tty1.service.d/override.conf
```

Add:
```ini
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM
```

### Kiosk Mode Features
- ✅ **Auto-start on boot** - System starts immediately when Pi powers on
- ✅ **Auto-restart** - If the system crashes, it automatically restarts
- ✅ **Network waiting** - Waits for internet before starting (for API calls)
- ✅ **Audio setup** - Ensures audio system is ready before starting
- ✅ **Error recovery** - Robust error handling and logging
- ✅ **Status monitoring** - Easy to check system status and logs

### Troubleshooting Kiosk Mode

#### Check Service Status
```bash
sudo systemctl status phone-gossip
```

#### View Logs
```bash
sudo journalctl -u phone-gossip -f
```

#### Test Service Manually
```bash
sudo systemctl start phone-gossip
./control_phone_system.sh logs
```

#### Disable Auto-Start (if needed)
```bash
sudo systemctl disable phone-gossip
```

## Expected Output
You should see:
```
Enhanced phone system initialized. Waiting for phone pickup...
Current gossip count in database: 0
Enhanced phone system ready!
Flow: Welcome → Previous Gossip → Transition → Record → Process → Save
```

## Common Issues & Solutions

### Issue 1: "No module named 'gpiozero'"
**Solution:** Make sure you're in your virtual environment:
```bash
source env/bin/activate
pip install gpiozero
```

### Issue 2: "No such file or directory: 'welcome.mp3'"
**Solution:** Run the welcome message generator:
```bash
python create_welcome.py
```

### Issue 3: Audio device errors
**Solution:** Check your audio setup:
```bash
python fix_audio.py
# Follow the recommendations
```

### Issue 4: "Invalid number of channels"
**Solution:** The system now auto-detects and adjusts. If it persists, edit `phone_system.py`:
```python
FORCE_AUDIO_DEVICE = None  # Let it auto-detect
```

### Issue 5: API key errors
**Solution:** Check your `.env` file:
```bash
cat .env
```
Make sure both API keys are present and valid.

### Issue 6: Service won't start on boot
**Solution:** Check service status and logs:
```bash
sudo systemctl status phone-gossip
sudo journalctl -u phone-gossip
```

Common fixes:
- Wrong file paths in service file
- Missing virtual environment
- Permission issues
- Network not ready

## Hardware Requirements

### Minimum Setup
- Raspberry Pi 3B+ or newer
- USB microphone or USB audio card
- Speaker or headphones
- Internet connection

### Recommended Setup  
- Raspberry Pi 4
- KT USB Audio card (or similar USB audio interface)
- Button connected to GPIO pin 4 and ground
- Powered speakers
- Status LED on GPIO pin 18 (optional)

## File Structure
After setup, you should have:
```
Raspberry_Pi_setup/
├── phone_system.py              # Main application
├── gossip_database.py           # Database functions
├── el.py                        # TTS functions
├── create_welcome.py            # Audio message generator
├── setup_kiosk_mode.sh          # Kiosk mode setup script
├── control_phone_system.sh      # Service control script
├── boot_status.py               # Boot status checker
├── .env                         # API keys
├── welcome.mp3                  # Generated welcome message
├── transition.mp3               # Generated transition message
├── phone_recording.wav          # Temporary recording file
└── gossip_database.db           # SQLite database (created automatically)
```

## Success Indicators

✅ **System Ready:** "Enhanced phone system ready!" message appears
✅ **Audio Working:** You can hear welcome messages
✅ **Recording Working:** Microphone captures audio
✅ **API Working:** Fast transcription via OpenAI API
✅ **TTS Working:** ElevenLabs generates speech
✅ **Database Working:** Gossip is saved and retrieved
✅ **Kiosk Mode:** System starts automatically on boot
✅ **Auto-Recovery:** System restarts if it crashes

## Production Deployment Checklist

- [ ] All tests pass (`python test_*.py`)
- [ ] API keys configured in `.env`
- [ ] Audio files generated (`welcome.mp3`, `transition.mp3`)
- [ ] Kiosk mode setup completed
- [ ] Service starts on boot
- [ ] Audio devices working correctly
- [ ] Network connectivity confirmed
- [ ] Physical button connected (if using)
- [ ] Power supply adequate for Pi + audio equipment

If all these work, your system is ready for production! 🎉

## Kiosk Mode Summary

**Turn on Pi → System automatically starts → Ready to receive calls!**

The Pi becomes a dedicated gossip phone device that:
1. **Boots up** and automatically starts the phone system
2. **Waits for calls** (button press or simulation)
3. **Handles everything** - welcome, recording, processing, storage
4. **Recovers automatically** if anything goes wrong
5. **Runs forever** until manually stopped or powered off