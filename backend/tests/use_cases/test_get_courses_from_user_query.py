import pytest
from unittest.mock import MagicMock, patch
from billiken_blueprint.use_cases.get_courses_from_user_query import (
    get_courses_from_user_query,
)


@patch("billiken_blueprint.use_cases.get_courses_from_user_query.genai_client")
@patch(
    "billiken_blueprint.use_cases.get_courses_from_user_query.user_input_to_keywords"
)
def test_get_courses_filters_excluded(mock_keywords, mock_genai):
    # Setup Mocks
    mock_keywords.return_value = ["key", "words"]

    mock_embedding = MagicMock()
    mock_embedding.values = [0.1, 0.2, 0.3]
    mock_genai.models.embed_content.return_value.embeddings = [mock_embedding]

    mock_collection = MagicMock()

    # Simulate DB returning 10 entries with IDs 1 to 10
    ids = [f"doc_{i}" for i in range(1, 11)]
    metadatas = [{"course_id": i} for i in range(1, 11)]
    distances = [0.1] * 10
    documents = ["desc"] * 10

    mock_collection.query.return_value = {
        "ids": [ids],
        "metadatas": [metadatas],
        "distances": [distances],
        "documents": [documents],
    }

    # Exclude courses 1, 2, and 8
    excluded = [1, 2, 8]

    result = get_courses_from_user_query(
        "dummy query", mock_collection, excluded_course_ids=excluded
    )

    # Expected behavior:
    # 1 (excluded, skip)
    # 2 (excluded, skip)
    # 3 (keep) -> count 1
    # 4 (keep) -> count 2
    # 5 (keep) -> count 3
    # 6 (keep) -> count 4
    # 7 (keep) -> count 5
    # STOP

    filtered_ids = result["ids"][0]
    filtered_metas = result["metadatas"][0]

    # Check length
    assert len(filtered_ids) == 5

    # Check specific IDs (docs)
    assert filtered_ids == ["doc_3", "doc_4", "doc_5", "doc_6", "doc_7"]

    # Check course_ids in metadata
    result_course_ids = [m["course_id"] for m in filtered_metas]
    assert result_course_ids == [3, 4, 5, 6, 7]

    # Verify we didn't get 8

    # Verify query was called
    mock_collection.query.assert_called()


@patch("billiken_blueprint.use_cases.get_courses_from_user_query.genai_client")
@patch(
    "billiken_blueprint.use_cases.get_courses_from_user_query.user_input_to_keywords"
)
def test_get_courses_pagination(mock_keywords, mock_genai):
    # Setup Mocks
    mock_keywords.return_value = ["key", "words"]
    mock_genai.models.embed_content.return_value.embeddings = [MagicMock(values=[0.1])]

    mock_collection = MagicMock()

    # Scenario:
    # First call (n_results=20), returns mostly excluded items or just a few items.
    # Let's say we have to query twice? The code loops n_results by +20.
    # If query(n=20) returns enough valid, we stop.
    # But to test the loop, we need query(n=20) to NOT return enough, but query(n=40) to return enough?

    # However, mocking the collection to return different things based on n_results argument is tricky with standard Mock side_effect, unless we inspect kwargs.

    def side_effect(*args, **kwargs):
        n = kwargs.get("n_results", 20)
        # return n items.
        # Let's say IDs 1..n
        # Exclude IDs 1..18.
        # If n=20: 1..20. Valid: 19, 20. Count=2. (Need 5).
        # Loop continues. n=40.
        # Returns 1..40. Valid: 19, 20 .. 40. Count=22. (Take 5).

        ids = [f"doc_{i}" for i in range(1, n + 1)]
        metadatas = [{"course_id": i} for i in range(1, n + 1)]
        distances = [0.1] * n
        documents = ["desc"] * n

        return {
            "ids": [ids],
            "metadatas": [metadatas],
            "distances": [distances],
            "documents": [documents],
        }

    mock_collection.query.side_effect = side_effect

    excluded = list(range(1, 19))  # Exclude 1 to 18

    result = get_courses_from_user_query(
        "dummy", mock_collection, excluded_course_ids=excluded
    )

    filtered_metas = result["metadatas"][0]
    result_ids = [m["course_id"] for m in filtered_metas]

    # Expected: 19, 20, 21, 22, 23
    assert result_ids == [19, 20, 21, 22, 23]
    assert len(result_ids) == 5
