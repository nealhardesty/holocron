from __future__ import annotations

import logging
import os
from pathlib import Path

import click

from holocron.extractor.plex_client import build_path_map, connect_plex
from holocron.extractor.writer import process_directory

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@click.command()
@click.option(
    "--dir",
    "directory",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Media directory to scan",
)
@click.option(
    "--plex-url",
    default="http://localhost:32400",
    show_default=True,
    help="Plex server URL",
)
@click.option(
    "--plex-token",
    default=lambda: os.environ.get("PLEX_TOKEN", ""),
    required=True,
    help="Plex auth token (or set PLEX_TOKEN env var)",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing .nfo files",
)
def main(directory: Path, plex_url: str, plex_token: str, overwrite: bool) -> None:
    """Extract Plex metadata and write Jellyfin-compatible .nfo sidecar files."""
    click.echo(f"Connecting to Plex at {plex_url} ...")
    server = connect_plex(plex_url, plex_token)
    click.echo("Building file path map ...")
    path_map = build_path_map(server)
    click.echo(f"Processing directory: {directory}")
    count = process_directory(directory, path_map, overwrite=overwrite)
    click.echo(f"Done. Wrote {count} NFO file(s).")
