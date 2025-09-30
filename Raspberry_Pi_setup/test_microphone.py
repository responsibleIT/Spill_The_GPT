#!/usr/bin/env python3
"""
Microphone testing script for Raspberry Pi
Tests all available audio input devices
"""

import pyaudio
import wave
import sys
import time
import threading

def list_audio_devices():
    """List all available audio devices with input capabilities"""
    audio = pyaudio.PyAudio()
    
    print("=== Available Audio Devices ===")
    input_devices = []
    
    for i in range(audio.get_device_count()):
        try:
            info = audio.get_device_info_by_index(i)
            device_name = info['name']
            max_input_channels = info['maxInputChannels']
            max_output_channels = info['maxOutputChannels']
            default_rate = info['defaultSampleRate']
            
            print(f"\nDevice {i}: {device_name}")
            print(f"  Input channels: {max_input_channels}")
            print(f"  Output channels: {max_output_channels}")
            print(f"  Default sample rate: {default_rate}")
            
            if max_input_channels > 0:
                input_devices.append((i, device_name, max_input_channels))
                print(f"  → Can be used for recording")
            
        except Exception as e:
            print(f"Device {i}: Error getting info - {e}")
    
    audio.terminate()
    return input_devices

def test_device_recording(device_index, device_name, duration=3):
    """Test recording from a specific device"""
    print(f"\n=== Testing Device {device_index}: {device_name} ===")
    
    audio = pyaudio.PyAudio()
    
    # Test different channel configurations
    for channels in [1, 2]:
        try:
            print(f"Testing {channels} channel(s)...")
            
            # Open stream
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=44100,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            print(f"  ✓ Successfully opened stream with {channels} channels")
            print(f"  Recording for {duration} seconds...")
            
            # Record some audio
            frames = []
            for i in range(0, int(44100 / 1024 * duration)):
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Show progress
                    if i % 10 == 0:
                        print(".", end="", flush=True)
                        
                except Exception as e:
                    print(f"\n  ✗ Error reading audio: {e}")
                    break
            
            stream.close()
            
            # Save test recording
            if frames:
                filename = f"test_device_{device_index}_{channels}ch.wav"
                wf = wave.open(filename, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                print(f"\n  ✓ Test recording saved as {filename}")
                
                # Check if we actually recorded something
                if len(b''.join(frames)) > 0:
                    print(f"  ✓ Recorded {len(frames)} audio chunks")
                    return True, channels, filename
                else:
                    print(f"  ✗ No audio data recorded")
            
        except Exception as e:
            print(f"  ✗ Failed with {channels} channels: {e}")
    
    audio.terminate()
    return False, 0, None

def record_with_level_monitoring(device_index, duration=5):
    """Record with real-time audio level monitoring"""
    print(f"\n=== Recording from device {device_index} with level monitoring ===")
    print("Speak into the microphone...")
    
    audio = pyaudio.PyAudio()
    
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024
        )
        
        frames = []
        max_level = 0
        
        for i in range(0, int(44100 / 1024 * duration)):
            data = stream.read(1024, exception_on_overflow=False)
            frames.append(data)
            
            # Calculate audio level
            import struct
            try:
                # Convert bytes to integers for level calculation
                audio_data = struct.unpack(f'{len(data)//2}h', data)
                level = max(abs(sample) for sample in audio_data) if audio_data else 0
                max_level = max(max_level, level)
                
                # Show level bar
                bar_length = 20
                filled = int((level / 32768) * bar_length)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"\rLevel: [{bar}] {level:5d}", end="", flush=True)
                
            except Exception:
                print(".", end="", flush=True)
        
        stream.close()
        
        print(f"\n✓ Recording complete. Max level: {max_level}")
        
        # Save recording
        filename = f"mic_test_{device_index}.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"Recording saved as {filename}")
        
        if max_level > 100:
            print("✓ Good audio levels detected!")
            return True, filename
        else:
            print("✗ Very low or no audio detected")
            return False, filename
            
    except Exception as e:
        print(f"\n✗ Recording failed: {e}")
        return False, None
    
    finally:
        audio.terminate()

def main():
    print("Microphone Test Script")
    print("======================")
    
    # List all devices
    input_devices = list_audio_devices()
    
    if not input_devices:
        print("\n✗ No input devices found!")
        return
    
    print(f"\nFound {len(input_devices)} input device(s)")
    
    # Test each input device
    working_devices = []
    
    for device_index, device_name, max_channels in input_devices:
        success, channels, filename = test_device_recording(device_index, device_name)
        if success:
            working_devices.append((device_index, device_name, channels, filename))
    
    # Report results
    print(f"\n=== Test Results ===")
    
    if working_devices:
        print("✓ Working microphone devices:")
        for device_index, device_name, channels, filename in working_devices:
            print(f"  Device {device_index}: {device_name} ({channels} channels) - {filename}")
        
        # Test the first working device with level monitoring
        first_device = working_devices[0][0]
        print(f"\nTesting device {first_device} with level monitoring...")
        success, filename = record_with_level_monitoring(first_device)
        
        if success:
            print(f"\n✓ Microphone is working! Use device {first_device} in your phone system")
            print(f"  Set FORCE_AUDIO_DEVICE = {first_device} in phone_system.py")
        else:
            print("\n✗ No significant audio input detected")
            
    else:
        print("✗ No working microphone devices found")
    
    print("\n=== Terminal Commands for Further Testing ===")
    print("1. Test with arecord (if available):")
    print("   arecord -D plughw:0,0 -d 3 -f cd test.wav")
    print("   arecord -l  # List capture devices")
    print("\n2. Test with pactl (PulseAudio):")
    print("   pactl list sources short")
    print("   pactl info")
    print("\n3. Test with alsamixer:")
    print("   alsamixer  # Check microphone levels")

if __name__ == "__main__":
    main()