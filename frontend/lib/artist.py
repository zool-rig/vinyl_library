import json
from dataclasses import dataclass


@dataclass
class Artist:
    id: int
    name: str

    @classmethod
    def from_json(cls, data):
        return cls(
            data["id"],
            data["name"]
        )

    @property
    def pretty_name(self):
        return " ".join(self.name.split("_")).title()
