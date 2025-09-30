# Enhanced Phone Gossip System Setup Guide

## 🎯 Enhanced User Experience

The system now provides this enhanced flow:
1. **📞 Phone Pickup** → Welcome message
2. **🎭 Previous Gossip** → Plays random gossip from database  
3. **🔄 Transition** → "Now it's your turn" message
4. **🎙️ Recording** → User speaks their gossip
5. **📞 Phone Hangup** → AI processing and database storage

## Hardware Setup

### Components Needed:
- Raspberry Pi (3B+ or newer)
- Old telephone handset
- Magnetic switch or button sensor for handset detection
- USB microphone (or Pi audio HAT)
- Speaker or audio output
- Jumper wires and breadboard

### GPIO Wiring:
- Button/switch: GPIO 18 (configurable in phone_system.py)
- Ground: GND pin
- Power: 3.3V (if needed for switch)

## Software Installation

### 1. Install Dependencies:
```bash
pip install -r requirements_phone.txt
```

### 2. Set Environment Variables:
```bash
export OPENAI_API_KEY="your_openai_api_key"
export ELEVENLABS_API_KEY="your_elevenlabs_api_key"
```

### 3. Create Audio Messages:
```bash
python create_welcome.py
```
This creates both:
- `welcome.mp3` - Initial greeting
- `transition.mp3` - "Now it's your turn" message

### 4. Run the Enhanced Phone System:
```bash
python phone_system.py
```

## How It Works

### Enhanced Flow:
1. **Phone Pickup**: User lifts phone horn
2. **Welcome Message**: "Welcome to the gossip system. First you will hear gossip from a previous user."
3. **Previous Gossip**: Random gossip from database plays
4. **Transition Message**: "Now it's your turn. Tell your gossip and hang up when you're done."
5. **Recording**: User speaks their gossip
6. **Phone Hangup**: System processes and saves to database
7. **Processing**: Whisper → GPT → ElevenLabs → Database storage

### Database Features:
- **SQLite Database**: Automatic creation and management
- **Random Selection**: Fair distribution of previous gossip
- **Persistent Storage**: Gossip survives system restarts
- **File Management**: Cleanup of missing audio files

## Configuration

### Audio Settings (in phone_system.py):
- `HORN_BUTTON_PIN`: GPIO pin for horn detection (default: 18)
- `AUDIO_RATE`: Recording sample rate (44100 Hz)
- `AUDIO_CHANNELS`: Mono (1) or Stereo (2)

### File Structure:
```
Raspberry_Pi_setup/
├── phone_system.py      # Main enhanced system
├── gossip_database.py   # Database management
├── create_welcome.py    # Audio message generator
├── el.py               # ElevenLabs TTS interface
├── requirements_phone.txt
├── PHONE_SETUP.md
├── audio/              # Generated gossip files
├── gossip.db           # SQLite database
├── welcome.mp3         # Welcome message
├── transition.mp3      # Transition message
└── phone_recording.wav # Temporary recording file
```

## Troubleshooting

### Audio Issues:
- Check microphone permissions
- Verify speaker output device
- Adjust audio levels in `alsamixer`

### GPIO Issues:
- Verify wiring connections
- Check GPIO pin permissions
- Test button with `gpio readall`

### Database Issues:
- Database auto-creates on first run
- Check file permissions in directory
- Use `sqlite3 gossip.db .tables` to verify

### Performance:
- Use "tiny" Whisper model for speed
- Consider warming up models on startup
- Monitor Pi temperature under load

## First User Experience:
- When no previous gossip exists, system gracefully handles the situation
- Each subsequent user adds to the growing gossip collection
- Creates an ever-expanding chain of anonymous stories