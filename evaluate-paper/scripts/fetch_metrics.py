"""Look up external metrics for one paper from OpenAlex and Crossref (no API keys).

    python fetch_metrics.py --doi 10.1234/abc
    python fetch_metrics.py --title "Exact or approximate paper title"

--doi prints one JSON object: article-level and journal-level numbers from each source side by
side (never merged), plus a retraction verdict. --title only lists candidate papers (title, year,
DOI) from each source; it never picks one or looks up metrics, so a person confirms which paper is
meant and then runs --doi. Nothing is read from or written to disk.

Every source succeeds or fails on its own. A failure is reported with its source, identifier,
time and reason, never as an empty result. Text that comes back from the APIs is treated purely
as data: only the fields below are copied out, cleaned and length-limited.

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
# Five candidates are enough for a person to spot the right paper; OpenAlex charges the same for
# a search however many hits it returns, so asking for more would not be cheaper.
MAX_CANDIDATES = 5
# Titles and names are only displayed; cap them so a hostile record cannot flood the report.
MAX_TEXT_LENGTH = 300

# Generic client name: never include personal details in a User-Agent.
USER_AGENT = "evaluate-paper-fetch-metrics/1.0"

OPENALEX_NAME = "OpenAlex"
CROSSREF_NAME = "Crossref"

# HTTP statuses OpenAlex uses when a request is refused for budget or rate reasons. The script
# does not know the budget figures (they change); it only recognises the refusal.
OPENALEX_QUOTA_STATUSES = (402, 409, 429)

# Failure kinds, so the AI can decide what to do next (e.g. fall back to an MCP on quota).
KIND_HTTP = "http_error"
KIND_NETWORK = "network_error"
KIND_BAD_RESPONSE = "bad_response"
KIND_MISMATCH = "doi_mismatch"
KIND_QUOTA = "quota_exhausted"
KIND_RATE_LIMITED = "rate_limited"
KIND_SKIPPED = "skipped"

NO_RETRACTION_TEXT = "查無撤稿紀錄"
JIF_NOTE = "OpenAlex 2-year mean citedness（JIF-style，不是 Clarivate 的 JIF），不可直接與 JIF 比較"
NEXT_STEP_TEXT = "請從候選中確認是哪一篇，再用 --doi 查詢指標；腳本不會自行選定。"

_DOI_PREFIXES = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)
_DOI_SHAPE = re.compile(r"^10\.\d{4,9}/\S+$")
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]+")
_WORK_FIELDS = "id,doi,title,publication_year,type,cited_by_count,is_retracted,primary_location"
_SOURCE_FIELDS = "id,display_name,issn_l,summary_stats"
_SEARCH_FIELDS_OPENALEX = "id,doi,title,publication_year"
_SEARCH_FIELDS_CROSSREF = "DOI,title,issued"


class FetchError(Exception):
    """A source could not give a usable answer; the message is safe to show."""

    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


def normalize_doi(raw):
    """Strip `doi:` / `https://doi.org/` prefixes; return None when it does not look like a DOI."""
    if not isinstance(raw, str):
        return None
    doi = _DOI_PREFIXES.sub("", raw.strip())
    return doi if _DOI_SHAPE.match(doi) else None


def same_doi(returned, wanted):
    normalized = normalize_doi(returned)
    return normalized is not None and normalized.lower() == wanted.lower()


def clean_text(value, limit=MAX_TEXT_LENGTH):
    """Make text from an API safe to display: strings only, no control characters, bounded."""
    if not isinstance(value, str):
        return None
    text = " ".join(_CONTROL_CHARS.sub(" ", value).split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


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


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _bad(message):
    return FetchError(KIND_BAD_RESPONSE, message)


def _http_failure(code, quota_source):
    if quota_source and code in OPENALEX_QUOTA_STATUSES:
        return FetchError(
            KIND_QUOTA,
            f"OpenAlex 額度用完或被限流（HTTP {code}）；可改用 OpenAlex 的 MCP，否則註記「未取得」",
        )
    if code == 429:
        return FetchError(KIND_RATE_LIMITED, "被限流（HTTP 429），請稍後再試")
    return FetchError(KIND_HTTP, f"HTTP {code}")


def _get_json(url, quota_source=False):
    """GET a JSON document; retry once on timeouts, connection errors and 5xx.

    quota_source marks OpenAlex, whose 402/409/429 mean "out of budget" rather than a plain error.
    """
    request = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    failure = None
    for attempt in range(MAX_RETRIES + 1):
        if attempt:
            time.sleep(RETRY_DELAY_SECONDS)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            failure = _http_failure(exc.code, quota_source)
            if exc.code < 500:
                break
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            failure = FetchError(KIND_NETWORK, f"連線失敗：{type(exc).__name__}")
        except ValueError:  # includes json.JSONDecodeError and bad UTF-8
            failure = _bad("回應不是合法的 JSON")
            break
    raise failure


def _record(name, identifier, url, **fields):
    return {"source": name, "identifier": identifier, "url": url,
            "queried_at": now_iso(), "ok": True, **fields}


def _failure(name, identifier, url, exc):
    return {"source": name, "identifier": identifier, "url": url, "queried_at": now_iso(),
            "ok": False, "kind": exc.kind, "error": str(exc)}


def _lookup(name, identifier, url, parse, mailto=None):
    """Fetch `url`, validate and extract with `parse`; any problem becomes a failure record."""
    shown_url = _redact(url, mailto)
    try:
        fields = parse(_get_json(url, quota_source=name == OPENALEX_NAME))
    except FetchError as exc:
        exc.args = (_redact(str(exc), mailto),)
        return _failure(name, identifier, shown_url, exc)
    return _record(name, identifier, shown_url, **fields)


# ── OpenAlex ──────────────────────────────────────────────────────────


def _parse_openalex_work(work, doi):
    if not isinstance(work, dict):
        raise _bad("回應不是 JSON object")
    returned = work.get("doi")
    if not isinstance(returned, str) or not returned.strip():
        raise _bad("缺少欄位 doi")
    if not _is_int(work.get("cited_by_count")):
        raise _bad("cited_by_count 缺少或不是整數")
    if not isinstance(work.get("is_retracted"), bool):
        raise _bad("is_retracted 缺少或不是布林值")
    if not same_doi(returned, doi):
        raise FetchError(
            KIND_MISMATCH,
            f"回傳的 DOI（{clean_text(returned, 100)}）與查詢的 DOI（{doi}）不一致，不採用這筆紀錄",
        )
    source = (work.get("primary_location") or {}).get("source") or {}
    return {
        "title": clean_text(work.get("title")),
        "publication_year": work.get("publication_year") if _is_int(
            work.get("publication_year")) else None,
        "type": clean_text(work.get("type"), 50),
        "cited_by_count": work["cited_by_count"],
        "is_retracted": work["is_retracted"],
        "journal_id": clean_text(source.get("id"), 100),
    }


def query_openalex_work(base, doi):
    url = f"{base}/works/doi:{urllib.parse.quote(doi, safe='/')}?select={_WORK_FIELDS}"
    return _lookup(OPENALEX_NAME, doi, url, lambda work: _parse_openalex_work(work, doi))


def _parse_openalex_source(source):
    if not isinstance(source, dict):
        raise _bad("回應不是 JSON object")
    stats = source.get("summary_stats")
    if not isinstance(stats, dict):
        raise _bad("summary_stats 缺少或不是物件")
    citedness = stats.get("2yr_mean_citedness")
    if citedness is not None and not _is_number(citedness):
        raise _bad("2yr_mean_citedness 不是數字")
    return {
        "journal": clean_text(source.get("display_name")),
        "issn_l": clean_text(source.get("issn_l"), 20),
        "2yr_mean_citedness": citedness,
        "note": JIF_NOTE,
    }


def query_openalex_journal(base, source_id):
    """Journal-level numbers for an OpenAlex source id like https://openalex.org/S123."""
    short_id = source_id.rstrip("/").rsplit("/", 1)[-1]
    url = f"{base}/sources/{urllib.parse.quote(short_id)}?select={_SOURCE_FIELDS}"
    return _lookup(OPENALEX_NAME, short_id, url, _parse_openalex_source)


def _parse_openalex_search(payload):
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        raise _bad("results 缺少或不是清單")
    candidates = []
    for item in results[:MAX_CANDIDATES]:
        if not isinstance(item, dict):
            raise _bad("results 內有不是物件的項目")
        year = item.get("publication_year")
        candidates.append({"title": clean_text(item.get("title")),
                           "year": year if _is_int(year) else None,
                           "doi": normalize_doi(item.get("doi"))})
    return {"candidates": candidates}


def search_openalex(base, title):
    query = urllib.parse.urlencode({
        "search.title": title, "per-page": MAX_CANDIDATES, "select": _SEARCH_FIELDS_OPENALEX,
    })
    return _lookup(OPENALEX_NAME, title, f"{base}/works?{query}", _parse_openalex_search)


# ── Crossref ──────────────────────────────────────────────────────────


def _parse_crossref_work(payload, doi):
    message = payload.get("message") if isinstance(payload, dict) else None
    if not isinstance(message, dict):
        raise _bad("message 缺少或不是物件")
    returned = message.get("DOI")
    if not isinstance(returned, str) or not returned.strip():
        raise _bad("缺少欄位 DOI")
    if not _is_int(message.get("is-referenced-by-count")):
        raise _bad("is-referenced-by-count 缺少或不是整數")
    raw_updates = message.get("updated-by", [])
    if not isinstance(raw_updates, list) or not all(isinstance(u, dict) for u in raw_updates):
        raise _bad("updated-by 不是物件清單")
    if not same_doi(returned, doi):
        raise FetchError(
            KIND_MISMATCH,
            f"回傳的 DOI（{clean_text(returned, 100)}）與查詢的 DOI（{doi}）不一致，不採用這筆紀錄",
        )
    # `updated-by` sits on the original article; `update-to` sits on the notice itself, so only
    # the former says "this article was retracted".
    updates = [{"type": clean_text(u.get("type"), 50), "source": clean_text(u.get("source"), 50),
                "doi": clean_text(u.get("DOI"), 100)} for u in raw_updates]
    titles = message.get("container-title")
    issns = message.get("ISSN")
    return {
        "is_referenced_by_count": message["is-referenced-by-count"],
        "container_title": clean_text(titles[0]) if isinstance(titles, list) and titles else None,
        "issn": [clean_text(i, 20) for i in issns if isinstance(i, str)]
                if isinstance(issns, list) else [],
        "updates": updates,
        "retractions": [u for u in updates if u["type"] == "retraction"],
    }


def _crossref_url(base, path, mailto, **params):
    if mailto:
        params["mailto"] = mailto
    query = urllib.parse.urlencode(params)
    return f"{base}{path}" + (f"?{query}" if query else "")


def query_crossref(base, doi, mailto):
    url = _crossref_url(base, f"/works/{urllib.parse.quote(doi, safe='/')}", mailto)
    return _lookup(CROSSREF_NAME, doi, url, lambda payload: _parse_crossref_work(payload, doi),
                   mailto)


def _year_from_crossref(item):
    try:
        year = item["issued"]["date-parts"][0][0]
    except (KeyError, IndexError, TypeError):
        return None
    return year if _is_int(year) else None


def _parse_crossref_search(payload):
    message = payload.get("message") if isinstance(payload, dict) else None
    items = message.get("items") if isinstance(message, dict) else None
    if not isinstance(items, list):
        raise _bad("message.items 缺少或不是清單")
    candidates = []
    for item in items[:MAX_CANDIDATES]:
        if not isinstance(item, dict):
            raise _bad("items 內有不是物件的項目")
        titles = item.get("title")
        candidates.append({
            "title": clean_text(titles[0]) if isinstance(titles, list) and titles else None,
            "year": _year_from_crossref(item),
            "doi": normalize_doi(item.get("DOI")),
        })
    return {"candidates": candidates}


def search_crossref(base, title, mailto):
    url = _crossref_url(base, "/works", mailto, **{
        "query.bibliographic": title, "rows": MAX_CANDIDATES, "select": _SEARCH_FIELDS_CROSSREF,
    })
    return _lookup(CROSSREF_NAME, title, url, _parse_crossref_search, mailto)


# ── verdict and top-level lookups ─────────────────────────────────────


def retraction_verdict(openalex_article, crossref_article):
    """Any source reporting a retraction makes the paper retracted.

    Finding nothing is reported as "no record found", never as "not retracted", and a failed
    source makes the check explicitly incomplete.
    """
    reported_by, checked, failed = [], [], []
    for record in (openalex_article, crossref_article):
        if not record["ok"]:
            failed.append(record["source"])
            continue
        checked.append(record["source"])
        if record.get("is_retracted") or record.get("retractions"):
            reported_by.append(record["source"])
    verdict = {"reported_by": reported_by, "checked_sources": checked, "failed_sources": failed,
               "complete": not failed}
    if reported_by:
        return {"status": "retracted", "text": f"{'、'.join(reported_by)} 回報撤稿", **verdict}
    if not checked:
        return {"status": "unknown", "text": "撤稿狀態未取得：所有來源都查詢失敗", **verdict}
    if failed:
        text = (f"在已查詢的來源（{'、'.join(checked)}）{NO_RETRACTION_TEXT}；"
                f"{'、'.join(failed)} 查詢失敗，結果不完整")
        return {"status": "no_record_found", "text": text, **verdict}
    return {"status": "no_record_found", "text": NO_RETRACTION_TEXT, **verdict}


def fetch_by_doi(doi, openalex_base, crossref_base, mailto):
    openalex_article = query_openalex_work(openalex_base, doi)
    if not openalex_article["ok"]:
        skipped = FetchError(KIND_SKIPPED, "文章查詢失敗，無法取得期刊資料")
        openalex_journal = _failure(OPENALEX_NAME, doi, openalex_article["url"], skipped)
    elif openalex_article["journal_id"]:
        openalex_journal = query_openalex_journal(openalex_base, openalex_article["journal_id"])
    else:
        openalex_journal = _record(OPENALEX_NAME, doi, openalex_article["url"], journal=None,
                                   note="OpenAlex 沒有這篇文章的期刊資料")
    crossref_article = query_crossref(crossref_base, doi, mailto)
    return {
        "query": {"doi": doi},
        "queried_at": now_iso(),
        "article": {"openalex": openalex_article, "crossref": crossref_article},
        "journal": {"openalex": openalex_journal},
        "retraction": retraction_verdict(openalex_article, crossref_article),
    }


def fetch_by_title(title, openalex_base, crossref_base, mailto):
    return {
        "query": {"title": title},
        "queried_at": now_iso(),
        "candidates": {"openalex": search_openalex(openalex_base, title),
                       "crossref": search_crossref(crossref_base, title, mailto)},
        "next_step": NEXT_STEP_TEXT,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Fetch external metrics for a paper from OpenAlex and Crossref (no keys)."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--doi", help="DOI, with or without a doi.org prefix: look up metrics")
    target.add_argument("--title", help="paper title: list candidate papers only (no metrics)")
    parser.add_argument(
        "--api-base",
        help="Serve both APIs from one host for testing: OpenAlex at <base>/openalex, "
             "Crossref at <base>/crossref",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.api_base:
        base = args.api_base.rstrip("/")
        openalex_base, crossref_base = f"{base}/openalex", f"{base}/crossref"
    else:
        openalex_base, crossref_base = OPENALEX_BASE, CROSSREF_BASE
    mailto = os.environ.get("CROSSREF_MAILTO", "").strip() or None

    if args.doi is not None:
        doi = normalize_doi(args.doi)
        if doi is None:
            print(f"error: {args.doi!r} does not look like a DOI "
                  "(expected 10.<registrant>/<suffix>)", file=sys.stderr)
            return 2
        result = fetch_by_doi(doi, openalex_base, crossref_base, mailto)
        records = (result["article"]["openalex"], result["article"]["crossref"])
    else:
        title = " ".join(args.title.split())
        if not title:
            print("error: --title is empty", file=sys.stderr)
            return 2
        result = fetch_by_title(title, openalex_base, crossref_base, mailto)
        records = (result["candidates"]["openalex"], result["candidates"]["crossref"])

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if any(r["ok"] for r in records) else 1


if __name__ == "__main__":
    sys.exit(main())
