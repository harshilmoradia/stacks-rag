from eval.scoring import score

def test_positive_case_passes():
    hits = [{"source": "coffee_brewing_guide.md", "distance": 0.1, "text": "..."}]
    r = score(
        question="What water temp for pour-over?",
        hits=hits,
        answer="Use water between 195°F and 205°F.",
        expected_source="coffee_brewing_guide.md",
        expected_keywords=["195", "205"],
    )
    assert r.passed

def test_positive_case_fails_on_wrong_source():
    hits = [{"source": "apartment_budgeting.md", "distance": 0.3, "text": "..."}]
    r = score(
        question="What water temp for pour-over?",
        hits=hits,
        answer="195°F to 205°F.",
        expected_source="coffee_brewing_guide.md",
        expected_keywords=["195", "205"],
    )
    assert not r.passed

def test_negative_case_passes_on_refusal():
    hits = [{"source": "coffee_brewing_guide.md", "distance": 0.9, "text": "..."}]
    r = score(
        question="Best ski resort in Colorado?",
        hits=hits,
        answer="The context does not contain information about ski resorts.",
        expect_no_answer=True,
    )
    assert r.passed

def test_negative_case_fails_on_hallucination():
    hits = [{"source": "coffee_brewing_guide.md", "distance": 0.9, "text": "..."}]
    r = score(
        question="Best ski resort in Colorado?",
        hits=hits,
        answer="Vail is widely considered one of the best.",
        expect_no_answer=True,
    )
    assert not r.passed