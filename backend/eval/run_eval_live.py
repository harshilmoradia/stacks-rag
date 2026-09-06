"""
Run the eval set against a LIVE deployed instance over HTTP, instead of
calling internal functions directly (see run_eval.py for that version).

This is the one that actually proves the deployed app works end-to-end —
it's the only eval path that exercises the real network request, CORS
config, rate limiter, and cold-start ingestion together.

Usage:
    python -m eval.run_eval_live https://your-app.onrender.com
"""
import json
import pathlib
import sys
import time

import httpx

from eval.scoring import score

EVAL_SET_PATH = pathlib.Path(__file__).parent / "eval_set.json"


def run(base_url: str) -> int:
    base_url = base_url.rstrip("/")
    eval_set = json.loads(EVAL_SET_PATH.read_text())
    results = []

    with httpx.Client(timeout=60.0) as client:
        for case in eval_set:
            resp = client.post(f"{base_url}/ask", json={"question": case["question"]})

            if resp.status_code == 429:
                print(f"[SKIP] Rate limited on: {case['question']}")
                print("  -> Hit the 20/day per-IP limit. Wait, or run fewer cases at a time.")
                continue

            resp.raise_for_status()
            data = resp.json()

            result = score(
                question=case["question"],
                hits=data["sources"],
                answer=data["answer"],
                expected_source=case.get("expected_source"),
                expected_keywords=case.get("expected_keywords"),
                expect_no_answer=case.get("expect_no_answer", False),
            )
            results.append(result)
            time.sleep(0.5)  # be polite to a free-tier instance, not a stress test

    if not results:
        print("No results — check the URL and rate limit status.")
        return 1

    positive = [r for r in results if not r.expect_no_answer]
    negative = [r for r in results if r.expect_no_answer]

    pos_passed = sum(1 for r in positive if r.passed)
    neg_passed = sum(1 for r in negative if r.passed)
    total_passed = pos_passed + neg_passed

    print(f"\n{'=' * 60}")
    print(f"LIVE URL: {base_url}")
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
    if len(sys.argv) != 2:
        print("Usage: python -m eval.run_eval_live <base_url>")
        sys.exit(1)
    sys.exit(run(sys.argv[1]))