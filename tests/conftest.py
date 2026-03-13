from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

import duckdb
import pytest

from holocron.materializer.schema import init_schema
from holocron.models import CastMember, Director, Genre, MovieMetadata

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@dataclass
class MockGenre:
    tag: str


@dataclass
class MockDirector:
    tag: str


@dataclass
class MockRole:
    tag: str
    role: str = ""


@dataclass
class MockPart:
    file: str


@dataclass
class MockMedia:
    parts: list[MockPart] = field(default_factory=list)


@dataclass
class MockPlexMovie:
    title: str = "Test Movie"
    year: int = 2000
    summary: str = "A test movie."
    contentRating: str = "PG"
    duration: int = 7200000  # 120 minutes in ms
    genres: list[MockGenre] = field(default_factory=list)
    directors: list[MockDirector] = field(default_factory=list)
    roles: list[MockRole] = field(default_factory=list)
    media: list[MockMedia] = field(default_factory=list)


@pytest.fixture
def sample_metadata(tmp_path: Path) -> MovieMetadata:
    """A sample MovieMetadata for The Matrix."""
    filepath = tmp_path / "The.Matrix.1999.mkv"
    filepath.touch()
    return MovieMetadata(
        media_id="abc123",
        filepath=filepath,
        title="The Matrix",
        year=1999,
        plot="A hacker discovers reality.",
        runtime=136,
        mpaa="R",
        genres=[Genre("Action"), Genre("Science Fiction")],
        directors=[Director("Lana Wachowski"), Director("Lilly Wachowski")],
        cast=[
            CastMember("Keanu Reeves", "Neo"),
            CastMember("Laurence Fishburne", "Morpheus"),
        ],
        last_modified=1000.0,
    )


@pytest.fixture
def mem_db() -> duckdb.DuckDBPyConnection:
    """An in-memory DuckDB connection with the schema initialized."""
    con = duckdb.connect(":memory:")
    init_schema(con)
    yield con
    con.close()


@pytest.fixture
def populated_db(mem_db, sample_metadata) -> duckdb.DuckDBPyConnection:
    """An in-memory DuckDB pre-populated with The Matrix."""
    from holocron.materializer.loader import upsert_movie

    upsert_movie(mem_db, sample_metadata)
    return mem_db


@pytest.fixture
def nfo_dir(tmp_path: Path) -> Path:
    """A temp directory containing copies of the test fixture NFO files."""
    dest = tmp_path / "media"
    dest.mkdir()
    for fixture in FIXTURES_DIR.glob("*.nfo"):
        shutil.copy(fixture, dest / fixture.name)
    return dest
