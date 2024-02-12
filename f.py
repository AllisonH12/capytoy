from pathlib import Path
import pyaudio
import wave
import subprocess
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

def record_audio(filename="output.wav", record_seconds=5, chunk=4096, format=pyaudio.paInt16, channels=1, rate=44100, device_index=2):
    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk, input_device_index=device_index)
    
    print("* Recording")
    frames = [stream.read(chunk) for _ in range(0, int(rate / chunk * record_seconds))]
    print("* Done Recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def speak(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)

    with open(speech_file_path, 'wb') as file:
        file.write(response.content)

    subprocess.run(['mpg123', str(speech_file_path)])

def transcribe(filepath):
    return client.audio.transcriptions.create(model="whisper-1", file=open(filepath, "rb"), response_format="text")

def get_response_from_gpt4(prompt_text):
    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt_text}])
    return response.choices[0].message.content

def main():
    print("Please speak into the microphone.")
    record_audio("user_input.wav", 5)

    transcription = transcribe("user_input.wav")
    print("Transcribed Text:", transcription)

    response = get_response_from_gpt4(transcription)
    print("GPT-4 Response:", response)
    
    speak(response)

if __name__ == "__main__":
    main()

