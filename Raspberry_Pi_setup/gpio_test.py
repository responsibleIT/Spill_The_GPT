#!/usr/bin/env python3
"""
GPIO Test Script for Raspberry Pi Phone System
Use this to test GPIO functionality before running the main system
"""

import time
import sys

def test_gpiozero():
    """Test gpiozero library"""
    try:
        from gpiozero import Button, Device
        print("✓ gpiozero library imported successfully")
        
        # Try different pin factories
        try:
            # Test with default pin factory
            button = Button(4, pull_up=True, bounce_time=0.1)
            print("✓ Button created with default pin factory")
            button.close()
            return True
        except Exception as e:
            print(f"✗ Default pin factory failed: {e}")
            
            # Try mock factory
            try:
                from gpiozero.pins.mock import MockFactory
                Device.pin_factory = MockFactory()
                button = Button(4, pull_up=True)
                print("✓ Button created with mock pin factory")
                button.close()
                return True
            except Exception as e2:
                print(f"✗ Mock pin factory failed: {e2}")
                return False
                
    except ImportError as e:
        print(f"✗ gpiozero library not available: {e}")
        return False

def test_rpi_gpio():
    """Test RPi.GPIO library"""
    try:
        import RPi.GPIO as GPIO
        print("✓ RPi.GPIO library imported successfully")
        
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            state = GPIO.input(4)
            print(f"✓ GPIO pin 4 state: {state}")
            GPIO.cleanup()
            return True
        except Exception as e:
            print(f"✗ RPi.GPIO setup failed: {e}")
            try:
                GPIO.cleanup()
            except:
                pass
            return False
            
    except ImportError as e:
        print(f"✗ RPi.GPIO library not available: {e}")
        return False

def test_lgpio():
    """Test lgpio library"""
    try:
        import lgpio
        print("✓ lgpio library imported successfully")
        return True
    except ImportError as e:
        print(f"✗ lgpio library not available: {e}")
        return False

def main():
    """Run GPIO tests"""
    print("GPIO Test for Raspberry Pi Phone System")
    print("=" * 40)
    
    # Test libraries
    lgpio_ok = test_lgpio()
    gpiozero_ok = test_gpiozero()
    rpi_gpio_ok = test_rpi_gpio()
    
    print("\nTest Summary:")
    print("=" * 40)
    print(f"lgpio:     {'✓ OK' if lgpio_ok else '✗ FAIL'}")
    print(f"gpiozero:  {'✓ OK' if gpiozero_ok else '✗ FAIL'}")
    print(f"RPi.GPIO:  {'✓ OK' if rpi_gpio_ok else '✗ FAIL'}")
    
    if not any([lgpio_ok, gpiozero_ok, rpi_gpio_ok]):
        print("\n⚠️  No GPIO libraries working!")
        print("Recommendations:")
        print("1. Install missing packages: sudo apt install python3-lgpio")
        print("2. Or: pip install rpi-lgpio")
        print("3. Or: pip install RPi.GPIO")
        print("4. Check if running on actual Raspberry Pi hardware")
        print("5. The system will fall back to keyboard input mode")
    elif gpiozero_ok:
        print("\n✓ gpiozero is working - system should run normally")
    elif rpi_gpio_ok:
        print("\n✓ RPi.GPIO is working - system will use this library")
    
    print(f"\nCurrent platform: {sys.platform}")
    
    # Try to detect if we're on actual Pi hardware
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                print("✓ Running on Raspberry Pi hardware")
            else:
                print("⚠️  May not be running on Raspberry Pi hardware")
    except:
        print("? Could not detect hardware type")

if __name__ == "__main__":
    main()