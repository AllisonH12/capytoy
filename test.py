from pathlib import Path
import pyaudio
import wave
from gtts import gTTS
import os
import tempfile
from openai import OpenAI
from pydub import AudioSegment
import subprocess


client = OpenAI()

def get_response_from_gpt4(prompt_text):
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful pet toy assistant. "},
        {"role": "user", "content": prompt_text},
    ])
    message = response.choices[0].message.content
    print("GPT-4 Response:", message)
    return message

def record_audio(WAVE_OUTPUT_FILENAME="output.wav", record_seconds=5, chunk=4098, format=pyaudio.paInt16, channels=1, rate=44100, device_index=2):
    p = pyaudio.PyAudio()
    #for i in range(p.get_device_count()):
    #    print(p.get_device_info_by_index(i))
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device_index)  # Specify the device index here

    print("* recording")

    frames = []

    for i in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


def speak(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=text
    )
    # Write the binary content directly to a file
    with open(speech_file_path, 'wb') as file:
        file.write(response.content)


    # Run mpg123 and play the specified MP3 file
    subprocess.run(['mpg123', speech_file_path])


def transcribe(filepath):
    return client.audio.transcriptions.create(
        model="whisper-1", 
        file=open(filepath, "rb"),
        response_format="text"
    )



def main():
    # Record audio from the microphone
    print("Please speak into the microphone.")
    record_audio(WAVE_OUTPUT_FILENAME="user_input.wav", record_seconds=5)

    #prompt = "Yong are a helpful assistant that you can transcribe audible files in any languages, correct spelling mistakes, try to be friendly"    
    # Transcribe the audio to text
    transcription = transcribe("user_input.wav")
    print("I heard:", transcription)    
     
    # Get a response from GPT-4
    response = get_response_from_gpt4(transcription)
    print(response)
    
    # Use text-to-speech to play the response
    speak(response)

if __name__ == "__main__":
    main()

