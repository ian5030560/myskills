#!/usr/bin/env python3
"""Score write-paper-notes' extract_text.py on olmOCR-Bench and compare with the baseline.

Steps: extract every bench PDF with the current extract_text.py, leave out PDFs it reports as
having no text layer (the skill does no OCR), score the rest with the official scorer in its
own venv, then print per-category pass rates and the difference from ``baseline.json``.
Run ``setup_venv.py`` and ``fetch.py`` first. The exit status never depends on the score;
``--update-baseline`` is the only way the baseline changes.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from bench_common import (BASELINE, BENCH_DIR, CATEGORIES, EXTRACT_SCRIPT, HERE, KNOWN_BAD,
                          REPO, SCORER_VERSION, WORK, die, read_jsonl, venv_python)

CANDIDATE = "extract_text"
_NO_TEXT_RE = re.compile(r"^no text layer: (.*)$", re.M)


def _extract(pdf: str, out_dir) -> bool:
    """Run extract_text.py on one bench PDF; return True when it has a text layer."""
    result = subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT), "--input", str(BENCH_DIR / "pdfs" / pdf),
         "--output-dir", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8", check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode != 0:
        die(f"extract_text.py failed on {pdf}:\n{result.stderr.strip()}")
    match = _NO_TEXT_RE.search(result.stdout)
    return bool(match) and match.group(1).strip() == "none"


def _extract_all(pdfs: list, workers: int) -> dict:
    """Return {pdf: has_text_layer} for every bench PDF, extracting in parallel."""
    out_dir = WORK / "extract"
    shutil.rmtree(out_dir, ignore_errors=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pdf: pool.submit(_extract, pdf, out_dir / pdf.split("/")[0]) for pdf in pdfs}
        return {pdf: future.result() for pdf, future in futures.items()}


def _link_or_copy(src, dest) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy2(src, dest)


def _build_scored_dir(tests: dict, has_text: dict) -> dict:
    """Lay out the folder the scorer reads: tests and PDFs with a text layer plus candidate output.

    Returns {category: {"tests": [ids], "excluded": number of PDFs left out}}.
    """
    scored = WORK / "scored"
    shutil.rmtree(scored, ignore_errors=True)
    summary = {}
    for category in CATEGORIES:
        kept_lines, ids, excluded = [], [], set()
        for test in tests[category]:
            if has_text[test["pdf"]]:
                kept_lines.append(json.dumps(test, ensure_ascii=False))
                ids.append(test["id"])
            else:
                excluded.add(test["pdf"])
        for pdf in sorted({t["pdf"] for t in tests[category]} - excluded):
            stem = pdf[:-len(".pdf")]
            _link_or_copy(BENCH_DIR / "pdfs" / pdf, scored / "pdfs" / pdf)
            text = WORK / "extract" / pdf.split("/")[0] / os.path.basename(stem) / "text.md"
            candidate = scored / CANDIDATE / f"{stem}_pg1_repeat1.md"
            candidate.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(text, candidate)
        (scored / f"{category}.jsonl").write_text("\n".join(kept_lines) + "\n", encoding="utf-8")
        summary[category] = {"tests": ids, "excluded": len(excluded)}
    return summary


def _score(scored_dir) -> dict:
    """Run the official scorer through the wrapper; return {test id: passed}."""
    results_file = WORK / "results.json"
    log_file = WORK / "scorer.log"
    command = [str(venv_python()), str(HERE / "scorer_wrapper.py"), "--dir", str(scored_dir),
               "--skip_baseline", "--results-out", str(results_file)]
    # PYTHONUTF8: the scorer opens the jsonl files without an encoding, which fails under a
    # Windows legacy code page (cp950 etc.).
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    with open(log_file, "w", encoding="utf-8") as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False, env=env)
    if result.returncode != 0 or not results_file.exists():
        tail = "\n".join(log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-15:])
        die(f"The official scorer failed (full log: {log_file}):\n{tail}")
    return json.loads(results_file.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def _extract_commit() -> str:
    rel = str(EXTRACT_SCRIPT.relative_to(REPO)).replace(os.sep, "/")
    commit = _git("log", "-1", "--format=%h", "--", rel) or "unknown"
    return commit + ("+uncommitted" if _git("status", "--porcelain", "--", rel) else "")


def _category_stats(summary: dict, results: dict) -> dict:
    stats = {}
    for category, info in summary.items():
        passed = sum(1 for test_id in info["tests"] if results.get(test_id))
        stats[category] = {"passed": passed, "total": len(info["tests"]),
                           "excluded_pdfs": info["excluded"]}
    return stats


def _percent(passed: int, total: int) -> float:
    return 100 * passed / total if total else 0.0


def _known_bad() -> set:
    if not KNOWN_BAD.exists():
        return set()
    lines = KNOWN_BAD.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.startswith("#")}


def _print_scores(stats: dict, baseline: dict) -> None:
    for category, now in stats.items():
        rate = _percent(now["passed"], now["total"])
        line = (f"{category:15s} {now['passed']}/{now['total']} = {rate:.1f}%"
                f"  (excluded no-text PDFs: {now['excluded_pdfs']})")
        before = baseline.get("categories", {}).get(category) if baseline else None
        if before:
            old_rate = _percent(before["passed"], before["total"])
            line += f"  vs baseline {old_rate:.1f}% ({rate - old_rate:+.1f})"
        print(line)


def _print_ids(title: str, ids: list, bad: set) -> None:
    print(f"{title}: {len(ids)}")
    for test_id in sorted(ids):
        print(f"  {test_id}{'  [known wrong test, allenai/olmocr#485]' if test_id in bad else ''}")


def _print_delta(results: dict, baseline: dict) -> None:
    was_pass, was_fail = set(baseline["passing"]), set(baseline["failing"])
    bad = _known_bad()
    print(f"\ncompared with baseline of {baseline['date']} "
          f"(extract_text.py {baseline['extract_text']}, {baseline['scorer']})")
    _print_ids("newly failing", [i for i, ok in results.items() if not ok and i in was_pass], bad)
    _print_ids("newly passing", [i for i, ok in results.items() if ok and i in was_fail], bad)
    new = [i for i in results if i not in was_pass and i not in was_fail]
    if new:
        print(f"tests not in the baseline: {len(new)} (a PDF now has or lost its text layer)")


def _write_baseline(stats: dict, results: dict) -> None:
    data = {
        "date": datetime.date.today().isoformat(),
        "extract_text": _extract_commit(),
        "scorer": SCORER_VERSION,
        "categories": stats,
        "passing": sorted(i for i, ok in results.items() if ok),
        "failing": sorted(i for i, ok in results.items() if not ok),
    }
    BASELINE.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    print(f"\nbaseline written: {BASELINE}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--update-baseline", action="store_true",
                        help="rewrite baseline.json with this run")
    parser.add_argument("--workers", type=int, default=4, help="parallel extractions (default 4)")
    args = parser.parse_args()

    if not venv_python().exists():
        die("The scorer venv is missing. Run: python setup_venv.py --python <Python 3.11+>")
    tests = {}
    for category in CATEGORIES:
        path = BENCH_DIR / f"{category}.jsonl"
        if not path.exists():
            die("Bench data is missing. Run: python fetch.py")
        tests[category] = read_jsonl(path)

    pdfs = sorted({test["pdf"] for items in tests.values() for test in items})
    print(f"extracting {len(pdfs)} PDFs ...")
    has_text = _extract_all(pdfs, args.workers)
    summary = _build_scored_dir(tests, has_text)
    print("scoring ...")
    results = _score(WORK / "scored")
    stats = _category_stats(summary, results)

    baseline = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else None
    print()
    _print_scores(stats, baseline)
    if baseline:
        _print_delta(results, baseline)
    else:
        print("\nno baseline yet; run with --update-baseline to record this run")
    if args.update_baseline:
        _write_baseline(stats, results)


if __name__ == "__main__":
    main()
