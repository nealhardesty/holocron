from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path

from holocron.models import MovieMetadata
from holocron.nfo import parse_nfo

logger = logging.getLogger(__name__)


def scan_nfo_files(directory: Path) -> Generator[Path, None, None]:
    """Recursively yield all .nfo file paths under directory.

    Args:
        directory: Root directory to scan.

    Yields:
        Path objects for each .nfo file found.
    """
    for path in directory.rglob("*.nfo"):
        if path.is_file():
            yield path


def parse_directory(directory: Path) -> Generator[MovieMetadata, None, None]:
    """Parse all .nfo files in directory, yielding MovieMetadata objects.

    Args:
        directory: Root directory to scan for .nfo files.

    Yields:
        MovieMetadata instances for each successfully parsed .nfo file.
    """
    for nfo_path in scan_nfo_files(directory):
        try:
            yield parse_nfo(nfo_path)
        except Exception as exc:
            logger.warning("Failed to parse %s: %s", nfo_path, exc)
