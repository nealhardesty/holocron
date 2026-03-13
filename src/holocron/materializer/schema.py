from __future__ import annotations

import duckdb

MOVIES_DDL = """
CREATE TABLE IF NOT EXISTS movies (
    media_id    VARCHAR PRIMARY KEY,
    filepath    VARCHAR NOT NULL,
    title       VARCHAR NOT NULL,
    year        INTEGER,
    plot        VARCHAR,
    runtime     INTEGER,
    mpaa        VARCHAR,
    last_modified DOUBLE NOT NULL
)
"""

GENRES_DDL = """
CREATE TABLE IF NOT EXISTS genres (
    media_id    VARCHAR NOT NULL,
    genre       VARCHAR NOT NULL,
    PRIMARY KEY (media_id, genre)
)
"""

DIRECTORS_DDL = """
CREATE TABLE IF NOT EXISTS directors (
    media_id    VARCHAR NOT NULL,
    director    VARCHAR NOT NULL,
    PRIMARY KEY (media_id, director)
)
"""

CAST_DDL = """
CREATE TABLE IF NOT EXISTS cast_members (
    media_id    VARCHAR NOT NULL,
    actor_name  VARCHAR NOT NULL,
    role        VARCHAR,
    PRIMARY KEY (media_id, actor_name, role)
)
"""

SEMANTIC_TAGS_DDL = """
CREATE TABLE IF NOT EXISTS semantic_tags (
    media_id    VARCHAR NOT NULL,
    tag_type    VARCHAR NOT NULL,
    tag_value   VARCHAR NOT NULL,
    PRIMARY KEY (media_id, tag_type, tag_value)
)
"""

ALL_DDL = [MOVIES_DDL, GENRES_DDL, DIRECTORS_DDL, CAST_DDL, SEMANTIC_TAGS_DDL]
ALL_TABLES = ["movies", "genres", "directors", "cast_members", "semantic_tags"]


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    """Create all tables if they do not exist.

    Args:
        con: An active DuckDB connection.
    """
    for ddl in ALL_DDL:
        con.execute(ddl)


def drop_all(con: duckdb.DuckDBPyConnection) -> None:
    """Drop all tables for a full refresh.

    Args:
        con: An active DuckDB connection.
    """
    for table in ALL_TABLES:
        con.execute(f"DROP TABLE IF EXISTS {table}")
