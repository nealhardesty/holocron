from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from holocron.materializer.parser import parse_directory
from holocron.materializer.schema import drop_all, init_schema
from holocron.models import MovieMetadata

logger = logging.getLogger(__name__)


def needs_update(
    con: duckdb.DuckDBPyConnection, media_id: str, last_modified: float
) -> bool:
    """Return True if the DB row is missing or older than last_modified.

    Args:
        con: An active DuckDB connection.
        media_id: The unique media identifier to check.
        last_modified: The filesystem modification timestamp to compare against.

    Returns:
        True if the record needs to be updated, False otherwise.
    """
    result = con.execute(
        "SELECT last_modified FROM movies WHERE media_id = ?", [media_id]
    ).fetchone()
    if result is None:
        return True
    return float(result[0]) < last_modified


def upsert_movie(con: duckdb.DuckDBPyConnection, metadata: MovieMetadata) -> None:
    """Delete and re-insert a movie and all its junction rows in one transaction.

    Args:
        con: An active DuckDB connection.
        metadata: The MovieMetadata to persist.
    """
    mid = metadata.media_id
    con.execute("DELETE FROM cast_members WHERE media_id = ?", [mid])
    con.execute("DELETE FROM directors WHERE media_id = ?", [mid])
    con.execute("DELETE FROM genres WHERE media_id = ?", [mid])
    con.execute("DELETE FROM movies WHERE media_id = ?", [mid])

    con.execute(
        """
        INSERT INTO movies
            (media_id, filepath, title, year, plot, runtime, mpaa, last_modified)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            mid,
            str(metadata.filepath),
            metadata.title,
            metadata.year,
            metadata.plot,
            metadata.runtime,
            metadata.mpaa,
            metadata.last_modified,
        ],
    )
    for genre in metadata.genres:
        con.execute(
            "INSERT INTO genres (media_id, genre) VALUES (?, ?)",
            [mid, genre.name],
        )
    for director in metadata.directors:
        con.execute(
            "INSERT INTO directors (media_id, director) VALUES (?, ?)",
            [mid, director.name],
        )
    for member in metadata.cast:
        con.execute(
            "INSERT INTO cast_members (media_id, actor_name, role) VALUES (?, ?, ?)",
            [mid, member.name, member.role],
        )


def materialize(directory: Path, db_path: Path, full_refresh: bool = False) -> int:
    """Orchestrate full materialization of .nfo files into DuckDB.

    Args:
        directory: Root directory containing .nfo files to process.
        db_path: Path to the DuckDB database file (created if absent).
        full_refresh: If True, drop all tables before re-processing.

    Returns:
        Number of movies upserted.
    """
    con = duckdb.connect(str(db_path))
    try:
        if full_refresh:
            drop_all(con)
        init_schema(con)

        count = 0
        for metadata in parse_directory(directory):
            if needs_update(con, metadata.media_id, metadata.last_modified):
                upsert_movie(con, metadata)
                count += 1
                logger.info("Upserted: %s (%s)", metadata.title, metadata.year)
            else:
                logger.debug("Skipping unchanged: %s", metadata.title)
        return count
    finally:
        con.close()
