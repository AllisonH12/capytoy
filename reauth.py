from spotipy.oauth2 import SpotifyOAuth

sp_oauth = SpotifyOAuth(client_id='your_client_id',
                        client_secret='your_client_secret',
                        redirect_uri='your_redirect_uri',
                        scope="user-read-playback-state,user-modify-playback-state,user-library-read")

