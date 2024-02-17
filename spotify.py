import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def list_all_devices(sp):
    devices = sp.devices()
    print("Available devices:")
    for device in devices['devices']:
        print(f"ID: {device['id']}, Name: {device['name']}, Type: {device['type']}, Active: {device['is_active']}")


def play_music_on_spotify(sp, preferred_device_id):
    devices = sp.devices()
    device_id_to_use = None
    device_name_to_use = None

    # Search for the preferred device by ID
    for device in devices['devices']:
        if device['id'] == preferred_device_id:
            device_id_to_use = preferred_device_id
            device_name_to_use = device['name']
            break
    
    # If the preferred device is not found, use the first available device
    if not device_id_to_use and devices['devices']:
        device_id_to_use = devices['devices'][0]['id']
        device_name_to_use = devices['devices'][0]['name']
    
    if device_id_to_use:
        # Play music on the selected device
        results = sp.search(q='your favorite song', limit=1, type='track')
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(device_id=device_id_to_use, uris=[track_uri])
        print(f"Playing music on '{device_name_to_use}' (ID: {device_id_to_use})")
    else:
        # Handle the case where no devices are available
        print("No available devices to play music on.")

# Spotify setup
scope = "user-read-playback-state,user-modify-playback-state"

client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope="user-read-playback-state,user-modify-playback-state"))


# Call this function after authenticating with Spotify
list_all_devices(sp)


# Example usage, replace 'your_device_id' with the actual device ID
play_music_on_spotify(sp, '3a00a2be23d1de3d94b3c51ce93f1d53bbadf46a')
