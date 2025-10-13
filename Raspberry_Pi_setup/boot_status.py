#!/usr/bin/env python3
"""
Boot Status Indicator for Phone Gossip System
Shows LED patterns or prints status during boot process
"""

import time
import sys
import os

# Try to import GPIO for status LED (optional)
try:
    from gpiozero import LED
    status_led = LED(18)  # GPIO 18 for status LED
    HAS_LED = True
except:
    HAS_LED = False
    status_led = None

def blink_pattern(pattern, message=""):
    """Blink LED in a pattern and print message"""
    if message:
        print(f"[BOOT] {message}")
    
    if HAS_LED and status_led:
        for on_time, off_time in pattern:
            status_led.on()
            time.sleep(on_time)
            status_led.off()
            time.sleep(off_time)
    else:
        # Just sleep for the total pattern time
        total_time = sum(on_time + off_time for on_time, off_time in pattern)
        time.sleep(total_time)

def boot_status_check():
    """Check system status during boot"""
    
    print("=== Phone Gossip System Boot Check ===")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Working directory: {script_dir}")
    
    # 2. Check virtual environment
    venv_path = os.path.join(script_dir, "phone_env")
    if os.path.exists(venv_path):
        blink_pattern([(0.1, 0.1)], "✅ Virtual environment found")
    else:
        blink_pattern([(0.5, 0.1), (0.5, 0.1)], "❌ Virtual environment missing")
        return False
    
    # 3. Check main script
    if os.path.exists("phone_system.py"):
        blink_pattern([(0.1, 0.1)], "✅ Main script found")
    else:
        blink_pattern([(0.5, 0.1), (0.5, 0.1)], "❌ phone_system.py missing")
        return False
    
    # 4. Check .env file
    if os.path.exists(".env"):
        blink_pattern([(0.1, 0.1)], "✅ API keys file found")
    else:
        blink_pattern([(0.5, 0.1), (0.5, 0.1)], "❌ .env file missing")
        return False
    
    # 5. Check audio files
    audio_files_ok = True
    for audio_file in ["welcome.mp3", "transition.mp3"]:
        if os.path.exists(audio_file):
            print(f"✅ {audio_file} found")
        else:
            print(f"⚠️  {audio_file} missing")
            audio_files_ok = False
    
    if audio_files_ok:
        blink_pattern([(0.1, 0.1)], "✅ Audio files ready")
    else:
        blink_pattern([(0.3, 0.1), (0.3, 0.1)], "⚠️  Some audio files missing")
    
    # 6. Wait for network (for API calls)
    print("🌐 Waiting for network connectivity...")
    max_wait = 30
    for i in range(max_wait):
        if os.system("ping -c 1 8.8.8.8 > /dev/null 2>&1") == 0:
            blink_pattern([(0.1, 0.1)], "✅ Network connectivity confirmed")
            break
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Waiting for network... ({i}/{max_wait}s)")
    else:
        blink_pattern([(0.5, 0.1), (0.5, 0.1)], "⚠️  Network timeout - continuing anyway")
    
    # 7. All systems go!
    blink_pattern([(0.1, 0.1), (0.1, 0.1), (0.1, 0.1)], "🚀 System ready to start!")
    
    # Keep LED on to indicate ready state
    if HAS_LED and status_led:
        status_led.on()
    
    return True

if __name__ == "__main__":
    try:
        success = boot_status_check()
        if success:
            print("=== Boot check completed successfully ===")
            sys.exit(0)
        else:
            print("=== Boot check failed ===")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nBoot check interrupted")
        if HAS_LED and status_led:
            status_led.off()
        sys.exit(1)
    except Exception as e:
        print(f"Boot check error: {e}")
        if HAS_LED and status_led:
            # Rapid blink for error
            for _ in range(10):
                status_led.on()
                time.sleep(0.1)
                status_led.off()
                time.sleep(0.1)
        sys.exit(1)