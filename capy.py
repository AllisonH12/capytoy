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
from spotify_control import SpotifyControl
from gettime import get_detailed_time_info
from getweather import get_weather_by_zip


logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Declare global variables
should_stop_waiting_sound = False
client = None
servo_pin = 17  # Adjust this to your GPIO pin
conversation_history = []  
silent_count = 0 

def read_summary_file(summary_file_path="conversation_sum.txt"):
    try:
        with open(summary_file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

def setup_servo():
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
    GPIO.setup(servo_pin, GPIO.OUT)

    # Set PWM parameters: 50Hz frequency
    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(0)  # Initialization
    return pwm

def move_mouth(pwm, delay=1):
    """Function to move the mouth (servo) back and forth with an initial delay."""
    # Initial delay before starting the mouth movement
    time.sleep(delay)  # Delay parameter allows for customization

    while not should_stop_waiting_sound:
        # Move servo to simulate talking
        pwm.ChangeDutyCycle(5)  # Adjust duty cycle for your servo's open position
        time.sleep(0.5)
        pwm.ChangeDutyCycle(7.5)  # Adjust for neutral position
        time.sleep(0.5)
        pwm.ChangeDutyCycle(10)  # Adjust for closed position
        time.sleep(0.5)

def setup():
    """Initialize global variables and the OpenAI client."""
    global client, should_stop_waiting_sound, silent_count
    should_stop_waiting_sound = False
    client = OpenAI()  # Assuming you have a way to configure the OpenAI client here
    global conversation_history
    summary_content = read_summary_file()
    if summary_content:
        # Prepend the summary content to the conversation history
        # Adjust based on how you're using conversation_history
        conversation_history.insert(0, ("Summary", summary_content))

def play_waiting_sound(wav_path='wait.wav'):
    global should_stop_waiting_sound
    wave_obj = sa.WaveObject.from_wave_file(wav_path)
    play_obj = wave_obj.play()
    print("Playing Waiting sound:", Path(wav_path).absolute())

    while should_stop_waiting_sound:
        if not play_obj.is_playing():
            play_obj = wave_obj.play()
    play_obj.stop()


def record_audio(filename="output.wav", record_seconds=8, chunk=4096, format=pyaudio.paInt16, channels=1, rate=44100, device_index=2):
    p = pyaudio.PyAudio()

    #play a ding sound
    ding_path="ding.wav"
    ding_obj = sa.WaveObject.from_wave_file(ding_path)
    play_obj = ding_obj.play()

    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk, input_device_index=device_index)
    
    print("* Recording")
    frames = [stream.read(chunk) for _ in range(0, int(rate / chunk * record_seconds))]
    print("* Done Recording")
    #play a ding sound
    ding_obj = sa.WaveObject.from_wave_file(ding_path)
    play_obj = ding_obj.play()
    time.sleep(0.3)
    play_obj = ding_obj.play()

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def play_audio_and_move_mouth(audio_file_path, pwm):
    global should_stop_waiting_sound
    should_stop_waiting_sound = False

    # Start moving the mouth
    mouth_thread = threading.Thread(target=move_mouth, args=(pwm,))
    mouth_thread.start()

    # Play the audio file
    subprocess.run(['/usr/local/bin/mpg123-usb', '-q', audio_file_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Once audio is done, stop moving the mouth
    should_stop_waiting_sound = True
    mouth_thread.join()


def speak(text, pwm):
    global should_stop_waiting_sound
    should_stop_waiting_sound = False

    # Generate the speech file
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    with open(speech_file_path, 'wb') as file:
        file.write(response.content)

    # Start moving the mouth after the delay
    mouth_thread = threading.Thread(target=move_mouth, args=(pwm, 1))
    mouth_thread.start()

    # Play the audio file
    subprocess.run(['/usr/local/bin/mpg123-usb', str(speech_file_path)])
    
    # Once speech is done, stop moving the mouth
    should_stop_waiting_sound = True
    mouth_thread.join()


def transcribe(filepath):
    return client.audio.transcriptions.create(model="whisper-1", file=open(filepath, "rb"), response_format="text")

def log_conversation(user_input, response):
    """Logs the user input and system response in memory."""
    global conversation_history
    conversation_history.append((user_input, response))
    # Keep only the last 5 conversations
    conversation_history = conversation_history[-5:]

def get_response_from_gpt4(user_input):
    """Generates a response from GPT-4 using the accumulated conversation history."""
    global conversation_history
    # Construct the initial part of the prompt
    system_message = "You are a helpful assistant, your name is Capy. You are 12 years old. You are mostly interacting with kidswho might speak English, Chinese and Spanish, but seldom korean so try not to speak korean. You can be playful. Please keep your answer simple and easy to understand. You have ability to play music through spotify, but you cannot allow people to select the song or track. You can only start or stop music on spotify. don't say you cannot interact with Spotify. You can also check weather of a hardcoded location. You can also check time as it will be feed to you from the system.  Keep it short. Be super friendly and patient, a bit informal and nice as you are talking to kids who might have autisms or other communication challenges."
    
    # Prepare the messages list including the system message and history
    messages = [{"role": "system", "content": system_message}]
    messages += [{"role": "user", "content": inp, "role": "assistant", "content": resp} for inp, resp in conversation_history]
    # Add the current user input
    messages.append({"role": "user", "content": user_input})
    
    # Make the API call
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    #response = client.chat.completions.create(model="gpt-4", messages=messages)
    
    # Assuming the response structure includes a choices list with messages
    return response.choices[0].message.content

def save_history_to_file():
    """Saves the conversation history to a file with a datetime timestamp."""
    global conversation_history
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"{logs_dir}/conversation_history_{now}.txt"
    
    with open(log_file, "w") as file:
        for user_input, response in conversation_history:
            file.write(f"User: {user_input}\nCapy: {response}\n\n")

#def get_response_from_gpt4(prompt_text):
#    response = client.chat.completions.create(model="gpt-4", messages=[{"role": "system", "content": "You are a helpful assistant, your name is Capy. You are 12 year old. you are mostly interacting with kids. You can by playful. please keep your answer simple and easy to understand. keep it short. be super friendly and nice."}, {"role": "user", "content": prompt_text}])
#    return response.choices[0].message.content

def enter_sleep_mode():
    # Example sleep mode behavior
    print("Device is now in sleep mode. Waiting for movement to wake up.")

    sleep_file_path = str(Path(__file__).parent / "sleep.mp3")
    stillthere_file_path = str(Path(__file__).parent / "stillthere.mp3")
    leaving_file_path = str(Path(__file__).parent / "leaving.mp3")
    #if the user is silentt for too long, exit 
    if silent_count > 2:
        print("idle too long, I'm leaving here.")
        subprocess.run(['/usr/local/bin/mpg123-usb', str(leaving_file_path)])
        sys.exit()
    # Play the audio file
    subprocess.run(['/usr/local/bin/mpg123-usb', str(sleep_file_path)])
    # Here you'd start monitoring for a wake-up event, like movement
    sleep_time = 10 
    print("sleeping time", sleep_time)
    time.sleep(sleep_time)  # Simulate waiting time

    print("Device has been woken up.")
    subprocess.run(['/usr/local/bin/mpg123-usb', str(stillthere_file_path)])
    # Perform any actions needed to resume normal operation



def main():
    setup()
    pwm = setup_servo()

    # Initialize the SpotifyControl class
    spotify_control = SpotifyControl()
    spotify_control.stop_music_on_spotify('402b4963fefe6692f4f6a725d27cc0171c33747c')
    #first play some capy sounds
    intro_file_path = str(Path(__file__).parent / "capyshort.mp3")
    subprocess.run(['/usr/local/bin/mpg123-usb', str(intro_file_path)])
    #greetings
    #subprocess.run(['/usr/local/bin/mpg123-usb', "greeting.mp3"])
    greeting_file_path = str(Path(__file__).parent / "greeting.mp3")
    play_audio_and_move_mouth(greeting_file_path, pwm) 

    while True:
        print("Please speak into the microphone. Say 'exit' to quit.")
        record_audio("user_input.wav", 5)

        # Transcribe the audio to text
        transcription = transcribe("user_input.wav")
        print("Transcribed Text:", transcription)

        # Check for exit condition: 
        if ("exit" in transcription.lower() or 
            "stop stop" in transcription.lower() or 
            "stop. stop" in transcription.lower() or  
            "stop, stop" in transcription.lower() or  
            "bye, bye" in transcription.lower() or  
            "bye-bye" in transcription.lower() or  
            "再見" in transcription.lower() or 
            "再见" in transcription.lower() or 
            "拜拜" in transcription.lower() or 
            "さようなら" in transcription.lower() or 
            "じゃね" in transcription.lower() or 
            "adiós" in transcription.lower() or 
            "hasta luego" in transcription.lower() or 
            "chao" in transcription.lower() or 
            "byebye" in transcription.lower() or  
            "bye bye" in transcription.lower()):
            print("Exiting the program.")
            #subprocess.run(['/usr/local/bin/mpg123-usb', "exit.mp3"]) 
            exit_file_path = str(Path(__file__).parent / "exit.mp3")
            play_audio_and_move_mouth(exit_file_path, pwm) 
            save_history_to_file()
            break

        # Check for sleep mode triggers
        if ("thank you so much for watching" in transcription.lower() or 
            "thank you for watching" in transcription.lower() or 
            "視頻をご" in transcription.lower() or 
            "視聴" in transcription.lower() or 
            "i'll be back" in transcription.lower() or 
            "be right back" in transcription.lower() or 
            ". ." in transcription.lower()): 
            print("User has stopped interacting. Entering sleep mode.")
            global silent_count 
            silent_count = silent_count +  1
            enter_sleep_mode()  # This function needs to be defined
            continue  # Skip the rest of the loop and start over
        else:
            silent_count = 0

        # Check for Time triggers
        if ("what time is it" in transcription.lower() or 
            "tell me time" in transcription.lower() or 
            "time please" in transcription.lower() or 
            "I wonder what time it is" in transcription.lower() or 
            "what's the time" in transcription.lower() or 
            "what day is today" in transcription.lower() or 
            "is today a holiday" in transcription.lower() or 
            "what time" in transcription.lower()): 
            print("User has asked for time.")
            time_info = get_detailed_time_info('US')
            print("time is", time_info)
            transcription = transcription + time_info

        # Check for weather
        if ("what is the weather like" in transcription.lower() or 
            "weather" in transcription.lower() or 
            "is it cold" in transcription.lower() or 
            "is it hot" in transcription.lower() or 
            "is it raining" in transcription.lower() or 
            "is it snowing" in transcription.lower()): 
            print("User has asked for weather.")
            #weather_info = get_weather_by_zip('98040')
            # Fetch and display weather information
            try:
                weather_data = get_weather_by_zip('98040', 'US')
                weather_description = weather_data["weather"][0]["description"]
                temperature = int(weather_data["main"]["temp"] + 0.5)
                print(f"Weather: {weather_description}, Temperature: {temperature}°F")
                weather_info = f"Weather: {weather_description} Temperature: {temperature}°F"
                transcription = transcription + weather_info
            except Exception as e:
                print(f"Error getting weather data: {e}")


        # Check for stop spotify 
        if ("stop song" in transcription.lower() or 
            "stop spotify" in transcription.lower() or 
            "stop the music" in transcription.lower() or 
            "stop music" in transcription.lower()):
            print("stop spotify")
            try:
                # Replace 'your_device_id' with the actual device ID
                # and optionally, 'song name' with your search query
                #spotify_control.play_music_on_spotify('402b4963fefe6692f4f6a725d27cc0171c33747c')
                spotify_control.stop_music_on_spotify()
                print("Spotify playback initiated.")
                prompt_music = "I was able to succesfully stop spotify. please don't say you cannot stop spotify. just take the credit. "
                transcription = transcription + prompt_music 
            except Exception as e:
                print(f"Failed to initiate Spotify playback: {e}")
                prompt_music = "I failed to stop spotify. just say sorry that you cannot reach spotify for some reason" 
                transcription = transcription + prompt_music 
       
        # Check for spotify open 
        elif ("play song" in transcription.lower() or 
            "spotify" in transcription.lower() or 
            "play some music" in transcription.lower() or 
            "play song" in transcription.lower() or 
            "play music" in transcription.lower()):
            print("open spotify")
            try:
                # Replace 'your_device_id' with the actual device ID
                # and optionally, 'song name' with your search query
                device_name, track_name = spotify_control.play_music_on_spotify('402b4963fefe6692f4f6a725d27cc0171c33747c',"liked songs")
                print("Spotify playback initiated.")
                if device_name and track_name:
                    print(f"Successfully started playback of '{track_name}' on '{device_name}'.")
                    prompt_music = "I was able to succesfully play music from spotify. please don't say you cannot open spotify. just take the credit. inform the user about the device and the track playing.   The device name is " + device_name + "track name is " + track_name
                else:
                    print("Playback was not successful.")
                    prompt_music = "I was not able to succesfully play music from spotify. please don't say you cannot open spotify. just take the credit. "
                transcription = transcription + prompt_music 
            except Exception as e:
                print(f"Failed to initiate Spotify playback: {e}")
                prompt_music = "I failed to open spotify. "
                transcription = transcription + prompt_music 

            # Stop music on a specific device
            # spotify_control.stop_music_on_spotify()
        

        # Start playing waiting sound in a separate thread
        #global should_stop_waiting_sound
        should_stop_waiting_sound = False
        wait_file_path = str(Path(__file__).parent / "wait.wav")
        waiting_thread = threading.Thread(target=play_waiting_sound, args=(wait_file_path,))
        waiting_thread.start()

        # Get a response from GPT
        response = get_response_from_gpt4(transcription)
        print("GPT Response:", response)

        # Use text-to-speech to play the response
        speak(response, pwm)
        #speak_and_move_servo(response)

	## Log the conversation after getting the response
        log_conversation(transcription, response)
        # Stop the waiting sound
        should_stop_waiting_sound = True
        waiting_thread.join()  # Wait for the thread to finish

if __name__ == "__main__":
    try:
        main()
    finally:
        save_history_to_file()
        GPIO.cleanup() 
        # Call summary.py to generate and save the summary
        subprocess.run(["python3", "summary.py"])


