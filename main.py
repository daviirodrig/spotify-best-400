import json
import os

import dotenv
import spotipy

from spotify_utils import Spotify

dotenv.load_dotenv()

playlist_id = os.environ["PLAYLIST_ID"]
new_playlist_id = os.environ["NEW_PLAYLIST_ID"]
sp = Spotify(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
)

spp = spotipy.Spotify(
    oauth_manager=spotipy.oauth2.SpotifyOAuth(
        client_id=os.environ["SPOTIPY_CLIENT_ID"],
        client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
        scope="playlist-modify-public,playlist-modify-private",
    )
)


def get_last_tracks(playlist_tracks: list, track_count: int) -> list:
    if track_count >= len(playlist_tracks):
        return playlist_tracks

    new_tracks = playlist_tracks[-track_count:]

    return new_tracks


def main():
    playlist_tracks = sp.get_playlist_tracks(playlist_id)
    new_tracks = get_last_tracks(playlist_tracks, 400)
    tracks_uris: list[str] = [f"spotify:track:{i['track']['id']}" for i in new_tracks]
    tracks_uris.reverse()
    is_first = True
    for i in sp.split_list(tracks_uris, 100):
        if is_first:
            spp.playlist_replace_items(new_playlist_id, i)
            is_first = False
        else:
            spp.playlist_add_items(new_playlist_id, i)


if __name__ == "__main__":
    main()
