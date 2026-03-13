import shutil
from pathlib import Path

import duckdb

from holocron.materializer.loader import materialize, needs_update, upsert_movie
from holocron.materializer.parser import scan_nfo_files
from holocron.materializer.schema import drop_all

FIXTURES = Path(__file__).parent / "fixtures"


def test_init_schema(mem_db):
    tables = {r[0] for r in mem_db.execute("SHOW TABLES").fetchall()}
    assert {"movies", "genres", "directors", "cast_members", "semantic_tags"} <= tables


def test_drop_all(mem_db):
    drop_all(mem_db)
    tables = {r[0] for r in mem_db.execute("SHOW TABLES").fetchall()}
    assert tables == set()


def test_upsert_movie(mem_db, sample_metadata):
    upsert_movie(mem_db, sample_metadata)
    row = mem_db.execute(
        "SELECT title, year FROM movies WHERE media_id = ?", [sample_metadata.media_id]
    ).fetchone()
    assert row == ("The Matrix", 1999)
    genres = mem_db.execute(
        "SELECT genre FROM genres WHERE media_id = ?", [sample_metadata.media_id]
    ).fetchall()
    assert len(genres) == 2


def test_upsert_idempotent(mem_db, sample_metadata):
    upsert_movie(mem_db, sample_metadata)
    upsert_movie(mem_db, sample_metadata)
    count = mem_db.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    assert count == 1


def test_needs_update_missing(mem_db, sample_metadata):
    assert needs_update(mem_db, sample_metadata.media_id, 999.0) is True


def test_needs_update_stale(mem_db, sample_metadata):
    upsert_movie(mem_db, sample_metadata)  # last_modified = 1000.0
    assert needs_update(mem_db, sample_metadata.media_id, 2000.0) is True


def test_needs_update_current(mem_db, sample_metadata):
    upsert_movie(mem_db, sample_metadata)  # last_modified = 1000.0
    assert needs_update(mem_db, sample_metadata.media_id, 500.0) is False


def test_scan_nfo_files(nfo_dir):
    found = list(scan_nfo_files(nfo_dir))
    assert len(found) >= 2
    assert all(f.suffix == ".nfo" for f in found)


def test_materialize_integration(tmp_path):
    dest = tmp_path / "media"
    dest.mkdir()
    shutil.copy(FIXTURES / "the_matrix.nfo", dest / "the_matrix.nfo")
    shutil.copy(FIXTURES / "inception.nfo", dest / "inception.nfo")

    db_path = tmp_path / "test.duckdb"
    count = materialize(dest, db_path)
    assert count == 2

    con = duckdb.connect(str(db_path))
    total = con.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    con.close()
    assert total == 2


def test_materialize_full_refresh(tmp_path):
    dest = tmp_path / "media"
    dest.mkdir()
    shutil.copy(FIXTURES / "the_matrix.nfo", dest / "the_matrix.nfo")

    db_path = tmp_path / "test.duckdb"
    materialize(dest, db_path)
    count = materialize(dest, db_path, full_refresh=True)
    assert count == 1
