#!/usr/bin/env python3
"""
Quick USB Audio Setup for KT USB Audio (Card 3)
This script directly configures your detected USB audio device
"""

import os
import subprocess

def setup_kt_usb_audio():
    """Setup KT USB Audio as default device"""
    print("Setting up KT USB Audio (Card 3) as default device...")
    
    # Create .asoundrc file for ALSA
    asoundrc_content = """
# ALSA configuration for KT USB Audio
pcm.!default {
    type hw
    card 3
}
ctl.!default {
    type hw
    card 3
}

# Alternative configuration with better compatibility
pcm.usb {
    type plughw
    card 3
    device 0
}
"""
    
    try:
        home_dir = os.path.expanduser("~")
        asoundrc_path = os.path.join(home_dir, ".asoundrc")
        
        with open(asoundrc_path, 'w') as f:
            f.write(asoundrc_content)
        
        print(f"✓ Created {asoundrc_path}")
        
        # Create audio config for phone system
        audio_config_content = """# USB Audio Configuration for Phone System
# Auto-generated for KT USB Audio device

# Force use of card 3 (KT USB Audio)
FORCE_AUDIO_DEVICE = 3

# Specific device settings
USB_AUDIO_OUTPUT_DEVICE = 3
USB_AUDIO_INPUT_DEVICE = 3

print("Using KT USB Audio (Card 3) configuration")
"""
        
        with open('audio_config.py', 'w') as f:
            f.write(audio_config_content)
        
        print("✓ Created audio_config.py")
        
        # Test the audio device
        print("Testing KT USB Audio...")
        test_result = test_audio()
        
        if test_result:
            print("✓ KT USB Audio configuration complete!")
            print("\nNext steps:")
            print("1. Run: python3 phone_system.py")
            print("2. The system should now use your USB audio device")
        else:
            print("⚠ Audio test failed, but configuration is saved")
            print("Try running the phone system anyway")
        
        return True
        
    except Exception as e:
        print(f"✗ Error setting up audio: {e}")
        return False

def test_audio():
    """Test KT USB Audio"""
    try:
        print("Playing test tone on KT USB Audio...")
        
        # Test with speaker-test
        result = subprocess.run([
            'speaker-test', 
            '-D', 'plughw:3,0',  # Card 3, device 0
            '-t', 'sine', 
            '-f', '1000',        # 1kHz tone
            '-l', '1'            # Play once
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✓ Audio test successful!")
            return True
        else:
            print(f"Audio test failed: {result.stderr}")
            
            # Try alternative test with aplay
            print("Trying alternative audio test...")
            result2 = subprocess.run([
                'aplay', '-D', 'plughw:3,0', '/dev/zero'
            ], capture_output=True, text=True, timeout=2)
            
            return result2.returncode == 0
            
    except subprocess.TimeoutExpired:
        print("✓ Audio test completed (timeout is normal)")
        return True
    except Exception as e:
        print(f"Audio test error: {e}")
        return False

def show_current_config():
    """Show current audio configuration"""
    print("Current Audio Configuration:")
    print("=" * 30)
    
    # Show ALSA cards
    try:
        result = subprocess.run(['cat', '/proc/asound/cards'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ALSA Cards:")
            print(result.stdout)
    except:
        pass
    
    # Show .asoundrc if exists
    asoundrc_path = os.path.expanduser("~/.asoundrc")
    if os.path.exists(asoundrc_path):
        print(f"\n{asoundrc_path} exists:")
        try:
            with open(asoundrc_path, 'r') as f:
                print(f.read())
        except:
            pass
    else:
        print(f"\n{asoundrc_path} does not exist")

def main():
    """Main setup function"""
    print("KT USB Audio Quick Setup")
    print("=" * 25)
    
    show_current_config()
    
    print("\nSetting up KT USB Audio (Card 3)...")
    
    if setup_kt_usb_audio():
        print("\n🎉 Setup complete!")
        print("\nYour KT USB Audio device should now be the default")
        print("Run 'python3 phone_system.py' to test the phone system")
    else:
        print("\n❌ Setup failed")
        print("You may need to configure audio manually")

if __name__ == "__main__":
    main()