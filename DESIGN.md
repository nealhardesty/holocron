Here is the consolidated Master PRD. It is structured like a proper data engineering pipeline—moving from raw extraction, to batch materialization, to low-latency serving, and finally, semantic enrichment.

---

# Master PRD: Local Media Intelligence System

## 1. Executive Summary

The Local Media Intelligence System is a four-part software suite designed to decouple metadata from a Plex Media Server, cache it locally as standardized `.nfo` XML files, compile it into a persistent relational database, and expose that highly structured dataset to Large Language Models via a Model Context Protocol (MCP) server.

By separating the extraction and materialization phases from the serving layer, the system bypasses API rate limits, eliminates cold-start latency, and creates a robust, offline context engine for AI-driven media curation.

---

## 2. System Architecture Overview

The system relies on a strict separation of concerns across four distinct Python components:

1. **Component A: The Extractor (CLI).** Ingests base metadata from Plex and writes Jellyfin-compatible `.nfo` sidecar files to the local filesystem.
2. **Component B: The Materializer (Batch/Cron).** Parses the local `.nfo` files and compiles them into a persistent DuckDB database file.
3. **Component C: The Context Server (MCP).** Connects to the compiled DuckDB file in read-only mode, instantly exposing tools and library context to an LLM client.
4. **Component D: The Augmentation Engine (Future CLI).** Utilizes an LLM API to generate deep semantic metadata (tropes, themes) and injects it back into the base `.nfo` files.

---

## 3. Component A: Plex-to-NFO Extractor (The Ingestion Layer)

### 3.1 Objectives

* Connect securely to a Plex API endpoint.
* Build an in-memory dictionary mapping Plex `ratingKey` IDs to physical file paths to avoid $O(N)$ API queries.
* Recursively scan a target directory for media files (e.g., `.mkv`, `.mp4`).
* Generate Kodi/Jellyfin-compliant `.nfo` files.

### 3.2 CLI Inputs

* `--dir`: Absolute path to the media directory (e.g., `/mnt/media/Movies`).
* `--plex-url`: Local/Remote URL (e.g., `http://localhost:32400`).
* `--plex-token`: Plex authentication token.
* `--overwrite`: (Optional boolean) Force overwrite of existing `.nfo` files.

### 3.3 Target Output Schema (Jellyfin XML Standard)

| Plex Attribute | NFO XML Tag | Example |
| --- | --- | --- |
| `title` | `<title>` | `<title>The Matrix</title>` |
| `year` | `<year>` | `<year>1999</year>` |
| `summary` | `<plot>` | `<plot>A computer hacker learns...</plot>` |
| `contentRating` | `<mpaa>` | `<mpaa>R</mpaa>` |
| `duration` | `<runtime>` | `<runtime>136</runtime>` (in minutes) |
| `genres` | `<genre>` | `<genre>Science Fiction</genre>` |
| `directors` | `<director>` | `<director>Lana Wachowski</director>` |
| `roles` | `<actor>` | `<actor><name>Keanu Reeves</name><role>Neo</role></actor>` |

---

## 4. Component B: NFO Indexer (The Materialization Layer)

### 4.1 Objectives

* Act as the ETL bridge between the flat XML files and the SQL-driven MCP server.
* Parse `.nfo` files recursively and load the structured data into a persistent DuckDB database (`library.duckdb`).
* Support incremental upserts so scheduled cron runs only process modified or net-new `.nfo` files based on filesystem timestamps.

### 4.2 CLI Inputs

* `--dir`: Target media directory to scan for `.nfo` files.
* `--db-path`: Local path to save/update `library.duckdb`.
* `--full-refresh`: (Optional boolean) Drops all existing tables and forces a complete re-parse.

### 4.3 Database Schema (DuckDB)

* **`movies`:** Core 1:1 metadata (`media_id` [PK], `filepath`, `title`, `year`, `plot`, `runtime`, `mpaa`, `last_modified`).
* **`genres` (Junction):** Maps `media_id` to `<genre>` tags.
* **`directors` (Junction):** Maps `media_id` to `<director>` tags.
* **`cast` (Junction):** Maps `media_id` to `<actor>` names and their `<role>`.
* **`semantic_tags` (Future):** Dedicated table for LLM-generated tropes and themes.

---

## 5. Component C: Local Context Server (The Serving Layer)

### 5.1 Objectives

* Provide a low-latency, read-only interface for LLMs using the `mcp.server.fastmcp` SDK.
* Connect directly to `library.duckdb` on startup (`read_only=True`) to eliminate parsing overhead and allow concurrent writes from Component B's background cron jobs.

### 5.2 MCP Resources (Read-Only State)

* **`nfo://library_overview`**: Returns a JSON statistical summary of the database (total movies, counts by genre, oldest/newest).
* **`nfo://available_tags`**: Returns a unique list of all custom taxonomic tags (genres, tropes, themes) present in the DB to guide the LLM's search vocabulary.

### 5.3 MCP Tools (Active Execution)

| Tool Name | Parameters | Description |
| --- | --- | --- |
| `search_library_metadata` | `genres` (list), `year_min` (int), `year_max` (int) | Executes a SQL query against the `movies` and `genres` tables. Returns a lightweight list of matching titles and years. |
| `get_movie_details` | `title` (str), `year` (int) | Pulls the complete profile for a specific movie, executing a join across the `movies`, `cast`, and `directors` tables. |
| `find_actor_crossovers` | `actor_name` (str) | Queries the `cast` junction table to return all movies featuring a specific person and their exact roles. |

---

## 6. Component D: LLM Metadata Augmentation (Future Phase)

### 6.1 Objectives

A standalone batch script that reads base `.nfo` files, queries an LLM API (e.g., Claude, Gemini, OpenAI), and appends deep semantic intelligence back into the XML structure for the Materializer to pick up on its next run.

### 6.2 Target Augmentation Tags

| Target Tag | Description | Example Output |
| --- | --- | --- |
| `<theme>` | Deep thematic vectors. | `<theme>Man vs. Machine</theme>` |
| `<trope>` | Storytelling devices. | `<trope>The Chosen One</trope>` |
| `<vibe>` | Emotional resonance. | `<vibe>Gritty, mind-bending cyberpunk action.</vibe>` |
| `<summary_spoilers>` | Full narrative arc. | `<summary_spoilers>...Neo sacrifices himself...</summary_spoilers>` |

---

## 7. Edge Cases & Constraints

* **Plex Path Matching:** Not all filesystem files may exist in Plex. The Extractor must log warnings and gracefully skip unmatched files.
* **Multiple File Versions:** If 1080p and 4K versions exist in the same directory, the Extractor must duplicate the metadata into unique `.nfo` files matching each specific filename.
* **XML Sanitization:** All text strings (especially `<plot>`) must be safely escaped (e.g., `&`, `<`, `>`) during Component A and D to prevent parsing failures in Component B.
* **Concurrency:** DuckDB's `read_only=True` connection in the MCP server ensures that background cron jobs updating the database do not cause file locks or crashes.

---

Would you like me to draft the standard Python project structure (requirements, folder hierarchy) so you can initialize the repository, or would you rather dive straight into writing the code for Component A?
