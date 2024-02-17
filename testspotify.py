import time
import threading
import subprocess
from spotify_control import SpotifyControl

def play_sound_with_mpg123(sound_file):
    print("Playing sound with mpg123...")
    subprocess.run(["mpg123", sound_file])
    print("Sound playback finished.")

def spotify_playback():
    # Initialize the SpotifyControl class
    spotify_control = SpotifyControl()

    # List all available devices
    spotify_control.list_all_devices()

    # Replace 'your_device_id' with the actual device ID and 'song name' with your search query
    #spotify_control.play_music_on_spotify('3a00a2be23d1de3d94b3c51ce93f1d53bbadf46a')
    spotify_control.play_music_on_spotify('402b4963fefe6692f4f6a725d27cc0171c33747c')
    # Assuming 'play_music_on_spotify' is non-blocking or handles playback in a way that doesn't indefinitely block the thread

    # Optionally, stop music on a specific device
    # spotify_control.stop_music_on_spotify('your_device_id')

# Specify the sound file you want to play with mpg123
sound_file = "greeting.mp3"

# Create thread for Spotify playback
spotify_thread = threading.Thread(target=spotify_playback)

# Create thread for playing sound with mpg123
mpg123_thread = threading.Thread(target=play_sound_with_mpg123, args=(sound_file,))

# Start the threads
spotify_thread.start()
time.sleep(1)
mpg123_thread.start()

# Wait for both threads to complete
spotify_thread.join()
mpg123_thread.join()

print("Both playbacks completed.")

