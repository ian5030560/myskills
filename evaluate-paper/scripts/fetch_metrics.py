"""Look up external metrics for one paper from OpenAlex and Crossref (no API keys).

    python fetch_metrics.py --doi 10.1234/abc

Prints one JSON object to stdout: article-level and journal-level numbers from each source side
by side (never merged), plus a retraction verdict. Reads and writes no files.

Exit codes: 0 = at least one source answered, 1 = every source failed, 2 = bad arguments.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

OPENALEX_BASE = "https://api.openalex.org"
CROSSREF_BASE = "https://api.crossref.org"

# Both APIs normally answer in well under 5 s; 20 s tolerates a slow network without hanging.
TIMEOUT_SECONDS = 20
# One retry rides out a transient timeout or 5xx; more would only slow down a real outage.
MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 0.5

# Generic client name: never include personal details in a User-Agent.
USER_AGENT = "evaluate-paper-fetch-metrics/1.0"

OPENALEX_NAME = "OpenAlex"
CROSSREF_NAME = "Crossref"

NO_RETRACTION_TEXT = "查無撤稿紀錄"
JIF_NOTE = "OpenAlex 2-year mean citedness（JIF-style，不是 Clarivate 的 JIF），不可直接與 JIF 比較"

_DOI_PREFIXES = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
_DOI_SHAPE = re.compile(r"^10\.\d{4,9}/\S+$")
_WORK_FIELDS = "id,doi,title,publication_year,type,cited_by_count,is_retracted,primary_location"
_SOURCE_FIELDS = "id,display_name,issn_l,summary_stats"


class FetchError(Exception):
    """A source could not be queried; the message is safe to show (no contact details)."""


def normalize_doi(raw):
    """Strip `doi:` / `https://doi.org/` prefixes; return None when it does not look like a DOI."""
    doi = _DOI_PREFIXES.sub("", raw.strip())
    return doi if _DOI_SHAPE.match(doi) else None


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _redact(text, mailto):
    """Remove the contact address from a URL or message before it reaches the output."""
    if not mailto:
        return text
    quoted = urllib.parse.quote(mailto, safe="")
    for variant in (mailto, quoted, quoted.replace("%40", "@")):
        text = text.replace(variant, "REDACTED")
    return re.sub(r"([?&]mailto=)[^&\s]*", r"\1REDACTED", text)


def _get_json(url):
    """GET a JSON document, retrying once on timeouts, connection errors and 5xx."""
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            time.sleep(RETRY_DELAY_SECONDS)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = f"連線失敗：{type(exc).__name__}"
        except json.JSONDecodeError:
            last_error = "回應不是合法的 JSON"
            break
    raise FetchError(last_error)


def _record(name, identifier, url, **fields):
    return {"source": name, "identifier": identifier, "url": url,
            "queried_at": now_iso(), "ok": True, **fields}


def _failure(name, identifier, url, error):
    return {"source": name, "identifier": identifier, "url": url,
            "queried_at": now_iso(), "ok": False, "error": error}


# ── OpenAlex ──────────────────────────────────────────────────────────


def query_openalex_work(base, doi):
    """Return (article record, OpenAlex source id or None)."""
    url = f"{base}/works/doi:{urllib.parse.quote(doi, safe='/')}?select={_WORK_FIELDS}"
    try:
        work = _get_json(url)
    except FetchError as exc:
        return _failure(OPENALEX_NAME, doi, url, str(exc)), None
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    record = _record(
        OPENALEX_NAME, doi, url,
        title=work.get("title"),
        publication_year=work.get("publication_year"),
        type=work.get("type"),
        cited_by_count=work.get("cited_by_count"),
        is_retracted=bool(work.get("is_retracted")),
    )
    return record, source.get("id")


def query_openalex_journal(base, source_id):
    """Journal-level numbers for an OpenAlex source id like https://openalex.org/S123."""
    short_id = source_id.rstrip("/").rsplit("/", 1)[-1]
    url = f"{base}/sources/{urllib.parse.quote(short_id)}?select={_SOURCE_FIELDS}"
    try:
        source = _get_json(url)
    except FetchError as exc:
        return _failure(OPENALEX_NAME, short_id, url, str(exc))
    stats = source.get("summary_stats") or {}
    return _record(
        OPENALEX_NAME, short_id, url,
        journal=source.get("display_name"),
        issn_l=source.get("issn_l"),
        **{"2yr_mean_citedness": stats.get("2yr_mean_citedness"), "note": JIF_NOTE},
    )


# ── Crossref ──────────────────────────────────────────────────────────


def query_crossref(base, doi, mailto):
    query = f"?mailto={urllib.parse.quote(mailto, safe='')}" if mailto else ""
    url = f"{base}/works/{urllib.parse.quote(doi, safe='/')}{query}"
    shown_url = _redact(url, mailto)
    try:
        message = (_get_json(url) or {}).get("message") or {}
    except FetchError as exc:
        return _failure(CROSSREF_NAME, doi, shown_url, _redact(str(exc), mailto))
    # `updated-by` sits on the original article; `update-to` sits on the notice itself, so only
    # the former says "this article was retracted".
    updates = [
        {"type": u.get("type"), "source": u.get("source"), "doi": u.get("DOI")}
        for u in message.get("updated-by") or []
    ]
    return _record(
        CROSSREF_NAME, doi, shown_url,
        is_referenced_by_count=message.get("is-referenced-by-count"),
        container_title=(message.get("container-title") or [None])[0],
        issn=message.get("ISSN") or [],
        updates=updates,
        retractions=[u for u in updates if u["type"] == "retraction"],
    )


# ── verdict ───────────────────────────────────────────────────────────


def retraction_verdict(openalex_article, crossref_article):
    """Any source reporting a retraction makes the paper retracted.

    Finding nothing is reported as "no record found", never as "not retracted".
    """
    reported_by, checked, failed = [], [], []
    for record in (openalex_article, crossref_article):
        if not record["ok"]:
            failed.append(record["source"])
            continue
        checked.append(record["source"])
        retracted = record.get("is_retracted") or record.get("retractions")
        if retracted:
            reported_by.append(record["source"])
    verdict = {"checked_sources": checked, "failed_sources": failed}
    if reported_by:
        return {"status": "retracted", "reported_by": reported_by, **verdict}
    return {"status": "no_record_found", "reported_by": [], "text": NO_RETRACTION_TEXT, **verdict}


def fetch_metrics(doi, openalex_base, crossref_base, mailto):
    openalex_article, source_id = query_openalex_work(openalex_base, doi)
    if source_id:
        openalex_journal = query_openalex_journal(openalex_base, source_id)
    elif openalex_article["ok"]:
        openalex_journal = _record(OPENALEX_NAME, doi, openalex_article["url"], journal=None,
                                   note="OpenAlex 沒有這篇文章的期刊資料")
    else:
        openalex_journal = _failure(OPENALEX_NAME, doi, openalex_article["url"],
                                    "文章查詢失敗，無法取得期刊資料")
    crossref_article = query_crossref(crossref_base, doi, mailto)
    return {
        "query": {"doi": doi},
        "queried_at": now_iso(),
        "article": {"openalex": openalex_article, "crossref": crossref_article},
        "journal": {"openalex": openalex_journal},
        "retraction": retraction_verdict(openalex_article, crossref_article),
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Fetch external metrics for a paper from OpenAlex and Crossref (no keys)."
    )
    parser.add_argument("--doi", required=True, help="DOI, with or without a doi.org prefix")
    parser.add_argument(
        "--api-base",
        help="Serve both APIs from one host for testing: OpenAlex at <base>/openalex, "
             "Crossref at <base>/crossref",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    doi = normalize_doi(args.doi)
    if doi is None:
        print(f"error: {args.doi!r} does not look like a DOI (expected 10.<registrant>/<suffix>)",
              file=sys.stderr)
        return 2
    if args.api_base:
        base = args.api_base.rstrip("/")
        openalex_base, crossref_base = f"{base}/openalex", f"{base}/crossref"
    else:
        openalex_base, crossref_base = OPENALEX_BASE, CROSSREF_BASE
    mailto = os.environ.get("CROSSREF_MAILTO", "").strip() or None

    result = fetch_metrics(doi, openalex_base, crossref_base, mailto)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sources = (result["article"]["openalex"], result["article"]["crossref"])
    return 0 if any(s["ok"] for s in sources) else 1


if __name__ == "__main__":
    sys.exit(main())
