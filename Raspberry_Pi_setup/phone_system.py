#!/usr/bin/env python3
"""
Enhanced Phone-based Gossip System for Raspberry Pi
Now includes previous gossip playback before recording
"""

import os
import time
import threading
import pyaudio
import wave
import pygame
from gpiozero import Button
from signal import pause
import whisper
from openai import OpenAI
from el import text_to_speech_file
from gossip_database import GossipDatabase

# Configuration
HORN_BUTTON_PIN = 4  # GPIO pin for horn detection (adjust as needed)
AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 44100
AUDIO_CHUNK = 1024
RECORDING_FILE = "phone_recording.wav"
WELCOME_AUDIO = "welcome.mp3"
TRANSITION_AUDIO = "transition.mp3"

# Initialize components
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
whisper_model = None  # Will be loaded when needed
pygame.mixer.init()

class EnhancedPhoneSystem:
    def __init__(self):
        self.horn_button = Button(HORN_BUTTON_PIN, pull_up=True)
        self.is_recording = False
        self.audio = pyaudio.PyAudio()
        self.recording_stream = None
        self.audio_frames = []
        self.db = GossipDatabase()
        
        # Set up event handlers
        self.horn_button.when_pressed = self.on_horn_pickup
        self.horn_button.when_released = self.on_horn_putdown
        
        print("Enhanced phone system initialized. Waiting for phone pickup...")
        print(f"Current gossip count in database: {self.db.get_gossip_count()}")
    
    def on_horn_pickup(self):
        """Called when the phone horn is picked up"""
        print("Phone picked up! Starting enhanced interaction...")
        
        # New flow: welcome → previous gossip → transition → record
        self.play_welcome_message()
        time.sleep(0.5)  # Brief pause
        
        self.play_previous_gossip()
        time.sleep(0.5)  # Brief pause
        
        self.play_transition_message()
        time.sleep(1)  # Pause before recording
        
        self.start_recording()
    
    def on_horn_putdown(self):
        """Called when the phone horn is put down"""
        print("Phone hung up! Processing recording...")
        
        if self.is_recording:
            self.stop_recording()
            # Process the recording in a separate thread to avoid blocking
            threading.Thread(target=self.process_new_gossip, daemon=True).start()
    
    def play_welcome_message(self):
        """Play the welcome audio message"""
        try:
            if os.path.exists(WELCOME_AUDIO):
                print("Playing welcome message...")
                pygame.mixer.music.load(WELCOME_AUDIO)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                print("Welcome audio file not found!")
        except Exception as e:
            print(f"Error playing welcome message: {e}")
    
    def play_previous_gossip(self):
        """Play a random previous gossip from the database"""
        try:
            print("Selecting previous gossip...")
            previous_gossip = self.db.get_random_gossip()
            
            if previous_gossip and os.path.exists(previous_gossip['file_path']):
                print(f"Playing previous gossip: {previous_gossip['gossip_text'][:50]}...")
                pygame.mixer.music.load(previous_gossip['file_path'])
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                print("No previous gossip available or file not found")
                # Optional: play a message saying this is the first gossip
                self.play_first_user_message()
                
        except Exception as e:
            print(f"Error playing previous gossip: {e}")
    
    def play_first_user_message(self):
        """Play a message for the first user when no previous gossip exists"""
        # This could be implemented to generate a one-time audio message
        print("This appears to be the first user - no previous gossip to play")
        time.sleep(2)  # Just a pause instead of audio for now
    
    def play_transition_message(self):
        """Play the transition message before recording"""
        try:
            if os.path.exists(TRANSITION_AUDIO):
                print("Playing transition message...")
                pygame.mixer.music.load(TRANSITION_AUDIO)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                print("Transition audio file not found!")
        except Exception as e:
            print(f"Error playing transition message: {e}")
    
    def start_recording(self):
        """Start recording audio from microphone"""
        try:
            self.is_recording = True
            self.audio_frames = []
            
            self.recording_stream = self.audio.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK
            )
            
            print("Recording started... Speak your gossip!")
            
            # Record in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
    
    def _record_audio(self):
        """Internal method to continuously record audio"""
        while self.is_recording:
            try:
                data = self.recording_stream.read(AUDIO_CHUNK, exception_on_overflow=False)
                self.audio_frames.append(data)
            except Exception as e:
                print(f"Recording error: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and save audio file"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        try:
            if self.recording_stream:
                self.recording_stream.stop_stream()
                self.recording_stream.close()
            
            # Save recorded audio to file
            with wave.open(RECORDING_FILE, 'wb') as wf:
                wf.setnchannels(AUDIO_CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(AUDIO_FORMAT))
                wf.setframerate(AUDIO_RATE)
                wf.writeframes(b''.join(self.audio_frames))
            
            print(f"Recording saved to {RECORDING_FILE}")
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
    
    def process_new_gossip(self):
        """Process the recorded audio through the AI pipeline and save to database"""
        try:
            print("Processing new gossip...")
            
            # Step 1: Transcribe audio
            print("Transcribing audio...")
            transcription = self.transcribe_audio(RECORDING_FILE)
            print(f"Transcription: {transcription}")
            
            if not transcription.strip():
                print("No speech detected in recording")
                return
            
            # Step 2: Process with GPT
            print("Processing with GPT...")
            gossip_text = self.clean_text(transcription)
            print(f"Processed gossip: {gossip_text}")
            
            # Step 3: Convert to speech
            print("Converting to speech...")
            audio_path = text_to_speech_file(gossip_text)
            
            # Step 4: Save to database
            print("Saving to database...")
            gossip_id = self.db.add_gossip(
                file_path=audio_path,
                original_text=transcription,
                gossip_text=gossip_text
            )
            
            if gossip_id > 0:
                print(f"Gossip saved to database with ID: {gossip_id}")
                print(f"Total gossip count: {self.db.get_gossip_count()}")
            
            # Step 5: Play the result (optional - you might want to skip this)
            print("Playing processed gossip...")
            self.play_audio_file(audio_path)
            
            print("New gossip processing complete!")
            
        except Exception as e:
            print(f"Error processing new gossip: {e}")
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio using Whisper"""
        global whisper_model
        if whisper_model is None:
            print("Loading Whisper model...")
            whisper_model = whisper.load_model("tiny")
        
        result = whisper_model.transcribe(audio_file_path)
        return result["text"]
    
    def clean_text(self, text):
        """Process text with GPT to create anonymized gossip"""
        prompt = f"Change the given text into an anonymized sentence of gossip:\n{text}"
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are changing gossip or stories that people give into an anonymized sentence in the form of gossip. The output should be the same language as the input."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def play_audio_file(self, audio_path):
        """Play an audio file through the speakers"""
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_recording:
            self.stop_recording()
        self.audio.terminate()
        pygame.mixer.quit()
        # Clean up any missing files in database
        self.db.cleanup_missing_files()

def main():
    """Main function to run the enhanced phone system"""
    try:
        phone = EnhancedPhoneSystem()
        print("Enhanced phone system ready. Pick up the phone to start!")
        print("Flow: Welcome → Previous Gossip → Transition → Record → Process → Save")
        
        # Keep the program running
        pause()
        
    except KeyboardInterrupt:
        print("\nShutting down enhanced phone system...")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        if 'phone' in locals():
            phone.cleanup()

if __name__ == "__main__":
    main()