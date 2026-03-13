from pathlib import Path

from holocron.nfo import parse_nfo, write_nfo

FIXTURES = Path(__file__).parent / "fixtures"


def test_round_trip(tmp_path, sample_metadata):
    out = tmp_path / "test.nfo"
    write_nfo(sample_metadata, out)
    parsed = parse_nfo(out)
    assert parsed.title == "The Matrix"
    assert parsed.year == 1999
    assert parsed.runtime == 136
    assert parsed.mpaa == "R"
    assert len(parsed.genres) == 2
    assert len(parsed.directors) == 2
    assert len(parsed.cast) == 2


def test_parse_matrix_fixture():
    nfo = FIXTURES / "the_matrix.nfo"
    m = parse_nfo(nfo)
    assert m.title == "The Matrix"
    assert m.year == 1999
    assert m.runtime == 136
    assert m.mpaa == "R"
    assert any(g.name == "Science Fiction" for g in m.genres)
    assert any(d.name == "Lana Wachowski" for d in m.directors)
    assert any(c.name == "Keanu Reeves" and c.role == "Neo" for c in m.cast)


def test_parse_minimal_fixture():
    nfo = FIXTURES / "minimal.nfo"
    m = parse_nfo(nfo)
    assert m.title == "Untitled Film"
    assert m.year is None
    assert m.runtime is None
    assert m.genres == []
    assert m.cast == []


def test_xml_escaping(tmp_path, sample_metadata):
    sample_metadata.plot = "A & B < C > D"
    out = tmp_path / "escape.nfo"
    write_nfo(sample_metadata, out)
    parsed = parse_nfo(out)
    assert parsed.plot == "A & B < C > D"
