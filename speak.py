from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment
import subprocess

client = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Today is a wonderful day to build something people love!"
)
# Write the binary content directly to a file
with open(speech_file_path, 'wb') as file:
    file.write(response.content)


# Run mpg123 and play the specified MP3 file
subprocess.run(['mpg123', speech_file_path])


# Load your MP3 file
# Export as WAV
#mp3_audio = AudioSegment.from_file(speech_file_path, format="mp3")
#mp3_audio.export("s.wav", format="wav")

