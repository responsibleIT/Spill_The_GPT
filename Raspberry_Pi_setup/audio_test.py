#!/usr/bin/env python3
"""
Audio Device Test Script for Raspberry Pi Phone System
Use this to find and test audio devices
"""

import pygame
import pyaudio
import wave
import tempfile
import os

def list_pygame_audio_devices():
    """List available pygame audio devices"""
    print("Pygame Audio Devices:")
    print("=" * 30)
    
    try:
        pygame.mixer.pre_init()
        pygame.mixer.init()
        
        # Get current audio driver
        driver = pygame.mixer.get_init()
        print(f"Current pygame audio driver: {driver}")
        
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"Error with pygame audio: {e}")

def list_pyaudio_devices():
    """List available pyaudio devices"""
    print("\nPyAudio Devices:")
    print("=" * 30)
    
    try:
        audio = pyaudio.PyAudio()
        
        print("Available audio devices:")
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            print(f"Device {i}: {info['name']}")
            print(f"  Max input channels: {info['maxInputChannels']}")
            print(f"  Max output channels: {info['maxOutputChannels']}")
            print(f"  Default sample rate: {info['defaultSampleRate']}")
            print(f"  Host API: {audio.get_host_api_info_by_index(info['hostApi'])['name']}")
            print()
        
        # Get default devices
        default_input = audio.get_default_input_device_info()
        default_output = audio.get_default_output_device_info()
        
        print(f"Default input device: {default_input['name']} (Index: {default_input['index']})")
        print(f"Default output device: {default_output['name']} (Index: {default_output['index']})")
        
        audio.terminate()
        
    except Exception as e:
        print(f"Error with pyaudio: {e}")

def find_usb_audio_devices():
    """Find USB audio devices specifically"""
    print("\nUSB Audio Devices:")
    print("=" * 30)
    
    try:
        audio = pyaudio.PyAudio()
        usb_devices = []
        
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            device_name = info['name'].lower()
            
            # Look for USB-related keywords
            if any(keyword in device_name for keyword in ['usb', 'card', 'device']):
                usb_devices.append((i, info))
                print(f"USB Device {i}: {info['name']}")
                print(f"  Input channels: {info['maxInputChannels']}")
                print(f"  Output channels: {info['maxOutputChannels']}")
                print()
        
        audio.terminate()
        return usb_devices
        
    except Exception as e:
        print(f"Error finding USB devices: {e}")
        return []

def test_audio_output(device_index=None):
    """Test audio output on specific device"""
    print(f"\nTesting audio output{f' on device {device_index}' if device_index else ''}:")
    print("=" * 30)
    
    try:
        # Create a simple test tone
        import numpy as np
        
        # Generate test tone
        duration = 2  # seconds
        sample_rate = 44100
        frequency = 440  # A note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        tone = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit PCM
        tone_16bit = (tone * 32767).astype(np.int16)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(tone_16bit.tobytes())
        
        # Test with pygame
        try:
            # Initialize pygame mixer with specific device if provided
            if device_index is not None:
                os.environ['SDL_AUDIODRIVER'] = 'alsa'
                os.environ['ALSA_PCM_DEVICE'] = str(device_index)
            
            pygame.mixer.init(frequency=sample_rate, size=-16, channels=1, buffer=1024)
            
            print("Playing test tone with pygame...")
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            pygame.mixer.quit()
            print("✓ Pygame audio test successful")
            
        except Exception as e:
            print(f"✗ Pygame audio test failed: {e}")
        
        # Clean up
        os.unlink(temp_path)
        
    except Exception as e:
        print(f"Error in audio test: {e}")

def check_alsa_devices():
    """Check ALSA audio devices"""
    print("\nALSA Audio Devices:")
    print("=" * 30)
    
    try:
        import subprocess
        
        # List ALSA devices
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ALSA playback devices:")
            print(result.stdout)
        else:
            print("Could not list ALSA devices")
            
        # List ALSA capture devices
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ALSA capture devices:")
            print(result.stdout)
            
    except Exception as e:
        print(f"Error checking ALSA devices: {e}")

def main():
    """Run audio device tests"""
    print("Audio Device Test for Raspberry Pi Phone System")
    print("=" * 50)
    
    # Check ALSA first
    check_alsa_devices()
    
    # List all devices
    list_pygame_audio_devices()
    list_pyaudio_devices()
    
    # Find USB devices
    usb_devices = find_usb_audio_devices()
    
    # Test default audio
    print("\nTesting default audio output...")
    test_audio_output()
    
    # Test USB devices if found
    if usb_devices:
        for device_index, device_info in usb_devices:
            if device_info['maxOutputChannels'] > 0:
                print(f"\nTesting USB audio device {device_index}: {device_info['name']}")
                test_audio_output(device_index)
    
    print("\nAudio test complete!")
    print("\nNext steps:")
    print("1. Note which device number corresponds to your USB audio")
    print("2. Update phone_system.py to use that device")
    print("3. You may also need to set ALSA default device")

if __name__ == "__main__":
    main()