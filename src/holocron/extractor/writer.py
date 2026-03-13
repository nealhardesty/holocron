from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from holocron.constants import MEDIA_EXTENSIONS
from holocron.models import CastMember, Director, Genre, MovieMetadata
from holocron.nfo import write_nfo

logger = logging.getLogger(__name__)


def _derive_media_id(filepath: Path) -> str:
    """Derive a short unique ID from a file path using SHA-256.

    Args:
        filepath: Path to the media file.

    Returns:
        First 16 hex characters of the SHA-256 hash of the filepath string.
    """
    return hashlib.sha256(str(filepath).encode()).hexdigest()[:16]


def plex_to_metadata(plex_item: Any, filepath: Path) -> MovieMetadata:
    """Convert a plexapi Movie object to a MovieMetadata dataclass.

    Args:
        plex_item: A plexapi Movie object.
        filepath: Local path to the media file.

    Returns:
        A populated MovieMetadata instance.
    """
    duration_ms = getattr(plex_item, "duration", None) or 0
    runtime_min = round(duration_ms / 60000) if duration_ms else None

    genres = [Genre(name=g.tag) for g in getattr(plex_item, "genres", [])]
    directors = [Director(name=d.tag) for d in getattr(plex_item, "directors", [])]
    cast = [
        CastMember(name=r.tag, role=getattr(r, "role", "") or "")
        for r in getattr(plex_item, "roles", [])
    ]

    return MovieMetadata(
        media_id=_derive_media_id(filepath),
        filepath=filepath,
        title=getattr(plex_item, "title", "") or "",
        year=getattr(plex_item, "year", None),
        plot=getattr(plex_item, "summary", "") or "",
        runtime=runtime_min,
        mpaa=getattr(plex_item, "contentRating", "") or "",
        genres=genres,
        directors=directors,
        cast=cast,
        last_modified=filepath.stat().st_mtime if filepath.exists() else 0.0,
    )


def process_directory(
    directory: Path,
    path_map: dict[str, Any],
    overwrite: bool = False,
) -> int:
    """Walk directory for media files, write .nfo sidecars from Plex metadata.

    Args:
        directory: Root directory to scan recursively.
        path_map: Mapping of resolved filepath strings to Plex Movie objects.
        overwrite: If True, overwrite existing .nfo files.

    Returns:
        Number of .nfo files written.
    """
    processed = 0
    for media_file in _iter_media_files(directory):
        normalized = str(media_file.resolve())
        plex_item = path_map.get(normalized)
        if plex_item is None:
            logger.warning("No Plex match for: %s", media_file)
            continue

        nfo_path = media_file.with_suffix(".nfo")
        if nfo_path.exists() and not overwrite:
            logger.debug("Skipping existing NFO: %s", nfo_path)
            continue

        metadata = plex_to_metadata(plex_item, media_file)
        write_nfo(metadata, nfo_path)
        logger.info("Wrote NFO: %s", nfo_path)
        processed += 1

    return processed


def _iter_media_files(directory: Path):
    """Yield all media files recursively under directory.

    Args:
        directory: Root directory to scan.

    Yields:
        Path objects for each media file found.
    """
    for path in directory.rglob("*"):
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS:
            yield path
