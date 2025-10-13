#!/usr/bin/env python3
"""
Generate audio messages for the enhanced phone system
Creates both welcome and transition messages
"""

import os
from el import text_to_speech_file

def create_welcome_message():
    """Create the welcome audio message"""
    
    # Welcome message text (adjust language as needed)
    welcome_text = """
    Welkom, heb jij iets gehoord? Over je buurvrouw? Mischien over iemand op werk of op school? Ik heb heel veel gehoord.
    Ik deel graag wat ik weet, maar ik wil ook graag jouw verhaal horen.
    Als ik jou iets vertel, vertel jij mij dan iets terug? Dat is wel zo eerlijk.
    Als je iets wil delen, blijf dan aan de lijn.
    Ik ga wel eerst.
    """
    
    # Alternative English version:
    # welcome_text = """
    # Welcome to the gossip system.
    # First you will hear gossip from a previous user.
    # """
    
    print("Generating welcome message...")
    
    try:
        # Generate the audio file
        audio_path = text_to_speech_file(welcome_text)
        
        # Rename to welcome.mp3
        welcome_path = "welcome.mp3"
        if os.path.exists(audio_path):
            os.rename(audio_path, welcome_path)
            print(f"Welcome message created: {welcome_path}")
            return welcome_path
        else:
            print("Failed to create welcome message")
            return None
            
    except Exception as e:
        print(f"Error creating welcome message: {e}")
        return None

def create_transition_message():
    """Create the transition message between gossip playback and recording"""
    
    # Transition message text
    transition_text = """
    Nu is het uw beurt, vertel mij uw roddels.
    Als je klaar bent leg dan de telefoon terug op de haak.
    """
    
    # Alternative English version:
    # transition_text = """
    # Now it's your turn.
    # Tell your gossip and hang up when you're done.
    # Your gossip will be anonymized.
    # """
    
    print("Generating transition message...")
    
    try:
        # Generate the audio file
        audio_path = text_to_speech_file(transition_text)
        
        # Rename to transition.mp3
        transition_path = "transition.mp3"
        if os.path.exists(audio_path):
            os.rename(audio_path, transition_path)
            print(f"Transition message created: {transition_path}")
            return transition_path
        else:
            print("Failed to create transition message")
            return None
            
    except Exception as e:
        print(f"Error creating transition message: {e}")
        return None

def create_all_messages():
    """Create all audio messages for the phone system"""
    print("Creating all audio messages for enhanced phone system...")
    
    welcome_path = create_welcome_message()
    transition_path = create_transition_message()
    
    if welcome_path and transition_path:
        print("All audio messages created successfully!")
        print(f"Created files: {welcome_path}, {transition_path}")
        return True
    else:
        print("Failed to create some audio messages")
        return False

if __name__ == "__main__":
    create_all_messages()