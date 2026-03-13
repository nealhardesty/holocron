from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

MEDIA_EXTENSIONS: frozenset[str] = frozenset(
    {".mkv", ".mp4", ".avi", ".m4v", ".ts", ".wmv", ".mov"}
)

NFO_ROOT_TAG = "movie"

try:
    VERSION = _pkg_version("holocron")
except PackageNotFoundError:
    VERSION = "0.0.0-dev"
