#!/usr/bin/env python3
"""
Quick audio configuration fix for the phone system
This script helps identify and resolve common audio issues
"""

def fix_audio_configuration():
    """Apply quick fixes for common audio issues"""
    
    print("=== Phone System Audio Fix ===\n")
    
    fixes_applied = []
    
    # Fix 1: Check if the audio device force setting is appropriate
    print("1. Checking FORCE_AUDIO_DEVICE setting...")
    
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        
        # Check if device 3 (commonly KT USB Audio) exists and works
        if audio.get_device_count() > 3:
            try:
                device_info = audio.get_device_info_by_index(3)
                device_name = device_info['name']
                print(f"   Device 3 found: {device_name}")
                
                if device_info['maxInputChannels'] > 0:
                    # Test mono recording on device 3
                    try:
                        test_stream = audio.open(
                            format=pyaudio.paInt16,
                            channels=1,  # Force mono
                            rate=44100,
                            input=True,
                            input_device_index=3,
                            frames_per_buffer=1024
                        )
                        test_stream.close()
                        print("   ✓ Device 3 supports mono recording")
                        fixes_applied.append("Device 3 mono recording verified")
                    except Exception as e:
                        print(f"   ✗ Device 3 mono recording failed: {e}")
                        print("   → Recommendation: Set FORCE_AUDIO_DEVICE = None to use default")
                        fixes_applied.append("Recommend using default audio device")
                else:
                    print("   ✗ Device 3 has no input channels")
                    fixes_applied.append("Device 3 not suitable for recording")
            except Exception as e:
                print(f"   ✗ Cannot access device 3: {e}")
                fixes_applied.append("Device 3 not accessible")
        else:
            print("   ✗ Device 3 not found")
            fixes_applied.append("Device 3 does not exist")
        
        audio.terminate()
        
    except ImportError:
        print("   ✗ PyAudio not available")
        fixes_applied.append("PyAudio import failed")
    except Exception as e:
        print(f"   ✗ Audio system error: {e}")
        fixes_applied.append(f"Audio system error: {e}")
    
    # Fix 2: Check Whisper installation
    print("\n2. Checking Whisper installation...")
    try:
        import whisper
        print("   ✓ Whisper is installed")
        
        # Try loading a model
        try:
            model = whisper.load_model("tiny")
            print("   ✓ Whisper tiny model loads successfully")
            fixes_applied.append("Whisper working correctly")
        except Exception as e:
            print(f"   ✗ Whisper model loading failed: {e}")
            fixes_applied.append(f"Whisper model error: {e}")
            
    except ImportError:
        print("   ✗ Whisper not installed")
        print("   → Run: pip install openai-whisper")
        fixes_applied.append("Whisper needs installation")
    
    # Fix 3: Check required audio files
    print("\n3. Checking audio files...")
    import os
    
    welcome_file = "welcome_message.mp3"
    transition_file = "transition_message.mp3"
    
    if os.path.exists(welcome_file):
        print(f"   ✓ {welcome_file} found")
    else:
        print(f"   ✗ {welcome_file} missing")
        print("   → Run create_welcome.py to generate audio files")
        fixes_applied.append("Missing welcome audio file")
    
    if os.path.exists(transition_file):
        print(f"   ✓ {transition_file} found")
    else:
        print(f"   ✗ {transition_file} missing")
        print("   → Run create_welcome.py to generate audio files")
        fixes_applied.append("Missing transition audio file")
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Issues found: {len(fixes_applied)}")
    for i, fix in enumerate(fixes_applied, 1):
        print(f"{i}. {fix}")
    
    # Generate a configuration recommendation
    print(f"\n=== Configuration Recommendation ===")
    
    config_lines = []
    
    # Audio device recommendation
    if any("Device 3" in fix and "verified" in fix for fix in fixes_applied):
        config_lines.append("FORCE_AUDIO_DEVICE = 3  # KT USB Audio device working")
    else:
        config_lines.append("FORCE_AUDIO_DEVICE = None  # Use default audio device")
    
    # Audio settings
    config_lines.append("AUDIO_CHANNELS = 1  # Mono recording for better compatibility")
    config_lines.append("AUDIO_RATE = 44100  # Standard sample rate")
    
    print("Add these lines to the top of phone_system.py:")
    for line in config_lines:
        print(f"  {line}")

if __name__ == "__main__":
    fix_audio_configuration()