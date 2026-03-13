# Holocron: Local Media Intelligence System

A four-component Python pipeline that decouples metadata from a Plex Media Server, caches it locally as `.nfo` XML files, compiles it into a DuckDB database, and exposes it to LLMs via a Model Context Protocol (MCP) server.

## Architecture

```
Plex Media Server
      │
      ▼
[A] holocron-extract   →  .nfo XML sidecar files (per media file)
                                    │
                                    ▼
                        [B] holocron-materialize  →  library.duckdb
                                                          │
                                                          ▼
                                              [C] holocron-serve  →  MCP Client (Claude, etc.)
```

## Components

| Component | CLI | Description |
|-----------|-----|-------------|
| A: Extractor | `holocron-extract` | Reads Plex API, writes `.nfo` XML sidecars |
| B: Materializer | `holocron-materialize` | Parses `.nfo` files into DuckDB |
| C: MCP Server | `holocron-serve` | Exposes DuckDB to LLMs via MCP |
| D: Augmentor | *(future)* | LLM-generated semantic tags injected back into `.nfo` files |

## Quick Start

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) — Python package manager

### Installation
```bash
make venv
make install
```

### Usage

#### Component A — Extract metadata from Plex
```bash
holocron-extract \
  --dir /path/to/movies \
  --plex-url http://localhost:32400 \
  --plex-token YOUR_PLEX_TOKEN
```

Or using environment variable:
```bash
export PLEX_TOKEN=your_token
holocron-extract --dir /path/to/movies
```

#### Component B — Compile NFO files into DuckDB
```bash
holocron-materialize --dir /path/to/movies --db-path library.duckdb
# Force full re-process:
holocron-materialize --dir /path/to/movies --db-path library.duckdb --full-refresh
```

#### Component C — Start the MCP Context Server
```bash
holocron-serve --db-path library.duckdb
```

Then configure your MCP client (e.g., Claude Desktop) to connect to `holocron-serve`.

## MCP Interface

### Resources
- `nfo://library_overview` — JSON summary: total movies, top genres, year range, avg runtime
- `nfo://available_tags` — List of all unique genre tags

### Tools
- `search_library_metadata(genres, year_min, year_max)` — filter movies by genre/year
- `get_movie_details_tool(title, year)` — full profile with cast, directors, plot
- `find_actor_crossovers_tool(actor_name)` — all movies for a given actor

## Development

```bash
make test      # run pytest
make lint      # ruff check
make format    # ruff format
make clean     # remove artifacts
```

## Project Structure

```
src/holocron/
├── models.py          # shared dataclasses
├── nfo.py             # NFO XML read/write
├── constants.py       # shared constants
├── extractor/         # Component A
├── materializer/      # Component B
├── server/            # Component C
└── augmentor/         # Component D (stub)
tests/
└── fixtures/          # sample .nfo files for testing
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
