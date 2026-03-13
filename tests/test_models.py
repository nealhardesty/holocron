from holocron.models import CastMember, Genre, MovieMetadata


def test_cast_member():
    m = CastMember(name="Keanu Reeves", role="Neo")
    assert m.name == "Keanu Reeves"
    assert m.role == "Neo"


def test_genre():
    g = Genre(name="Action")
    assert g.name == "Action"


def test_movie_metadata_defaults(tmp_path):
    filepath = tmp_path / "movie.mkv"
    filepath.touch()
    m = MovieMetadata(media_id="abc", filepath=filepath, title="Test")
    assert m.year is None
    assert m.plot == ""
    assert m.runtime is None
    assert m.mpaa == ""
    assert m.genres == []
    assert m.directors == []
    assert m.cast == []
    assert m.last_modified == 0.0
