# -*- coding: utf-8 -*-
import os
import os.path
import webbrowser
from typing import List, Optional, Tuple

import requests

from frontend.lib.artist import Artist
from frontend.lib.vinyl import Vinyl
from PySide6.QtGui import QImage


class VinylLibraryAPI(object):
    API_URL: str = f"http://{os.environ.get('VINYL_LIBRARY_ADDRESS', '127.0.0.1:8000')}/vinyl_library"

    def __init__(self):
        self._artists: Optional[list] = None
        self._vinyls: Optional[list] = None
        self._images = dict()

    # [ARTISTS] ========================================================================================================

    def get_artists(self) -> List[Artist]:
        url = f"{self.API_URL}/artists"
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
        return [Artist.from_json(data) for data in response.json()]

    @property
    def artists(self) -> List[Artist]:
        if self._artists is None:
            self._artists = self.get_artists()
        return self._artists

    @artists.setter
    def artists(self, artist: Artist) -> None:
        if self._artists is None:
            self._artists = [artist]
            return
        self._artists.append(artist)

    def add_artist(self, name: str) -> Tuple[Artist, bool]:
        url = f"{self.API_URL}/artists"
        response = requests.post(url, json=name)
        if not response.ok:
            response.raise_for_status()
        new_artist = Artist.from_json(response.json())
        if new_artist not in self.artists:
            self.artists.append(new_artist)
            return new_artist, True
        return new_artist, False

    def find_artist_by_name(self, name: str) -> Optional[Artist]:
        return {a.name: a for a in self.artists}.get(name)

    def get_vinyls_for_artist(self, artist: Artist) -> List[Vinyl]:
        url = f"{self.API_URL}/artists/list_vinyls?id={artist.id}"
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
        return [Vinyl.from_json(data) for data in response.json()]

    def delete_artist(self, artist: Artist) -> None:
        url = f"{self.API_URL}/artists/delete?id={artist.id}"
        response = requests.post(url)
        if not response.ok:
            response.raise_for_status()

    def update_artist(self, artist: Artist, new_name: str) -> Artist:
        url = f"{self.API_URL}/artists/update?id={artist.id}"
        response = requests.post(url, data=new_name)
        if not response.ok:
            response.raise_for_status()
        return Artist.from_json(response.json())

    # [Vinyls] =========================================================================================================

    def get_vinyls(self) -> List[Vinyl]:
        url = f"{self.API_URL}/vinyls"
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
        return [Vinyl.from_json(data) for data in response.json()]

    @property
    def vinyls(self) -> List[Vinyl]:
        if self._vinyls is None:
            self._vinyls = self.get_vinyls()
        return self._vinyls

    def add_vinyl(
        self, name: str, artist_id: int, artist_name: str, cover_file_name: str
    ) -> Tuple[Vinyl, bool]:
        url = f"{self.API_URL}/vinyls"
        response = requests.post(
            url,
            json={
                "name": name,
                "artist_id": artist_id,
                "artist_name": artist_name,
                "cover_file_name": cover_file_name,
            },
        )
        if not response.ok:
            response.raise_for_status()
        new_vinyl = Vinyl.from_json(response.json())
        if new_vinyl not in self.artists:
            self.vinyls.append(new_vinyl)
            return new_vinyl, True
        return new_vinyl, False

    @staticmethod
    def listen_on_deezer(vinyl):
        url = f'https://api.deezer.com/search?q=album:"{vinyl.name}"'
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
        data = response.json().get("data")
        if not data:
            raise ValueError(f"{vinyl.pretty_name} not found on Deezer")
        album_id = data[0]["album"]["id"]
        url = f"https://www.deezer.com/fr/album/{album_id}"
        webbrowser.open(url)

    @staticmethod
    def listen_on_youtube(vinyl):
        url = f"https://www.youtube.com/results?search_query={vinyl.artist_name} {vinyl.name}"
        webbrowser.open(url)

    def listen_vinyl(self, site: str, vinyl: Vinyl) -> None:
        method = {
            "deezer": self.listen_on_deezer,
            "youtube": self.listen_on_youtube,
        }.get(site)
        method(vinyl)

    def update_vinyl(
        self,
        id_: int,
        name: str,
        artist_id: int,
        artist_name: str,
        cover_file_name: str,
    ) -> Vinyl:
        url = f"{self.API_URL}/vinyls/update?id={id_}"
        response = requests.post(
            url,
            json={
                "name": name,
                "artist_id": artist_id,
                "artist_name": artist_name,
                "cover_file_name": cover_file_name,
            },
        )
        if not response.ok:
            response.raise_for_status()

        updated_vinyl = Vinyl.from_json(response.json())
        for i, vinyl in enumerate(self.vinyls):
            if vinyl.id == updated_vinyl.id:
                self.vinyls[i] = updated_vinyl
                break
        return updated_vinyl

    def delete_vinyl(self, vinyl: Vinyl) -> None:
        url = f"{VinylLibraryAPI.API_URL}/vinyls/delete?id={vinyl.id}"
        response = requests.post(url)
        if not response.ok:
            response.raise_for_status()
        self.vinyls.remove(vinyl)

    def shuffle_vinyls(self, count: int) -> List[Vinyl]:
        url = f"{self.API_URL}/vinyls/shuffle?count={count}"
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()
        return [Vinyl.from_json(data) for data in response.json()]

    # [IMAGES] =========================================================================================================

    def get_image(self, image_name: str) -> QImage:
        loaded_image = self._images.get(image_name)
        if loaded_image is not None:
            return loaded_image

        url = f"{self.API_URL}/images/{image_name}"
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()

        image = QImage()
        image.loadFromData(response.content)
        self._images[image_name] = image
        setattr(image, "name", image_name)
        return image

    def get_images(self) -> List[QImage]:
        url = f"{self.API_URL}/images"
        response = requests.get(url)
        if not response.ok:
            response.raise_for_status()

        return [self.get_image(name) for name in response.json()]

    def upload_image(self, image_path: str) -> QImage:
        image_name = os.path.split(image_path)[-1]
        url = f"{self.API_URL}/images/upload/{image_name}"

        with open(image_path, "rb") as f:
            response = requests.post(url, data=f.read())

        if not response.ok:
            response.raise_for_status()

        return self.get_image(image_name)
