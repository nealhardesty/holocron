from __future__ import annotations

import hashlib
from pathlib import Path

from lxml import etree

from holocron.models import CastMember, Director, Genre, MovieMetadata


def _derive_media_id(filepath: Path) -> str:
    """Derive a short unique ID from a file path using SHA-256.

    Args:
        filepath: Path to the media file.

    Returns:
        First 16 hex characters of the SHA-256 hash of the filepath string.
    """
    return hashlib.sha256(str(filepath).encode()).hexdigest()[:16]


def write_nfo(metadata: MovieMetadata, output_path: Path) -> None:
    """Write a MovieMetadata object to a Jellyfin/Kodi-compatible .nfo XML file.

    Args:
        metadata: The movie metadata to serialize.
        output_path: Destination path for the .nfo file.
    """
    root = etree.Element("movie")

    def sub(tag: str, text: str | None) -> None:
        el = etree.SubElement(root, tag)
        el.text = text or ""

    sub("title", metadata.title)
    if metadata.year is not None:
        sub("year", str(metadata.year))
    sub("plot", metadata.plot)
    if metadata.mpaa:
        sub("mpaa", metadata.mpaa)
    if metadata.runtime is not None:
        sub("runtime", str(metadata.runtime))
    for genre in metadata.genres:
        sub("genre", genre.name)
    for director in metadata.directors:
        sub("director", director.name)
    for member in metadata.cast:
        actor_el = etree.SubElement(root, "actor")
        name_el = etree.SubElement(actor_el, "name")
        name_el.text = member.name
        role_el = etree.SubElement(actor_el, "role")
        role_el.text = member.role

    tree = etree.ElementTree(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        str(output_path),
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )


def parse_nfo(nfo_path: Path) -> MovieMetadata:
    """Parse a .nfo XML file into a MovieMetadata dataclass.

    Args:
        nfo_path: Path to the .nfo file to parse.

    Returns:
        A MovieMetadata instance populated from the XML contents.
    """
    parser = etree.XMLParser(recover=True)
    try:
        tree = etree.parse(str(nfo_path), parser)
        root = tree.getroot()
    except Exception:
        root = etree.Element("movie")

    def text(tag: str) -> str:
        el = root.find(tag)
        return (el.text or "").strip() if el is not None else ""

    year_str = text("year")
    year = int(year_str) if year_str.isdigit() else None

    runtime_str = text("runtime")
    runtime = int(runtime_str) if runtime_str.isdigit() else None

    genres = [Genre(name=el.text.strip()) for el in root.findall("genre") if el.text]
    directors = [
        Director(name=el.text.strip()) for el in root.findall("director") if el.text
    ]

    cast = []
    for actor_el in root.findall("actor"):
        name_el = actor_el.find("name")
        role_el = actor_el.find("role")
        name = (name_el.text or "").strip() if name_el is not None else ""
        role = (role_el.text or "").strip() if role_el is not None else ""
        if name:
            cast.append(CastMember(name=name, role=role))

    last_modified = nfo_path.stat().st_mtime if nfo_path.exists() else 0.0
    media_id = _derive_media_id(nfo_path)

    return MovieMetadata(
        media_id=media_id,
        filepath=nfo_path,
        title=text("title"),
        year=year,
        plot=text("plot"),
        runtime=runtime,
        mpaa=text("mpaa"),
        genres=genres,
        directors=directors,
        cast=cast,
        last_modified=last_modified,
    )
