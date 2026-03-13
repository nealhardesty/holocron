from holocron.extractor.writer import plex_to_metadata, process_directory
from tests.conftest import (
    MockDirector,
    MockGenre,
    MockPlexMovie,
    MockRole,
)


def test_plex_to_metadata_basic(tmp_path):
    filepath = tmp_path / "movie.mkv"
    filepath.touch()
    plex = MockPlexMovie(
        title="Blade Runner",
        year=1982,
        summary="A story about replicants.",
        contentRating="R",
        duration=6900000,  # 115 minutes
        genres=[MockGenre("Science Fiction"), MockGenre("Thriller")],
        directors=[MockDirector("Ridley Scott")],
        roles=[MockRole("Harrison Ford", "Deckard")],
    )
    meta = plex_to_metadata(plex, filepath)
    assert meta.title == "Blade Runner"
    assert meta.year == 1982
    assert meta.mpaa == "R"
    assert meta.runtime == 115
    assert len(meta.genres) == 2
    assert meta.directors[0].name == "Ridley Scott"
    assert meta.cast[0].name == "Harrison Ford"
    assert meta.cast[0].role == "Deckard"


def test_plex_to_metadata_missing_fields(tmp_path):
    filepath = tmp_path / "unknown.mkv"
    filepath.touch()
    plex = MockPlexMovie(duration=0, genres=[], directors=[], roles=[])
    meta = plex_to_metadata(plex, filepath)
    assert meta.runtime is None
    assert meta.genres == []


def test_process_directory_no_match(tmp_path, capsys):
    media_file = tmp_path / "movie.mkv"
    media_file.touch()
    result = process_directory(tmp_path, path_map={}, overwrite=False)
    assert result == 0
    assert not (tmp_path / "movie.nfo").exists()


def test_process_directory_writes_nfo(tmp_path):
    media_file = tmp_path / "movie.mkv"
    media_file.touch()
    plex = MockPlexMovie(title="Test", year=2020)
    path_map = {str(media_file.resolve()): plex}
    count = process_directory(tmp_path, path_map=path_map, overwrite=False)
    assert count == 1
    assert (tmp_path / "movie.nfo").exists()


def test_process_directory_no_overwrite(tmp_path):
    media_file = tmp_path / "movie.mkv"
    media_file.touch()
    nfo_file = tmp_path / "movie.nfo"
    nfo_file.write_text("<movie><title>Old</title></movie>")
    plex = MockPlexMovie(title="New")
    path_map = {str(media_file.resolve()): plex}
    count = process_directory(tmp_path, path_map=path_map, overwrite=False)
    assert count == 0
    assert "Old" in nfo_file.read_text()


def test_process_directory_with_overwrite(tmp_path):
    media_file = tmp_path / "movie.mkv"
    media_file.touch()
    nfo_file = tmp_path / "movie.nfo"
    nfo_file.write_text("<movie><title>Old</title></movie>")
    plex = MockPlexMovie(title="New Title")
    path_map = {str(media_file.resolve()): plex}
    count = process_directory(tmp_path, path_map=path_map, overwrite=True)
    assert count == 1
