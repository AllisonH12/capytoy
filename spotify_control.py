import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyControl:
    def __init__(self):
        # Spotify setup
        scope = "user-read-playback-state,user-modify-playback-state,user-library-read"
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


    def play_music_on_spotify(self, preferred_device_id, search_query='Capybara'):
        devices = self.sp.devices()
        device_id_to_use = None
        device_name_to_use = None

        # Search for the preferred device by ID
        for device in devices['devices']:
            if device['id'] == preferred_device_id:
                device_id_to_use = preferred_device_id
                device_name_to_use = device['name']
                break

        # If the preferred device is not found, select an available device
        if not device_id_to_use and devices['devices']:
            # Optionally, filter devices to select based on certain criteria
            # For example, you might prefer devices that are currently active:
            # active_devices = [d for d in devices['devices'] if d['is_active']]
            # if active_devices:
            #     device = active_devices[0]
            # else:
            #     device = devices['devices'][0]
        
            # For simplicity, just select the first available device
            device = devices['devices'][0]
            device_id_to_use = device['id']
            device_name_to_use = device['name']
            print(f"No preferred device found. Using available device: '{device_name_to_use}'")


        # Handle special case for "Liked Songs"
        if search_query.lower() == "liked songs":
            try:
                # Fetch the user's liked songs (Spotify calls them "Saved Tracks")
                results = self.sp.current_user_saved_tracks(limit=20)  # Spotify's limit for start_playback is 50 URIs
                track_uris = [item['track']['uri'] for item in results['items']]
                if track_uris:
                    # Attempt to play the first few liked songs
                    self.sp.start_playback(device_id=device_id_to_use, uris=track_uris[:20])  # Adjust as needed
                    print(f"Playing Liked Songs on '{device_name_to_use}' (ID: {device_id_to_use})")
                    return device_name_to_use, "Liked Songs"
                else:
                    print("No Liked Songs found.")
                    return None, None
            except Exception as e:
                print(f"Error playing Liked Songs: {e}")
                # Optionally fallback to the default behavior or handle the error differently
                return None, None

    # The rest of your function for handling other search queries remains unchanged


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
    
