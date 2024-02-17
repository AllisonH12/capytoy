import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyControl:
    def __init__(self):
        # Spotify setup
        scope = "user-read-playback-state,user-modify-playback-state"
        client_id = os.getenv('SPOTIPY_CLIENT_ID')
        client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                            client_secret=client_secret,
                                                            redirect_uri=redirect_uri,
                                                            scope=scope))
    
    def list_all_devices(self):
        devices = self.sp.devices()
        print("Available devices:")
        for device in devices['devices']:
            print(f"ID: {device['id']}, Name: {device['name']}, Type: {device['type']}, Active: {device['is_active']}")

    def play_music_on_spotify(self, preferred_device_id, search_query='your favorite song'):
        devices = self.sp.devices()
        device_id_to_use = None
        device_name_to_use = None

        # Search for the preferred device by ID
        for device in devices['devices']:
            if device['id'] == preferred_device_id:
                device_id_to_use = preferred_device_id
                device_name_to_use = device['name']
                break

        if device_id_to_use:
            # Play music on the selected device
            results = self.sp.search(q=search_query, limit=1, type='track')
            if results['tracks']['items']:
                track_uri = results['tracks']['items'][0]['uri']
                self.sp.start_playback(device_id=device_id_to_use, uris=[track_uri])
                print(f"Playing music on '{device_name_to_use}' (ID: {device_id_to_use})")
            else:
                print("No tracks found for your query.")
        else:
            # Handle the case where no devices are available
            print("No available devices to play music on.")

    def stop_music_on_spotify(self, device_id=None):
        try:
            # Stop music playback on the specified device
            self.sp.pause_playback(device_id=device_id)
            print(f"Music playback stopped on device ID: {device_id}")
        except spotipy.exceptions.SpotifyException as e:
            if device_id:
                print(f"Failed to stop music on device ID: {device_id}. Error: {e}")
            else:
                print("Device ID not specified. Unable to stop music playback.")

