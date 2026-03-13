from __future__ import annotations

import logging
from pathlib import Path

from plexapi.server import PlexServer
from plexapi.video import Movie

logger = logging.getLogger(__name__)


def connect_plex(url: str, token: str) -> PlexServer:
    """Connect to a Plex Media Server.

    Args:
        url: Base URL of the Plex server (e.g., http://localhost:32400).
        token: Plex authentication token.

    Returns:
        An authenticated PlexServer instance.
    """
    return PlexServer(url, token)


def build_path_map(server: PlexServer) -> dict[str, Movie]:
    """Build a normalized filepath -> Plex Movie mapping for all movie libraries.

    Args:
        server: An authenticated PlexServer instance.

    Returns:
        A dictionary mapping resolved file paths to Plex Movie objects.
    """
    path_map: dict[str, Movie] = {}
    for section in server.library.sections():
        if section.type != "movie":
            continue
        for item in section.all():
            for media in item.media:
                for part in media.parts:
                    normalized = _normalize_path(part.file)
                    path_map[normalized] = item
    logger.info("Built path map with %d entries", len(path_map))
    return path_map


def _normalize_path(path_str: str) -> str:
    """Normalize a path string for consistent comparison.

    Args:
        path_str: Raw path string from Plex.

    Returns:
        Resolved absolute path string, or empty string if input is falsy.
    """
    return str(Path(path_str).resolve()) if path_str else ""
