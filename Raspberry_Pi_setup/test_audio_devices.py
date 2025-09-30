#!/usr/bin/env python3
"""
Test script to check audio device capabilities before running the phone system
"""

import pyaudio
import sys

def test_audio_devices():
    """Test all available audio devices and their capabilities"""
    
    try:
        audio = pyaudio.PyAudio()
        print("=== Audio Device Capabilities Test ===\n")
        
        print(f"Total audio devices: {audio.get_device_count()}\n")
        
        for i in range(audio.get_device_count()):
            try:
                info = audio.get_device_info_by_index(i)
                device_name = info['name']
                
                print(f"Device {i}: {device_name}")
                print(f"  Max input channels: {info['maxInputChannels']}")
                print(f"  Max output channels: {info['maxOutputChannels']}")
                print(f"  Default sample rate: {info['defaultSampleRate']}")
                print(f"  Host API: {info['hostApi']}")
                
                # Test if device supports mono recording
                if info['maxInputChannels'] > 0:
                    mono_supported = test_device_format(audio, i, channels=1, input_device=True)
                    stereo_supported = test_device_format(audio, i, channels=2, input_device=True)
                    print(f"  Mono recording: {'✓' if mono_supported else '✗'}")
                    print(f"  Stereo recording: {'✓' if stereo_supported else '✗'}")
                
                # Test if device supports audio output
                if info['maxOutputChannels'] > 0:
                    mono_output = test_device_format(audio, i, channels=1, input_device=False)
                    stereo_output = test_device_format(audio, i, channels=2, input_device=False)
                    print(f"  Mono output: {'✓' if mono_output else '✗'}")
                    print(f"  Stereo output: {'✓' if stereo_output else '✗'}")
                
                # Check if this looks like a USB device
                if any(keyword in device_name.lower() for keyword in ['usb', 'card', 'device']):
                    print("  → Detected as USB audio device")
                
                print()
                
            except Exception as e:
                print(f"Device {i}: Error getting info - {e}\n")
        
        audio.terminate()
        
    except Exception as e:
        print(f"Error initializing PyAudio: {e}")
        return False
    
    return True

def test_device_format(audio, device_index, channels=1, input_device=True, 
                      sample_rate=44100, format=pyaudio.paInt16):
    """Test if a device supports a specific audio format"""
    try:
        if input_device:
            stream = audio.open(
                format=format,
                channels=channels,
                rate=sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
        else:
            stream = audio.open(
                format=format,
                channels=channels,
                rate=sample_rate,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024
            )
        
        stream.close()
        return True
        
    except Exception:
        return False

def recommend_settings():
    """Provide recommendations based on detected devices"""
    audio = pyaudio.PyAudio()
    
    print("\n=== Recommendations ===")
    
    # Look for USB devices that support mono recording
    usb_devices = []
    for i in range(audio.get_device_count()):
        try:
            info = audio.get_device_info_by_index(i)
            device_name = info['name'].lower()
            
            if any(keyword in device_name for keyword in ['usb', 'card']):
                if info['maxInputChannels'] > 0:
                    mono_works = test_device_format(audio, i, channels=1, input_device=True)
                    if mono_works:
                        usb_devices.append((i, info['name']))
        except:
            continue
    
    if usb_devices:
        print("✓ Compatible USB audio devices found:")
        for device_id, device_name in usb_devices:
            print(f"  Device {device_id}: {device_name}")
        print(f"\nRecommendation: Use FORCE_AUDIO_DEVICE = {usb_devices[0][0]} in phone_system.py")
    else:
        print("✗ No compatible USB audio devices found")
        print("Recommendation: The system will use the default audio device")
    
    audio.terminate()

if __name__ == "__main__":
    print("Testing audio device capabilities...\n")
    
    if test_audio_devices():
        recommend_settings()
    else:
        print("Failed to test audio devices")
        sys.exit(1)