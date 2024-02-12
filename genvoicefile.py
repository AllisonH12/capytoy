from pathlib import Path
import subprocess
from openai import OpenAI

def create_speech(client, text, model="tts-1", voice="nova", file_format="mp3"):
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )
    return response.content

def save_file(content, file_path):
    with open(file_path, 'wb') as file:
        file.write(content)

def play_audio(file_path):
    subprocess.run(['mpg123', file_path])

# Main execution
if __name__ == "__main__":
    client = OpenAI()

    inp = input("give me file name:")
    # Define file path
    speech_file_path = Path(__file__).parent / inp

    text = input("give me the content you want to record:")
    # Create speech and save to file
    speech_content = create_speech(client, text)
    save_file(speech_content, speech_file_path)

    # Play the audio file
    play_audio(speech_file_path)

