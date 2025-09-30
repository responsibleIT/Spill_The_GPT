#!/usr/bin/env python3
"""
USB Audio Configuration Script for Raspberry Pi Phone System
This script helps configure the correct USB audio device
"""

import subprocess
import os

def set_alsa_default(card_number):
    """Set ALSA default audio device"""
    try:
        # Create or update .asoundrc file
        asoundrc_content = f"""
pcm.!default {{
    type hw
    card {card_number}
}}
ctl.!default {{
    type hw
    card {card_number}
}}
"""
        
        home_dir = os.path.expanduser("~")
        asoundrc_path = os.path.join(home_dir, ".asoundrc")
        
        with open(asoundrc_path, 'w') as f:
            f.write(asoundrc_content)
        
        print(f"Created/updated {asoundrc_path} to use card {card_number}")
        return True
        
    except Exception as e:
        print(f"Error setting ALSA default: {e}")
        return False

def list_alsa_cards():
    """List available ALSA sound cards"""
    try:
        result = subprocess.run(['cat', '/proc/asound/cards'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Available ALSA sound cards:")
            print(result.stdout)
            return result.stdout
        else:
            print("Could not read /proc/asound/cards")
            return None
    except Exception as e:
        print(f"Error listing ALSA cards: {e}")
        return None

def test_audio_device(card_number):
    """Test audio output on specific card"""
    try:
        print(f"Testing audio output on card {card_number}...")
        # Play a test sound using aplay
        result = subprocess.run([
            'speaker-test', 
            '-D', f'plughw:{card_number},0',
            '-t', 'sine', 
            '-f', '1000', 
            '-l', '1'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print(f"✓ Audio test successful on card {card_number}")
            return True
        else:
            print(f"✗ Audio test failed on card {card_number}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Audio test on card {card_number} completed")
        return True
    except Exception as e:
        print(f"Error testing audio on card {card_number}: {e}")
        return False

def configure_usb_audio():
    """Interactive USB audio configuration"""
    print("USB Audio Configuration for Phone System")
    print("=" * 40)
    
    # List available cards
    cards_output = list_alsa_cards()
    if not cards_output:
        print("Could not detect audio cards")
        return
    
    # Parse card numbers and names - improved detection
    cards = []
    for line in cards_output.split('\n'):
        line = line.strip()
        if not line or 'card' not in line.lower():
            continue
            
        try:
            # Extract card number and details
            if '[' in line and ']' in line:
                card_part = line.split('[')[0].strip()
                card_num = int(card_part)
                
                # Get card name and driver info
                name_part = line.split('[')[1].split(']')[0]
                driver_part = line.split(']:')[1].strip() if ']:' in line else ""
                
                # Check if this looks like a USB audio device
                is_usb = any(keyword in line.upper() for keyword in [
                    'USB-AUDIO', 'USB AUDIO', 'KT USB', 'AUDIO', 
                    'MICROPHONE', 'HEADSET', 'WEBCAM'
                ])
                
                # Exclude built-in Pi audio
                is_builtin = any(keyword in line.upper() for keyword in [
                    'BCM2835', 'VC4-HDMI', 'HEADPHONES'
                ])
                
                if is_usb and not is_builtin:
                    cards.append((card_num, f"{name_part} - {driver_part}"))
                    print(f"Found USB audio device: {card_num} - {name_part}")
                elif not is_builtin:
                    # Include any non-builtin audio device as potential USB
                    cards.append((card_num, f"{name_part} - {driver_part}"))
                    print(f"Found external audio device: {card_num} - {name_part}")
                    
        except (ValueError, IndexError) as e:
            continue
    
    if not cards:
        print("No external audio devices detected")
        print("Available cards:")
        print(cards_output)
        print("\nTrying manual detection...")
        
        # Manual fallback - show all non-builtin cards
        for line in cards_output.split('\n'):
            if 'bcm2835' not in line.lower() and 'vc4-hdmi' not in line.lower() and '[' in line:
                try:
                    card_num = int(line.split('[')[0].strip())
                    name = line.split('[')[1].split(']')[0]
                    cards.append((card_num, name))
                    print(f"Manual detection found: {card_num} - {name}")
                except:
                    continue
    
    if not cards:
        print("No suitable audio cards found")
        return
    
    # Let user select card
    print("\nSelect USB audio card to configure:")
    for i, (card_num, card_name) in enumerate(cards):
        print(f"{i + 1}. Card {card_num}: {card_name}")
    
    try:
        choice = int(input("Enter choice (1-{}): ".format(len(cards)))) - 1
        if 0 <= choice < len(cards):
            selected_card = cards[choice][0]
            print(f"Selected card {selected_card}")
            
            # Test the selected card
            if test_audio_device(selected_card):
                # Set as default
                if set_alsa_default(selected_card):
                    print(f"✓ USB audio card {selected_card} configured as default")
                    
                    # Update phone system configuration
                    update_phone_config(selected_card)
                    
                    print("\nConfiguration complete!")
                    print("Restart the phone system to use the new audio settings")
                else:
                    print("Failed to set as default audio device")
            else:
                print("Audio test failed - device may not work correctly")
        else:
            print("Invalid choice")
            
    except (ValueError, KeyboardInterrupt):
        print("Configuration cancelled")

def update_phone_config(card_number):
    """Update phone system configuration file"""
    try:
        config_content = f"""# USB Audio Configuration
# This file is auto-generated by configure_usb_audio.py

# Set this to force specific audio device (ALSA card number)
FORCE_AUDIO_DEVICE = {card_number}

# You can also set specific device indices if needed
# USB_AUDIO_OUTPUT_DEVICE = {card_number}
# USB_AUDIO_INPUT_DEVICE = {card_number}
"""
        
        with open('audio_config.py', 'w') as f:
            f.write(config_content)
        
        print(f"Created audio_config.py with card {card_number}")
        return True
        
    except Exception as e:
        print(f"Error creating config file: {e}")
        return False

def main():
    """Main configuration function"""
    print("Starting USB audio configuration...")
    
    # Check if running on Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' not in f.read():
                print("Warning: This doesn't appear to be a Raspberry Pi")
    except:
        pass
    
    configure_usb_audio()

if __name__ == "__main__":
    main()