"""Fixtures for evaluate-paper tests.

The metrics script is driven as a subprocess against a fake local HTTP server that plays both
OpenAlex (under /openalex) and Crossref (under /crossref). Every JSON body is built here at run
time; there are no static fixture files and the tests never touch the real network.
"""

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "evaluate-paper" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
FETCH_METRICS = SCRIPTS_DIR / "fetch_metrics.py"

DOI = "10.1234/example.2024.001"
SOURCE_ID = "https://openalex.org/S4242"
SOURCE_SHORT_ID = "S4242"


class FakeApi:
    """A tiny scriptable HTTP server that records every request it receives."""

    def __init__(self):
        self.routes = {}
        self.requests = []
        api = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):  # pylint: disable=invalid-name
                parts = urlsplit(self.path)
                api.requests.append({
                    "path": unquote(parts.path),
                    "query": parse_qs(parts.query),
                    "headers": {k.lower(): v for k, v in self.headers.items()},
                })
                status, body = api.routes.get(unquote(parts.path), (404, {"error": "not found"}))
                payload = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):  # keep test output quiet
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def serve(self, path, body, status=200):
        self.routes[path] = (status, body)

    def requests_to(self, prefix):
        return [r for r in self.requests if r["path"].startswith(prefix)]

    # ── response builders ─────────────────────────────────────────────

    def serve_openalex_work(self, doi=DOI, cited_by_count=120, is_retracted=False,
                            source_id=SOURCE_ID, status=200, body=None):
        location = {"source": {"id": source_id}} if source_id else {"source": None}
        self.serve(f"/openalex/works/doi:{doi}", body if body is not None else {
            "id": "https://openalex.org/W1",
            "doi": f"https://doi.org/{doi}",
            "title": "An Example Paper",
            "publication_year": 2024,
            "type": "article",
            "cited_by_count": cited_by_count,
            "is_retracted": is_retracted,
            "primary_location": location,
        }, status)

    def serve_openalex_source(self, short_id=SOURCE_SHORT_ID, mean_citedness=3.5, status=200):
        self.serve(f"/openalex/sources/{short_id}", {
            "id": f"https://openalex.org/{short_id}",
            "display_name": "Journal of Examples",
            "issn_l": "1234-5678",
            "summary_stats": {"2yr_mean_citedness": mean_citedness, "h_index": 99,
                              "i10_index": 500},
        }, status)

    def serve_crossref_work(self, doi=DOI, is_referenced_by_count=80, updated_by=None,
                            status=200, body=None):
        message = {
            "DOI": doi,
            "is-referenced-by-count": is_referenced_by_count,
            "container-title": ["Journal of Examples"],
            "ISSN": ["1234-5678"],
        }
        if updated_by is not None:
            message["updated-by"] = updated_by
        self.serve(f"/crossref/works/{doi}",
                   body if body is not None else {"status": "ok", "message": message}, status)

    def serve_openalex_search(self, results, status=200):
        """Title search results; each is {"doi", "title", "year"} (doi may be None)."""
        self.serve("/openalex/works", {"meta": {"count": len(results)}, "results": [
            {"id": f"https://openalex.org/W{i}", "title": r["title"],
             "doi": f"https://doi.org/{r['doi']}" if r["doi"] else None,
             "publication_year": r["year"]}
            for i, r in enumerate(results)
        ]}, status)

    def serve_crossref_search(self, results, status=200):
        self.serve("/crossref/works", {"status": "ok", "message": {"items": [
            {"DOI": r["doi"], "title": [r["title"]], "issued": {"date-parts": [[r["year"], 1, 1]]}}
            for r in results
        ]}}, status)

    def serve_everything(self, doi=DOI, **overrides):
        """A healthy world: both works and the journal resolve and nothing is retracted."""
        self.serve_openalex_work(doi, **overrides.get("openalex", {}))
        self.serve_openalex_source(**overrides.get("source", {}))
        self.serve_crossref_work(doi, **overrides.get("crossref", {}))


@pytest.fixture
def fake_api():
    api = FakeApi()
    yield api
    api.close()


@pytest.fixture
def run_fetch(fake_api, tmp_path):
    """Run fetch_metrics.py against the fake server from an empty working directory."""
    workdir = tmp_path / "cwd"
    workdir.mkdir()

    def run(*args, env=None, use_fake_api=True):
        full_env = {k: v for k, v in os.environ.items() if k != "CROSSREF_MAILTO"}
        full_env["PYTHONIOENCODING"] = "utf-8"
        full_env.update(env or {})
        cmd = [sys.executable, str(FETCH_METRICS), *args]
        if use_fake_api:
            cmd += ["--api-base", fake_api.url]
        return subprocess.run(cmd, cwd=workdir, env=full_env, capture_output=True,
                              timeout=60, check=False)

    run.workdir = workdir
    return run


def parse_output(result):
    """Decode stdout of a finished run as the JSON document the script prints."""
    return json.loads(result.stdout.decode("utf-8"))


def run_ok(run_fetch, *args, **kwargs):
    """Run the script, require exit code 0, and return its parsed JSON."""
    result = run_fetch(*args, **kwargs)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    return parse_output(result)
