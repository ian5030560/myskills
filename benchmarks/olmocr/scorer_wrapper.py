"""Run the official olmOCR-Bench scorer with two additions. Executed by the scorer venv's Python.

1. Windows path fix. The scorer keys candidate PDFs by ``os.path.relpath`` (backslashes on
   Windows) but looks tests up by the jsonl ``pdf`` field (forward slashes), so every test
   reports missing output and scores 0%. Here the test paths are converted to ``os.sep`` at
   load time. Nothing in the installed package or the jsonl files is edited, and on other
   platforms the conversion is a no-op.
2. Per-test results. ``--results-out <file>`` writes ``{test id: passed}`` as JSON, so the
   caller can compare runs test by test.

All other arguments go to the official CLI unchanged.
"""

import json
import os
import sys

from olmocr.bench import benchmark

RESULTS_FLAG = "--results-out"


def _pop_results_path() -> str:
    if RESULTS_FLAG not in sys.argv:
        return ""
    index = sys.argv.index(RESULTS_FLAG)
    path = sys.argv[index + 1]
    del sys.argv[index:index + 2]
    return path


def _patch(results_path: str) -> dict:
    results = {}
    original_load = benchmark.load_tests
    original_evaluate = benchmark.evaluate_candidate

    def load_tests(path):
        tests = original_load(path)
        for test in tests:
            test.pdf = test.pdf.replace("/", os.sep)
        return tests

    def evaluate_candidate(*args, **kwargs):
        outcome = original_evaluate(*args, **kwargs)
        for pages in outcome[-1].values():   # test_results: pdf -> page -> [(test, passed, why)]
            for entries in pages.values():
                for test, passed, _ in entries:
                    results[test.id] = bool(passed)
        if results_path:
            with open(results_path, "w", encoding="utf-8") as out:
                json.dump(results, out)
        return outcome

    benchmark.load_tests = load_tests
    benchmark.evaluate_candidate = evaluate_candidate
    return results


if __name__ == "__main__":
    _patch(_pop_results_path())
    benchmark.main()
