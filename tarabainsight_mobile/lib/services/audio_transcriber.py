import os
from openai import OpenAI

def transcribe_and_translate_audio(audio_file_path):
    """Uses OpenAI Whisper to transcribe audio and translate to English."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return "Error: OPENAI_API_KEY not found."

    client = OpenAI(api_key=api_key)
    
    try:
        print(f"🎤 Transcribing audio: {audio_file_path}")
        
        # Open the audio file
        with open(audio_file_path, "rb") as audio_file:
            # Whisper automatically detects the language and translates to English
            transcription = client.audio.translations.create(
                model="whisper-1",
                file=audio_file
            )
        
        translated_text = transcription.text
        print(f"✅ Transcription successful: {translated_text[:50]}...")
        return translated_text
        
    except Exception as e:
        print(f"❌ Audio Transcription Failed: {e}")
        return f"Error: {str(e)}"