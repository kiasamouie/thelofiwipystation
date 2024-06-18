from dataclasses import dataclass, field, InitVar

@dataclass
class Track:
    id: int
    title: str
    url: str