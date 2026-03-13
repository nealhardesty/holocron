# Changelog

## [0.1.0] - 2026-03-12

### Added
- Initial project scaffold: `pyproject.toml`, `Makefile`, `.gitignore`, `.python-version`
- Component A: Plex-to-NFO Extractor (`holocron-extract` CLI)
  - Connects to Plex Media Server and builds filepath → metadata map
  - Writes Jellyfin/Kodi-compatible `.nfo` XML sidecar files
  - Supports `--overwrite` flag and graceful skip of unmatched files
- Component B: NFO Materializer (`holocron-materialize` CLI)
  - Parses `.nfo` files recursively into a persistent DuckDB database
  - Incremental upserts via filesystem timestamps
  - `--full-refresh` flag for complete re-processing
- Component C: MCP Context Server (`holocron-serve` CLI)
  - FastMCP server exposing library resources and query tools to LLMs
  - Resources: `nfo://library_overview`, `nfo://available_tags`
  - Tools: `search_library_metadata`, `get_movie_details_tool`, `find_actor_crossovers_tool`
- Component D stub: `augmentor/stub.py` with `NotImplementedError` and full docstring
- Shared core: `models.py` (dataclasses), `nfo.py` (XML read/write), `constants.py`
- Test suite with fixtures, unit tests, and integration tests for all components
