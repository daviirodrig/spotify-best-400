import base64
import time
from typing import Generic
from urllib.parse import unquote

import requests


class Spotify:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.access_token_expire = None

    @staticmethod
    def get_id(spotify_input: str):
        # input is uri
        if spotify_input.startswith("spotify:") and len(spotify_input.split(":")) == 3:
            return spotify_input.split(":")[-1]
        # input is url
        else:
            return spotify_input.split("/")[-1].split("?")[0]

    def get_access_token(self):
        if self.access_token and self.access_token_expire:
            now = int(time.time())
            if now < self.access_token_expire:
                return self.access_token
        auth_to_encode = f"{self.client_id}:{self.client_secret}".encode("ascii")
        auth_b64 = base64.b64encode(auth_to_encode)
        body = {"grant_type": "client_credentials"}
        header = {"Authorization": f"Basic {auth_b64.decode('ascii')}"}
        res = requests.post(
            "https://accounts.spotify.com/api/token", data=body, headers=header
        )
        access_token = res.json().get("access_token")
        self.access_token = access_token
        self.access_token_expire = int(time.time()) + 3600
        return access_token

    def get_song_json(self, song):
        song_id = self.get_id(song)
        access_token = self.get_access_token()
        header = {"Authorization": f"Bearer {access_token}"}
        base_url = f"https://api.spotify.com/v1/tracks/{song_id}"
        res_json = requests.get(base_url, headers=header).json()

        return res_json

    def get_playlist_json(self, playlist):
        playlist_id = self.get_id(playlist)
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        res_json = requests.get(base_url, headers=headers).json()
        return res_json

    def get_playlist_tracks(self, playlist):
        pl_json = self.get_playlist_json(playlist)
        tracks = pl_json["tracks"]["items"]
        next_url = pl_json["tracks"]["next"]
        while next_url:
            access_token = self.get_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            res = requests.get(next_url, headers=headers).json()
            next_url = res["next"]
            tracks.extend(res["items"])
        return tracks

    def add_tracks_to_playlist(self, playlist_id, tracks_id: list[str]):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        tracks_uris: list[str] = [f"spotify:track:{i}" for i in tracks_id]
        splited_tracks = self.split_list(tracks_uris, 100)

        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        for id_list in splited_tracks:
            res = requests.post(
                url,
                data={"uris": id_list},
                headers=headers,
            )
            print(res.status_code)

    def split_list(self, input_list: list, sublist_size: int) -> list[list]:
        """
        Splits a list into smaller sublists of a specified size.

        Args:
            input_list (List): The original list to be split.
            sublist_size (int): The size of each sublist.

        Returns:
            List[List]: A list of sublists containing the items from the original list.

        Example:
            >>> original_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
            >>> sublist_size = 100
            >>> sublists = split_list(original_list, sublist_size)
            >>> print(sublists)
            [[1, 2, 3, ..., 19, 20]]
        """

        return [
            input_list[i : i + sublist_size]
            for i in range(0, len(input_list), sublist_size)
        ]
