import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def list_all_devices(sp):
    devices = sp.devices()
    print("Available devices:")
    for device in devices['devices']:
        print(f"ID: {device['id']}, Name: {device['name']}, Type: {device['type']}, Active: {device['is_active']}")

# Call this function after authenticating with Spotify

def play_music_on_spotify(sp, device_id):
    results = sp.search(q='your favorite song', limit=1, type='track')
    track_uri = results['tracks']['items'][0]['uri']
    sp.start_playback(device_id=device_id, uris=[track_uri])


# Spotify setup
scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="6bd938f2ed5e46c589d142312045eff1",
                                               client_secret="2de2ca1ff32443e99c6bcb87fbdd8eb6",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope=scope))
# Call this function after authenticating with Spotify
list_all_devices(sp)

# Example usage, replace 'your_device_id' with the actual device ID
play_music_on_spotify(sp, '3a00a2be23d1de3d94b3c51ce93f1d53bbadf46a')
