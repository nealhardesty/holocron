from __future__ import annotations

import logging
from pathlib import Path

import click

from holocron.materializer.loader import materialize

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@click.command()
@click.option(
    "--dir",
    "directory",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Directory to scan for .nfo files",
)
@click.option(
    "--db-path",
    default="./library.duckdb",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to DuckDB database file",
)
@click.option(
    "--full-refresh",
    is_flag=True,
    default=False,
    help="Drop all tables and re-process everything",
)
def main(directory: Path, db_path: Path, full_refresh: bool) -> None:
    """Parse .nfo files and compile them into a DuckDB database."""
    if full_refresh:
        click.echo("Full refresh mode: dropping all existing data.")
    click.echo(f"Scanning: {directory}")
    count = materialize(directory, db_path, full_refresh=full_refresh)
    click.echo(f"Done. Processed {count} NFO file(s) into {db_path}.")
