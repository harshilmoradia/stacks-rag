import json
import pathlib
import sys

from app import embeddings, llm, vectorstore
from app.config import settings
from eval.scoring import score

EVAL_SET_PATH = pathlib.Path(__file__).parent / "eval_set.json"


def run() -> int:
    eval_set = json.loads(EVAL_SET_PATH.read_text())
    results = []

    for case in eval_set:
        query_vector = embeddings.embed_query(case["question"])
        hits = vectorstore.query(query_vector, top_k=settings.top_k)
        answer = llm.generate_answer(case["question"], hits)

        result = score(
            question=case["question"],
            expected_source=case["expected_source"],
            expected_keywords=case["expected_keywords"],
            hits=hits,
            answer=answer,
        )
        results.append(result)

    passed = sum(1 for r in results if r.passed)
    print(f"\n{'=' * 60}")
    print(f"EVAL RESULTS: {passed}/{len(results)} passed")
    print(f"{'=' * 60}\n")

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.question}")
        print(f"  Retrieved sources: {r.retrieved_sources}  (expected: {r.expected_source})")
        print(f"  Top distance: {r.top_distance}")
        if not r.retrieval_hit:
            print("  -> Retrieval miss: expected source was not in the top results")
        if r.missing_keywords:
            print(f"  -> Missing expected keywords in answer: {r.missing_keywords}")
        print()

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(run())