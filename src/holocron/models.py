from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CastMember:
    """A cast member with their role in a film."""

    name: str
    role: str


@dataclass
class Director:
    """A film director."""

    name: str


@dataclass
class Genre:
    """A film genre."""

    name: str


@dataclass
class MovieMetadata:
    """Complete metadata for a movie, parsed from an NFO file or Plex API."""

    media_id: str  # sha256(filepath)[:16]
    filepath: Path
    title: str
    year: int | None = None
    plot: str = ""
    runtime: int | None = None  # minutes
    mpaa: str = ""
    genres: list[Genre] = field(default_factory=list)
    directors: list[Director] = field(default_factory=list)
    cast: list[CastMember] = field(default_factory=list)
    last_modified: float = 0.0
