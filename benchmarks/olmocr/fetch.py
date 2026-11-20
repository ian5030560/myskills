#!/usr/bin/env python3
"""Download the scored part of olmOCR-Bench into the gitignored data folder.

Only the jsonl test files and PDFs of the categories listed in bench_common.CATEGORIES are
fetched (about 88 MB), keeping the dataset's ``bench_data/`` layout. Files already present are
skipped, so rerunning is cheap. No Hugging Face account or token is needed.
"""

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from bench_common import BENCH_DIR, CATEGORIES, HF_BASE, die, read_jsonl

USER_AGENT = "myskills-olmocr-bench-fetch"
TIMEOUT = 60


def _download(url: str, dest) -> bool:
    """Download url to dest; return False when the file was already there."""
    if dest.exists() and dest.stat().st_size > 0:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response, open(part, "wb") as out:
        while chunk := response.read(1 << 16):
            out.write(chunk)
    part.replace(dest)
    return True


def _url(relative: str) -> str:
    return f"{HF_BASE}/{urllib.parse.quote(relative)}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workers", type=int, default=8, help="parallel downloads (default 8)")
    args = parser.parse_args()

    jobs = []
    try:
        for category in CATEGORIES:
            jsonl = BENCH_DIR / f"{category}.jsonl"
            _download(_url(f"{category}.jsonl"), jsonl)
            pdfs = sorted({test["pdf"] for test in read_jsonl(jsonl)})
            jobs += [(_url(f"pdfs/{pdf}"), BENCH_DIR / "pdfs" / pdf) for pdf in pdfs]
    except (urllib.error.URLError, OSError) as exc:
        die(f"Could not download the test files: {exc}")

    fetched = skipped = failed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [(dest, pool.submit(_download, url, dest)) for url, dest in jobs]
        for dest, future in futures:
            try:
                if future.result():
                    fetched += 1
                else:
                    skipped += 1
            except (urllib.error.URLError, OSError) as exc:
                failed += 1
                print(f"failed: {dest.name}: {exc}", file=sys.stderr)

    print(f"pdfs: {len(jobs)} (downloaded {fetched}, already present {skipped}, failed {failed})")
    print(f"data: {BENCH_DIR}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
