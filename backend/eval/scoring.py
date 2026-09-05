from dataclasses import dataclass, field

REFUSAL_PHRASES = [
    "don't have",
    "doesn't contain",
    "does not contain",
    "cannot find",
    "can't find",
    "no information",
    "not covered",
    "don't know",
    "unable to answer",
    "context does not",
]


@dataclass
class EvalResult:
    question: str
    expected_source: str | None
    retrieved_sources: list[str]
    top_distance: float | None
    answer: str
    expected_keywords: list[str]
    expect_no_answer: bool = False
    missing_keywords: list[str] = field(default_factory=list)

    @property
    def retrieval_hit(self) -> bool:
        if self.expect_no_answer:
            return True  # not applicable; passed is judged on refusal instead
        return self.expected_source in self.retrieved_sources

    @property
    def keywords_found(self) -> bool:
        return len(self.missing_keywords) == 0

    @property
    def refused(self) -> bool:
        answer_lower = self.answer.lower()
        return any(phrase in answer_lower for phrase in REFUSAL_PHRASES)

    @property
    def passed(self) -> bool:
        if self.expect_no_answer:
            return self.refused
        return self.retrieval_hit and self.keywords_found


def score(
    question: str,
    hits: list[dict],
    answer: str,
    expected_source: str | None = None,
    expected_keywords: list[str] | None = None,
    expect_no_answer: bool = False,
) -> EvalResult:
    expected_keywords = expected_keywords or []
    retrieved_sources = [h["source"] for h in hits]
    top_distance = hits[0]["distance"] if hits else None

    answer_lower = answer.lower()
    missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]

    return EvalResult(
        question=question,
        expected_source=expected_source,
        retrieved_sources=retrieved_sources,
        top_distance=top_distance,
        answer=answer,
        expected_keywords=expected_keywords,
        expect_no_answer=expect_no_answer,
        missing_keywords=missing,
    )