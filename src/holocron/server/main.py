from __future__ import annotations

import logging
from pathlib import Path

import click
import duckdb
from mcp.server.fastmcp import FastMCP

from holocron.server.queries import (
    find_actor_crossovers,
    get_available_tags,
    get_library_overview,
    get_movie_details,
    search_library,
)

logger = logging.getLogger(__name__)
mcp = FastMCP("holocron")

# Module-level connection (set at startup via main())
_con: duckdb.DuckDBPyConnection | None = None


def _get_con() -> duckdb.DuckDBPyConnection:
    """Return the active DuckDB connection.

    Returns:
        The module-level DuckDB connection.

    Raises:
        RuntimeError: If the connection has not been initialized.
    """
    if _con is None:
        raise RuntimeError("DuckDB connection not initialized. Call main() first.")
    return _con


@mcp.resource("nfo://library_overview")
def library_overview() -> str:
    """Statistical summary of the entire movie library."""
    import json

    return json.dumps(get_library_overview(_get_con()), indent=2)


@mcp.resource("nfo://available_tags")
def available_tags() -> str:
    """All unique genre/taxonomy tags present in the library."""
    import json

    return json.dumps(get_available_tags(_get_con()), indent=2)


@mcp.tool()
def search_library_metadata(
    genres: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
) -> list[dict]:
    """Search the movie library by genre and/or year range."""
    return search_library(
        _get_con(), genres=genres, year_min=year_min, year_max=year_max
    )


@mcp.tool()
def get_movie_details_tool(title: str, year: int | None = None) -> dict | None:
    """Get the full profile for a specific movie including cast and directors."""
    return get_movie_details(_get_con(), title=title, year=year)


@mcp.tool()
def find_actor_crossovers_tool(actor_name: str) -> list[dict]:
    """Find all movies featuring a specific actor and their roles."""
    return find_actor_crossovers(_get_con(), actor_name=actor_name)


@click.command()
@click.option(
    "--db-path",
    default="./library.duckdb",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the DuckDB database file",
)
def main(db_path: Path) -> None:
    """Start the Holocron MCP context server."""
    global _con
    if not db_path.exists():
        raise click.ClickException(
            f"Database not found: {db_path}. Run holocron-materialize first."
        )
    _con = duckdb.connect(str(db_path), read_only=True)
    logger.info("Connected to %s (read-only)", db_path)
    mcp.run()
