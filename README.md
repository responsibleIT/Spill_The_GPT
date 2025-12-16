# 🗣️ Spill The GPT

An interactive AI gossip installation created for Dutch Design Week 2025. This system transforms personal stories into anonymized gossip using AI, creating a chain of whispered secrets through an old telephone handset.

## 🎯 Overview

**Spill The GPT** is an interactive art installation that uses AI to collect, anonymize, and share gossip. Users pick up an old telephone, hear gossip from a previous participant, then share their own story. The system uses OpenAI's Whisper for speech recognition, GPT-4 for text transformation, and ElevenLabs for text-to-speech, creating an endless chain of anonymous stories.

### Two Modes of Operation

1. **Web Interface** (`app.py`) - Browser-based gossip collection for development and testing
2. **Phone System** (`enhanced_phone_system.py`) - Raspberry Pi installation with physical telephone handset

## 🎭 How It Works

### Enhanced User Flow:
1. **📞 Phone Pickup** - User lifts the handset
2. **🔊 Welcome Message** - "Welcome to the gossip system. First you will hear gossip from a previous user."
3. **🎧 Previous Gossip** - Plays a random gossip from the database
4. **🔄 Transition Message** - "Now it's your turn. Tell your gossip and hang up when you're done."
5. **🎙️ Recording** - User speaks their gossip
6. **📞 Phone Hangup** - Stops recording and begins processing
7. **🤖 AI Processing Chain**:
   - Whisper transcribes the audio to text
   - GPT-4 transforms it into anonymized gossip
   - ElevenLabs converts it back to speech (Dutch voice)
8. **💾 Storage** - Saved in SQLite database for future playback
9. **🔁 Loop** - Next user hears this gossip

## 🛠️ Hardware Requirements

### For Raspberry Pi Installation:
- Raspberry Pi (3B+ or newer recommended)
- Old telephone handset with hookswitch
- Magnetic reed switch or button sensor (hookswitch detection)
- USB microphone or Raspberry Pi audio HAT
- Speaker or amplified audio output
- Jumper wires and breadboard
- Power supply for Raspberry Pi

### GPIO Wiring:
- **Hookswitch Sensor**: GPIO 18 (configurable)
- **Ground**: GND pin
- **Power**: 3.3V (if needed)

## 📦 Installation

### Prerequisites

#### 1. System Dependencies (Raspberry Pi)
```bash
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio alsa-utils pulseaudio
```

#### 2. Python Environment
```bash
# Create virtual environment
python3 -m venv env

# Activate environment
# On Linux/Mac:
source env/bin/activate
# On Windows:
env\Scripts\activate

# Install dependencies
pip install -r requirements_enhanced.txt
```

#### 3. API Keys Setup

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

Or export as environment variables:
```bash
export OPENAI_API_KEY="your_openai_api_key"
export ELEVENLABS_API_KEY="your_elevenlabs_api_key"
```

#### 4. Generate Welcome Audio Messages

```bash
python create_audio_messages.py
```

This creates:
- `welcome.mp3` - Initial greeting
- `transition.mp3` - "Now it's your turn" message

## 🚀 Running the System

### Web Interface Mode (Development/Testing)

```bash
python app.py
```

Access at `http://localhost:5000`

Features:
- Record audio through browser
- Transcribe and process gossip
- View gossip loop of all collected audio

### Phone System Mode (Raspberry Pi)

```bash
python enhanced_phone_system.py
```

The system will wait for the phone to be picked up and automatically handle the interaction flow.

## 📂 Project Structure

```
Spill_The_GPT/
├── app.py                          # Flask web application
├── enhanced_phone_system.py        # Main phone system for Raspberry Pi
├── gossip_database.py              # SQLite database management
├── el.py                           # ElevenLabs TTS integration
├── create_audio_messages.py        # Generate welcome/transition audio
├── requirements.txt                # Web app dependencies
├── requirements_enhanced.txt       # Enhanced system dependencies
├── templates/                      # HTML templates
│   ├── index.html                 # Main web interface
│   └── gossip_loop.html           # Continuous gossip playback
├── Raspberry_Pi_setup/            # Raspberry Pi specific files
│   ├── phone_system.py            # Main phone system for Raspberry Pi
│   ├── gossip_database.py         # Database handler
│   ├── el.py                      # ElevenLabs TTS handler
│   ├── create_welcome.py          # Welcome audio generator
│   ├── requirements_phone.txt     # Pi dependencies
│   ├── PHONE_SETUP.md            # Detailed setup guide
│   ├── CLEAN_PI_SETUP.md         # Clean installation guide
│   ├── setup_clean_pi.sh         # Automated installation script
│   ├── setup_kiosk_mode.sh       # Auto-start configuration script
│   ├── test_audio_devices.py     # Audio device diagnostics
│   ├── test_microphone.py        # Microphone testing utility
│   └── gpio_test.py              # GPIO testing utility
├── audio/                         # Generated gossip audio files
├── gossip.db                      # SQLite database (auto-created)
├── welcome.mp3                    # Welcome message audio
└── transition.mp3                 # Transition message audio
```

## 🔧 Configuration

### Phone System Settings

Edit `enhanced_phone_system.py`:

```python
HORN_BUTTON_PIN = 18        # GPIO pin for hookswitch
AUDIO_RATE = 44100          # Recording sample rate
AUDIO_CHANNELS = 1          # Mono recording
AUDIO_CHUNK = 1024          # Audio buffer size
```

### Audio Device Configuration

Test and configure audio devices:

```bash
# List audio devices
aplay -l     # Playback devices
arecord -l   # Recording devices

# Test microphone
arecord -D plughw:1,0 -d 5 test.wav
aplay test.wav

# Adjust audio levels
alsamixer
```

### Voice Customization

Edit `el.py` to change the ElevenLabs voice:

```python
voice_id="ANHrhmaFeVN0QJaa0PhL"  # Currently: Petra (Flemish)
model_id="eleven_turbo_v2_5"      # Turbo model for low latency
```

## 🗄️ Database Structure

SQLite database (`gossip.db`) automatically created with:

```sql
CREATE TABLE gossip (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    original_text TEXT,              -- Raw transcription
    gossip_text TEXT,                -- GPT-4 anonymized version
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,
    file_size_bytes INTEGER,
    is_active BOOLEAN DEFAULT 1
)
```

### Database Features:
- **Automatic Creation**: No manual setup required
- **Random Selection**: Fair distribution of previous gossip
- **Persistent Storage**: Survives system restarts
- **File Cleanup**: Automatically handles missing audio files
- **Metadata Tracking**: Records timestamps, file sizes, and durations

## 🎨 Kiosk Mode Setup (Auto-Start on Boot)

### Quick Setup

Run the automated script:

```bash
cd Raspberry_Pi_setup
chmod +x setup_kiosk_mode.sh
./setup_kiosk_mode.sh
```

### Manual Systemd Service Setup

Create service file:

```bash
sudo nano /etc/systemd/system/phone-gossip.service
```

Add configuration:

```ini
[Unit]
Description=Phone Gossip System
After=network.target sound.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Spill_The_GPT
Environment=PATH=/home/pi/Spill_The_GPT/env/bin
ExecStart=/home/pi/Spill_The_GPT/env/bin/python enhanced_phone_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable phone-gossip.service
sudo systemctl start phone-gossip.service
```

## 🧪 Testing & Troubleshooting

### Audio Device Testing
```bash
cd Raspberry_Pi_setup
python test_audio_devices.py    # List and test all audio devices
python test_microphone.py        # Record and playback test
```

### GPIO Testing
```bash
cd Raspberry_Pi_setup
python gpio_test.py              # Test hookswitch button
```

### Common Issues

#### Audio Not Working
- Check device permissions: `sudo usermod -a -G audio $USER`
- Verify audio devices with `aplay -l` and `arecord -l`
- Test with `speaker-test` and `arecord`
- Adjust levels in `alsamixer`

#### GPIO Issues
- Verify wiring connections
- Check pin permissions
- Test with `gpio readall` (install `wiringpi`)
- Ensure correct pin numbering (BCM vs BOARD)

#### Database Issues
- Check file permissions in project directory
- Verify database with: `sqlite3 gossip.db ".tables"`
- Database auto-creates on first run

#### Performance Issues
- Use Whisper "tiny" model for faster transcription
- Monitor CPU temperature: `vcgencmd measure_temp`
- Consider using lighter weight models
- Reduce audio quality if needed

## 🌐 Web Interface Features

Access the web interface at `http://localhost:5000`

### Main Interface (`/`)
- Record audio directly in browser
- Live transcription
- GPT-4 anonymization
- Text-to-speech playback

### Gossip Loop (`/gossip-loop`)
- Continuous playback of all gossip
- Auto-advancing carousel
- Background installation mode

## 🔐 Security & Privacy

- **Anonymization**: GPT-4 removes personally identifiable information
- **No User Tracking**: System doesn't store user identities
- **Local Storage**: All data stored locally in SQLite
- **Audio Cleanup**: Temporary recordings automatically deleted
- **API Keys**: Store in `.env` file (not in version control)

## 🎯 Use Cases

1. **Art Installations**: Interactive gallery pieces
2. **Events**: Dutch Design Week, festivals, exhibitions
3. **Research**: Social interaction and AI studies
4. **Education**: Demonstrating AI pipeline (STT → LLM → TTS)

## 📝 Development Notes

### First User Experience
- When no previous gossip exists, system handles gracefully
- First gossip becomes available for second user
- Database grows organically with each interaction

### Whisper Model Options
- `tiny`: Fastest, lowest accuracy (recommended for Pi)
- `base`: Good balance
- `small`: Better accuracy, slower
- `medium`/`large`: Best accuracy, very slow on Pi

### ElevenLabs Configuration
- Currently uses Dutch/Flemish voice (Petra)
- Turbo model for low latency
- Configurable speed, stability, and similarity

## 🤝 Contributing

This project was created for Dutch Design Week 2025. Feel free to fork and adapt for your own installations.

## 📄 License

Created for Dutch Design Week 2025

## 🙏 Acknowledgments

- **OpenAI**: Whisper and GPT-4 models
- **ElevenLabs**: Text-to-speech voice synthesis
- **Dutch Design Week**: Exhibition platform

## 📞 Support

For issues or questions, please refer to the setup guides:
- `Raspberry_Pi_setup/PHONE_SETUP.md` - Phone system guide
- `Raspberry_Pi_setup/CLEAN_PI_SETUP.md` - Clean installation guide
- `ENHANCED_SYSTEM.md` - Enhanced features documentation

---

**Project**: Spill The GPT  
**Event**: Dutch Design Week 2025  
**Type**: Interactive AI Art Installation
