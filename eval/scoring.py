from dataclasses import dataclass, field


@dataclass
class EvalResult:
    question: str
    expected_source: str
    retrieved_sources: list[str]
    top_distance: float | None
    answer: str
    expected_keywords: list[str]
    missing_keywords: list[str] = field(default_factory=list)

    @property
    def retrieval_hit(self) -> bool:
        return self.expected_source in self.retrieved_sources

    @property
    def keywords_found(self) -> bool:
        return len(self.missing_keywords) == 0

    @property
    def passed(self) -> bool:
        return self.retrieval_hit and self.keywords_found


def score(
    question: str,
    expected_source: str,
    expected_keywords: list[str],
    hits: list[dict],
    answer: str,
) -> EvalResult:
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
        missing_keywords=missing,
    )