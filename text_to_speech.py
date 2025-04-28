import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def read_script(filename="script_1.txt"):
    """Read the generated script file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return None

def generate_speech(script_content, voice="alloy", output_file="output_audio.mp3"):
    """Generate speech from the script using OpenAI's TTS API."""
    try:
        # Available voices: alloy, echo, fable, onyx, nova, shimmer
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=script_content,
            instructions="Speak in a fast pase voice as you are reading a news. You are a news reporter.",
        ) as response:
            response.stream_to_file(output_file)

        # response = openai.audio.speech.create(
        #     model="gpt-4o-mini-tts",
        #     voice=voice,
        #     input=,
        #     instructions="Speak like you are reading a news. You are a news reporter."
        # )
        
        # Save the audio file
        # response.stream_to_file(output_file)
        print(f"Successfully generated speech audio: {output_file}")
        return output_file
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def main():
    print("Starting text-to-speech conversion...")
    
    # Read the script
    script_content = read_script()
    if not script_content:
        print("Failed to read script. Exiting.")
        return
    
    # Generate speech audio
    output_file = generate_speech(script_content)
    if not output_file:
        print("Failed to generate speech audio. Exiting.")
        return
    
    print(f"Text-to-speech conversion complete! Audio saved to {output_file}")

if __name__ == "__main__":
    main()