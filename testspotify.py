from spotify_control import SpotifyControl

# Initialize the SpotifyControl class
spotify_control = SpotifyControl()

# List all available devices
spotify_control.list_all_devices()

# Replace 'your_device_id' with the actual device ID and 'song name' with your search query
#spotify_control.play_music_on_spotify('3a00a2be23d1de3d94b3c51ce93f1d53bbadf46a')

# Stop music on a specific device
spotify_control.stop_music_on_spotify()

