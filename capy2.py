# Import necessary libraries
import sys
from pathlib import Path
import pyaudio
import wave
import subprocess
import threading
from openai import OpenAI
import simpleaudio as sa
from time import sleep
import RPi.GPIO as GPIO
import time
import os
from datetime import datetime

# Create a logs directory if it doesn't already exist
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Declare global variables for use across the script
should_stop_waiting_sound = False  # Controls playback of waiting sound
client = None  # Placeholder for OpenAI client object
servo_pin = 17  # GPIO pin connected to the servo (can be adjusted)
conversation_history = []  # Stores history of conversations
silent_count = 0  # Counter for tracking silence or inactivity

def read_summary_file(summary_file_path="conversation_sum.txt"):
    """Attempt to read a summary file and return its content."""
    try:
        with open(summary_file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""  # Return an empty string if the file does not exist

def setup_servo():
    """Initialize GPIO and servo settings."""
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
    GPIO.setup(servo_pin, GPIO.OUT)

    # Set PWM parameters: 50Hz frequency
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(0)  # Start PWM with 0% duty cycle
    return pwm

def move_mouth(pwm, delay=1):
    """Simulate mouth movement by adjusting servo position."""
    time.sleep(delay)  # Wait before starting the movement

    while not should_stop_waiting_sound:
        # Sequentially adjust servo position to simulate talking
        pwm.ChangeDutyCycle(5)  # Open position
        time.sleep(0.5)
        pwm.ChangeDutyCycle(7.5)  # Neutral position
        time.sleep(0.5)
        pwm.ChangeDutyCycle(10)  # Closed position
        time.sleep(0.5)

def setup():
    """Initialize the script environment, including global variables."""
    global client, should_stop_waiting_sound, silent_count
    should_stop_waiting_sound = False
    client = OpenAI()  # Initialize the OpenAI client
    # Load any existing summary content into conversation history
    summary_content = read_summary_file()
    if summary_content:
        conversation_history.insert(0, ("Summary", summary_content))

def play_waiting_sound(wav_path='wait.wav'):
    """Play a waiting sound repeatedly until stopped."""
    global should_stop_waiting_sound
    wave_obj = sa.WaveObject.from_wave_file(wav_path)
    play_obj = wave_obj.play()
    print("Playing Waiting sound:", Path(wav_path).absolute())

    while should_stop_waiting_sound:
        if not play_obj.is_playing():
            play_obj = wave_obj.play()
    play_obj.stop()

def record_audio(filename="output.wav", record_seconds=8, chunk=4096, format=pyaudio.paInt16, channels=1, rate=44100, device_index=2):
    """Record audio from the microphone and save it to a file."""
    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk, input_device_index=device_index)

    print("* Recording")
    frames = [stream.read(chunk) for _ in range(0, int(rate / chunk * record_seconds))]
    print("* Done Recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def play_audio_and_move_mouth(audio_file_path, pwm):
    """Play an audio file and simulate mouth movement simultaneously."""
    global should_stop_waiting_sound
    should_stop_waiting_sound = False

    mouth_thread = threading.Thread(target=move_mouth, args=(pwm,))
    mouth_thread.start()

    # Use subprocess to play the audio file with mpg123
    subprocess.run(['/usr/bin/mpg123', audio_file_path])

    # Stop mouth movement once audio playback is complete
    should_stop_waiting_sound = True
    mouth_thread.join()

def speak(text, pwm):
    """Convert text to speech, play it, and simulate mouth movement."""
    global should_stop_waiting_sound
    should_stop_waiting_sound = False

    # Generate speech from text using OpenAI's API and save it as an MP3
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    with open(speech_file_path, 'wb') as file:
        file.write(response.content)

    # Move the mouth in sync with the generated speech
    mouth_thread = threading.Thread(target=move_mouth, args=(pwm, 1))
    mouth_thread.start()

    # Play the generated speech
    subprocess.run(['/usr/bin/mpg123', str(speech_file_path)])

    # Stop mouth movement once speech is done
    should_stop_waiting_sound = True
    mouth_thread.join()

def transcribe(filepath):
    """Transcribe audio from a file using OpenAI's transcription service."""
    return client.audio.transcriptions.create(model="whisper-1", file=open(filepath, "rb"), response_format="text")

def log_conversation(user_input, response):
    """Log conversation history in memory."""
    global conversation_history
    conversation_history.append((user_input, response))
    # Limit conversation history to the last 5 entries
    conversation_history = conversation_history[-5:]

def get_response_from_gpt4(user_input):
    """Generate a response from GPT-4 based on accumulated conversation history."""
    global conversation_history
    system_message = "You are a helpful assistant, your name is Capy. You are 12 years old. You are mostly interacting with kids who might speak English, Chinese, and Spanish. You can be playful. Please keep your answer simple and easy to understand. Keep it short. Be super friendly and nice."

    messages = [{"role": "system", "content": system_message}]
    messages += [{"role": "user", "content": inp, "role": "assistant", "content": resp} for inp, resp in conversation_history]
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(model="gpt-4", messages=messages)
    return response.choices[0].message.content

def save_history_to_file():
    """Save the conversation history to a file with a datetime timestamp."""
    global conversation_history
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"{logs_dir}/conversation_history_{now}.txt"

    with open(log_file, "w") as file:
        for user_input, response in conversation_history:
            file.write(f"User: {user_input}\nCapy: {response}\n\n")

def enter_sleep_mode():
    """Enter sleep mode after a period of inactivity."""
    print("Device is now in sleep mode. Waiting for movement to wake up.")

    sleep_file_path = str(Path(__file__).parent / "sleep.mp3")
    stillthere_file_path = str(Path(__file__).parent / "stillthere.mp3")
    leaving_file_path = str(Path(__file__).parent / "leaving.mp3")

    if silent_count > 1:
        print("idle too long, I'm leaving here.")
        subprocess.run(['/usr/bin/mpg123', str(leaving_file_path)])
        sys.exit()

    subprocess.run(['/usr/bin/mpg123', str(sleep_file_path)])
    sleep_time = 30 
    print("sleeping time", sleep_time)
    time.sleep(sleep_time)

    print("Device has been woken up.")
    subprocess.run(['/usr/bin/mpg123', str(stillthere_file_path)])

def main():
    """Main function to initialize the device and handle interactions."""
    setup()
    pwm = setup_servo()

    # Play introduction sounds
    intro_file_path = str(Path(__file__).parent / "capyshort.mp3")
    subprocess.run(['/usr/bin/mpg123', str(intro_file_path)])

    greeting_file_path = str(Path(__file__).parent / "greeting.mp3")
    play_audio_and_move_mouth(greeting_file_path, pwm)

    # Main interaction loop
    while True:
        print("Please speak into the microphone. Say 'exit' to quit.")
        record_audio("user_input.wav", 5)

        transcription = transcribe("user_input.wav")
        print("Transcribed Text:", transcription)

        # Handle exit conditions
        exit_phrases = ["exit", "stop stop", "stop. stop", "stop, stop", "bye, bye", "bye-bye", "再見", "再见", "さようなら", "じゃね", "adiós", "hasta luego", "chao", "byebye", "bye bye"]
        if any(phrase in transcription.lower() for phrase in exit_phrases):
            print("Exiting the program.")
            exit_file_path = str(Path(__file__).parent / "exit.mp3")
            play_audio_and_move_mouth(exit_file_path, pwm)
            save_history_to_file()
            break

        # Handle sleep triggers
        sleep_triggers = ["thank you so much for watching", "thank you for watching", "視頻をご", "視聴", "i'll be back", "be right back", ". ."]
        if any(trigger in transcription.lower() for trigger in sleep_triggers):
            print("User has stopped interacting. Entering sleep mode.")
            silent_count += 1
            enter_sleep_mode()
            continue
        else:
            silent_count = 0

        # Play waiting sound and get response from GPT
        should_stop_waiting_sound = False
        wait_file_path = str(Path(__file__).parent / "wait.wav")
        waiting_thread = threading.Thread(target=play_waiting_sound, args=(wait_file_path,))
        waiting_thread.start()

        response = get_response_from_gpt4(transcription)
        print("GPT Response:", response)

        speak(response, pwm)
        log_conversation(transcription, response)

        should_stop_waiting_sound = True
        waiting_thread.join()

if __name__ == "__main__":
    try:
        main()
    finally:
        save_history_to_file()
        subprocess.run(["python3", "summary.py"])
        GPIO.cleanup()

