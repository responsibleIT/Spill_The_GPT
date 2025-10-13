#!/usr/bin/env python3
"""
Audio Level Monitor and Controller for Raspberry Pi Phone System
This script monitors and maintains consistent ALSA audio levels
"""

import subprocess
import time
import threading
import re

class AudioLevelController:
    def __init__(self, target_volume=85, check_interval=30):
        """
        Initialize audio level controller
        
        Args:
            target_volume (int): Target volume percentage (0-100)
            check_interval (int): How often to check levels in seconds
        """
        self.target_volume = target_volume
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None
        self.audio_card = None
        self.audio_device = None
        
        # Detect audio setup
        self.detect_audio_setup()
    
    def detect_audio_setup(self):
        """Detect the primary audio card and device"""
        try:
            # Get list of audio cards
            result = subprocess.run(['aplay', '-l'], 
                                  capture_output=True, text=True, check=True)
            
            print("Available audio devices:")
            print(result.stdout)
            
            # Look for USB audio first, then fall back to default
            lines = result.stdout.split('\n')
            usb_card = None
            default_card = None
            
            for line in lines:
                if 'card' in line.lower():
                    # Extract card number
                    match = re.search(r'card (\d+):', line)
                    if match:
                        card_num = match.group(1)
                        if 'usb' in line.lower() or 'kt' in line.lower():
                            usb_card = card_num
                        if default_card is None:
                            default_card = card_num
            
            # Prefer USB, fall back to default
            self.audio_card = usb_card if usb_card else default_card
            self.audio_device = "0"  # Usually device 0
            
            if self.audio_card:
                print(f"Using audio card {self.audio_card}, device {self.audio_device}")
            else:
                print("No audio card detected, using default")
                
        except Exception as e:
            print(f"Error detecting audio setup: {e}")
            self.audio_card = None
    
    def get_current_volume(self, control_name="PCM"):
        """Get current volume level for a specific control"""
        try:
            if self.audio_card:
                cmd = ['amixer', '-c', self.audio_card, 'get', control_name]
            else:
                cmd = ['amixer', 'get', control_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse volume from output like "[85%]" or "85%"
            volume_match = re.search(r'\[(\d+)%\]', result.stdout)
            if volume_match:
                return int(volume_match.group(1))
                
        except Exception as e:
            print(f"Error getting volume for {control_name}: {e}")
        
        return None
    
    def set_volume(self, volume, control_name="PCM"):
        """Set volume level for a specific control"""
        try:
            if self.audio_card:
                cmd = ['amixer', '-c', self.audio_card, 'set', control_name, f'{volume}%']
            else:
                cmd = ['amixer', 'set', control_name, f'{volume}%']
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"Set {control_name} volume to {volume}%")
            return True
            
        except Exception as e:
            print(f"Error setting volume for {control_name}: {e}")
            return False
    
    def get_all_controls(self):
        """Get list of all available mixer controls"""
        try:
            if self.audio_card:
                cmd = ['amixer', '-c', self.audio_card, 'controls']
            else:
                cmd = ['amixer', 'controls']
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            controls = []
            for line in result.stdout.split('\n'):
                if 'name=' in line:
                    # Extract control name like "name='PCM'"
                    match = re.search(r"name='([^']+)'", line)
                    if match:
                        controls.append(match.group(1))
            
            return controls
            
        except Exception as e:
            print(f"Error getting mixer controls: {e}")
            return []
    
    def fix_audio_levels(self):
        """Fix and maintain audio levels for all relevant controls"""
        controls = self.get_all_controls()
        print(f"Available mixer controls: {controls}")
        
        # Common control names to check and fix
        important_controls = ['PCM', 'Master', 'Speaker', 'Headphone', 'Digital', 'Capture']
        
        for control in important_controls:
            if control in controls:
                current = self.get_current_volume(control)
                if current is not None:
                    print(f"{control}: {current}%")
                    if abs(current - self.target_volume) > 5:  # If more than 5% off
                        print(f"Adjusting {control} from {current}% to {self.target_volume}%")
                        self.set_volume(self.target_volume, control)
                    else:
                        print(f"{control} volume OK at {current}%")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print(f"Starting audio level monitoring (target: {self.target_volume}%, interval: {self.check_interval}s)")
        
        while self.running:
            try:
                print(f"\n--- Audio Level Check at {time.strftime('%H:%M:%S')} ---")
                self.fix_audio_levels()
                
                # Wait for next check
                for _ in range(self.check_interval * 10):  # Check every 0.1s for stop signal
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def start_monitoring(self):
        """Start the audio level monitoring in background"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("Audio level monitoring started")
        else:
            print("Audio monitoring already running")
    
    def stop_monitoring(self):
        """Stop the audio level monitoring"""
        if self.running:
            self.running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            print("Audio level monitoring stopped")
        else:
            print("Audio monitoring not running")
    
    def set_initial_levels(self):
        """Set initial audio levels and show current status"""
        print("=== Setting Initial Audio Levels ===")
        self.fix_audio_levels()
        print("=== Initial Setup Complete ===\n")

if __name__ == "__main__":
    import sys
    
    # Default settings
    target_vol = 85
    check_interval = 30
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        target_vol = int(sys.argv[1])
    if len(sys.argv) > 2:
        check_interval = int(sys.argv[2])
    
    # Create controller
    controller = AudioLevelController(target_volume=target_vol, check_interval=check_interval)
    
    print(f"Audio Level Controller")
    print(f"Target Volume: {target_vol}%")
    print(f"Check Interval: {check_interval} seconds")
    print()
    
    # Set initial levels
    controller.set_initial_levels()
    
    # Start monitoring
    controller.start_monitoring()
    
    try:
        print("Press Ctrl+C to stop monitoring...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        controller.stop_monitoring()