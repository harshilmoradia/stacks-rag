from eval.scoring import score


def test_passing_result_when_source_and_keywords_match():
    result = score(
        question="What is the best time to go?",
        expected_source="notes.md",
        expected_keywords=["spring", "fall"],
        hits=[{"source": "notes.md", "distance": 0.2}],
        answer="Late spring and early fall offer the clearest skies.",
    )
    assert result.retrieval_hit is True
    assert result.keywords_found is True
    assert result.passed is True


def test_fails_when_expected_source_not_retrieved():
    result = score(
        question="q",
        expected_source="notes.md",
        expected_keywords=["spring"],
        hits=[{"source": "other_file.md", "distance": 0.5}],
        answer="Spring is a good time.",
    )
    assert result.retrieval_hit is False
    assert result.passed is False


def test_fails_when_keyword_missing_from_answer():
    result = score(
        question="q",
        expected_source="notes.md",
        expected_keywords=["spring", "fall"],
        hits=[{"source": "notes.md", "distance": 0.2}],
        answer="Summer works well for most travelers.",
    )
    assert result.retrieval_hit is True
    assert result.keywords_found is False
    assert "spring" in result.missing_keywords
    assert "fall" in result.missing_keywords
    assert result.passed is False


def test_keyword_match_is_case_insensitive_substring():
    result = score(
        question="q",
        expected_source="notes.md",
        expected_keywords=["FOG"],
        hits=[{"source": "notes.md", "distance": 0.1}],
        answer="Morning fog is common along the coast.",
    )
    assert result.keywords_found is True


def test_empty_hits_gives_none_distance_and_fails_retrieval():
    result = score(
        question="q",
        expected_source="notes.md",
        expected_keywords=[],
        hits=[],
        answer="I don't have any indexed documents to answer from yet.",
    )
    assert result.top_distance is None
    assert result.retrieval_hit is False
    assert result.passed is False