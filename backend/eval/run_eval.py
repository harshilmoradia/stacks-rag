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
            hits=hits,
            answer=answer,
            expected_source=case.get("expected_source"),
            expected_keywords=case.get("expected_keywords"),
            expect_no_answer=case.get("expect_no_answer", False),
        )
        results.append(result)

    positive = [r for r in results if not r.expect_no_answer]
    negative = [r for r in results if r.expect_no_answer]

    pos_passed = sum(1 for r in positive if r.passed)
    neg_passed = sum(1 for r in negative if r.passed)
    total_passed = pos_passed + neg_passed

    print(f"\n{'=' * 60}")
    print(f"RETRIEVAL + GENERATION: {pos_passed}/{len(positive)} passed")
    print(f"REFUSAL ON OUT-OF-SCOPE: {neg_passed}/{len(negative)} passed")
    print(f"OVERALL: {total_passed}/{len(results)} passed")
    print(f"{'=' * 60}\n")

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.question}")
        if r.expect_no_answer:
            print(f"  Expected: refusal. Answer: {r.answer[:100]}")
        else:
            print(f"  Retrieved: {r.retrieved_sources}  (expected: {r.expected_source})")
            print(f"  Top distance: {r.top_distance}")
            if not r.retrieval_hit:
                print("  -> Retrieval miss")
            if r.missing_keywords:
                print(f"  -> Missing keywords: {r.missing_keywords}")
                print(f"  -> Full answer: {r.answer}")
        print()

    return 0 if total_passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(run())