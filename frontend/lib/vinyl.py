# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class Vinyl:
    id: int
    name: str
    artist_id: int
    artist_name: str
    added_date: int
    cover_file_name: str

    @classmethod
    def from_json(cls, data):
        return cls(
            data["id"],
            data["name"],
            data["artist_id"],
            data["artist_name"],
            data["added_date"],
            data["cover_file_name"],
        )

    @property
    def pretty_name(self):
        return " ".join(self.name.split("_")).title()

    @property
    def artist_pretty_name(self):
        return " ".join(self.artist_name.split("_")).title()

    def as_dict(self):
        return self.__dict__
