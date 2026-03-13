from holocron.server.queries import (
    find_actor_crossovers,
    get_available_tags,
    get_library_overview,
    get_movie_details,
    search_library,
)


def test_library_overview(populated_db):
    overview = get_library_overview(populated_db)
    assert overview["total_movies"] == 1
    assert overview["year_min"] == 1999
    assert overview["year_max"] == 1999
    assert len(overview["top_genres"]) >= 1


def test_available_tags(populated_db):
    tags = get_available_tags(populated_db)
    assert "Action" in tags
    assert "Science Fiction" in tags


def test_search_library_no_filter(populated_db):
    results = search_library(populated_db)
    assert len(results) == 1
    assert results[0]["title"] == "The Matrix"


def test_search_library_genre_match(populated_db):
    results = search_library(populated_db, genres=["Action"])
    assert len(results) == 1


def test_search_library_genre_no_match(populated_db):
    results = search_library(populated_db, genres=["Horror"])
    assert len(results) == 0


def test_search_library_year_filter(populated_db):
    assert len(search_library(populated_db, year_min=2000)) == 0
    assert len(search_library(populated_db, year_max=2000)) == 1


def test_get_movie_details(populated_db):
    details = get_movie_details(populated_db, "The Matrix")
    assert details is not None
    assert details["year"] == 1999
    assert "Action" in details["genres"]
    assert any(c["name"] == "Keanu Reeves" for c in details["cast"])


def test_get_movie_details_not_found(populated_db):
    assert get_movie_details(populated_db, "Nonexistent Film") is None


def test_find_actor_crossovers(populated_db):
    results = find_actor_crossovers(populated_db, "Keanu Reeves")
    assert len(results) == 1
    assert results[0]["role"] == "Neo"


def test_find_actor_crossovers_case_insensitive(populated_db):
    results = find_actor_crossovers(populated_db, "keanu reeves")
    assert len(results) == 1


def test_find_actor_crossovers_not_found(populated_db):
    assert find_actor_crossovers(populated_db, "Nobody Special") == []
