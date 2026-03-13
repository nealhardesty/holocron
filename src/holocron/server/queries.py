from __future__ import annotations

import duckdb


def get_library_overview(con: duckdb.DuckDBPyConnection) -> dict:
    """Return a statistical summary of the movie library.

    Args:
        con: An active DuckDB connection.

    Returns:
        A dict with total_movies, year range, avg_runtime_minutes, and top_genres.
    """
    total = con.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    year_range = con.execute(
        "SELECT MIN(year), MAX(year) FROM movies WHERE year IS NOT NULL"
    ).fetchone()
    avg_runtime = con.execute(
        "SELECT ROUND(AVG(runtime)) FROM movies WHERE runtime IS NOT NULL"
    ).fetchone()[0]
    genre_counts = con.execute(
        """
        SELECT genre, COUNT(*) AS cnt
        FROM genres
        GROUP BY genre
        ORDER BY cnt DESC
        LIMIT 10
        """
    ).fetchall()
    return {
        "total_movies": total,
        "year_min": year_range[0] if year_range else None,
        "year_max": year_range[1] if year_range else None,
        "avg_runtime_minutes": avg_runtime,
        "top_genres": [{"genre": g, "count": c} for g, c in genre_counts],
    }


def get_available_tags(con: duckdb.DuckDBPyConnection) -> list[str]:
    """Return a sorted list of all unique genre tags in the library.

    Args:
        con: An active DuckDB connection.

    Returns:
        Sorted list of genre name strings.
    """
    rows = con.execute("SELECT DISTINCT genre FROM genres ORDER BY genre").fetchall()
    return [row[0] for row in rows]


def search_library(
    con: duckdb.DuckDBPyConnection,
    genres: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
) -> list[dict]:
    """Search movies by optional genre list and/or year range.

    Args:
        con: An active DuckDB connection.
        genres: Optional list of genre names to filter by (OR logic).
        year_min: Optional minimum release year (inclusive).
        year_max: Optional maximum release year (inclusive).

    Returns:
        List of dicts with title, year, and genres for matching movies.
    """
    conditions = []
    params: list = []

    if year_min is not None:
        conditions.append("m.year >= ?")
        params.append(year_min)
    if year_max is not None:
        conditions.append("m.year <= ?")
        params.append(year_max)

    if genres:
        placeholders = ", ".join("?" * len(genres))
        conditions.append(
            "m.media_id IN "
            f"(SELECT media_id FROM genres WHERE genre IN ({placeholders}))"
        )
        params.extend(genres)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT m.title, m.year,
               STRING_AGG(g.genre, ', ' ORDER BY g.genre) AS genres
        FROM movies m
        LEFT JOIN genres g ON m.media_id = g.media_id
        {where_clause}
        GROUP BY m.title, m.year
        ORDER BY m.title
    """
    rows = con.execute(sql, params).fetchall()
    return [{"title": r[0], "year": r[1], "genres": r[2] or ""} for r in rows]


def get_movie_details(
    con: duckdb.DuckDBPyConnection, title: str, year: int | None = None
) -> dict | None:
    """Return full profile for a movie, including cast and directors.

    Args:
        con: An active DuckDB connection.
        title: Movie title to look up (case-insensitive).
        year: Optional release year to disambiguate titles.

    Returns:
        A dict with full movie details, or None if not found.
    """
    params: list = [title]
    year_clause = ""
    if year is not None:
        year_clause = "AND m.year = ?"
        params.append(year)

    row = con.execute(
        f"""
        SELECT m.media_id, m.title, m.year, m.plot, m.runtime, m.mpaa
        FROM movies m
        WHERE LOWER(m.title) = LOWER(?) {year_clause}
        LIMIT 1
        """,
        params,
    ).fetchone()
    if row is None:
        return None

    media_id, title, year_val, plot, runtime, mpaa = row

    directors = [
        r[0]
        for r in con.execute(
            "SELECT director FROM directors WHERE media_id = ? ORDER BY director",
            [media_id],
        ).fetchall()
    ]
    genres = [
        r[0]
        for r in con.execute(
            "SELECT genre FROM genres WHERE media_id = ? ORDER BY genre",
            [media_id],
        ).fetchall()
    ]
    cast = [
        {"name": r[0], "role": r[1]}
        for r in con.execute(
            "SELECT actor_name, role FROM cast_members"
            " WHERE media_id = ? ORDER BY actor_name",
            [media_id],
        ).fetchall()
    ]

    return {
        "title": title,
        "year": year_val,
        "plot": plot,
        "runtime": runtime,
        "mpaa": mpaa,
        "genres": genres,
        "directors": directors,
        "cast": cast,
    }


def find_actor_crossovers(
    con: duckdb.DuckDBPyConnection, actor_name: str
) -> list[dict]:
    """Return all movies featuring an actor, with their role in each.

    Args:
        con: An active DuckDB connection.
        actor_name: Actor name to search for (case-insensitive).

    Returns:
        List of dicts with title, year, and role for each appearance.
    """
    rows = con.execute(
        """
        SELECT m.title, m.year, c.role
        FROM cast_members c
        JOIN movies m ON c.media_id = m.media_id
        WHERE LOWER(c.actor_name) = LOWER(?)
        ORDER BY m.year, m.title
        """,
        [actor_name],
    ).fetchall()
    return [{"title": r[0], "year": r[1], "role": r[2]} for r in rows]
