from dataclasses import dataclass


@dataclass
class Location:
    latitude: str
    longitude: str

    def as_str(self):
        return f"{self.latitude}, {self.longitude}"
