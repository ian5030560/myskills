"""Behaviour of fetch_metrics.py (DOI lookup), checked through its command line only."""

import pytest

from conftest import DOI, SOURCE_SHORT_ID, parse_output


def run_ok(run_fetch, *args, **kwargs):
    result = run_fetch(*args, **kwargs)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    return parse_output(result)


class TestSourcesSideBySide:
    def test_article_numbers_from_both_sources_are_reported_separately(self, fake_api, run_fetch):
        fake_api.serve_everything(openalex={"cited_by_count": 120},
                                  crossref={"is_referenced_by_count": 80})
        out = run_ok(run_fetch, "--doi", DOI)

        openalex, crossref = out["article"]["openalex"], out["article"]["crossref"]
        assert openalex["ok"] and crossref["ok"]
        assert openalex["cited_by_count"] == 120
        assert crossref["is_referenced_by_count"] == 80  # Crossref counts fewer; never merged
        assert openalex["source"] == "OpenAlex" and crossref["source"] == "Crossref"

    def test_each_record_carries_identifier_and_query_time(self, fake_api, run_fetch):
        fake_api.serve_everything()
        out = run_ok(run_fetch, "--doi", DOI)
        for record in (out["article"]["openalex"], out["article"]["crossref"]):
            assert record["identifier"] == DOI
            assert record["queried_at"]
            assert record["url"].startswith(fake_api.url)
        assert out["query"] == {"doi": DOI}
        assert out["queried_at"]

    def test_journal_level_number_is_labelled_as_jif_style_not_jif(self, fake_api, run_fetch):
        fake_api.serve_everything(source={"mean_citedness": 3.5})
        journal = run_ok(run_fetch, "--doi", DOI)["journal"]["openalex"]

        assert journal["ok"]
        assert journal["identifier"] == SOURCE_SHORT_ID
        assert journal["journal"] == "Journal of Examples"
        assert journal["2yr_mean_citedness"] == 3.5
        assert "不是" in journal["note"] and "JIF" in journal["note"]
        assert "impact_factor" not in journal and "jif" not in journal

    def test_author_level_numbers_are_not_reported(self, fake_api, run_fetch):
        fake_api.serve_everything()
        journal = run_ok(run_fetch, "--doi", DOI)["journal"]["openalex"]
        assert "h_index" not in journal and "i10_index" not in journal

    def test_work_without_a_journal_still_succeeds(self, fake_api, run_fetch):
        fake_api.serve_openalex_work(source_id=None)
        fake_api.serve_crossref_work()
        out = run_ok(run_fetch, "--doi", DOI)
        assert out["article"]["openalex"]["ok"]
        assert out["journal"]["openalex"]["ok"]
        assert out["journal"]["openalex"]["journal"] is None
        assert not fake_api.requests_to("/openalex/sources")


class TestRetraction:
    def test_openalex_alone_reporting_retraction_marks_it_retracted(self, fake_api, run_fetch):
        fake_api.serve_everything(openalex={"is_retracted": True})
        retraction = run_ok(run_fetch, "--doi", DOI)["retraction"]
        assert retraction["status"] == "retracted"
        assert retraction["reported_by"] == ["OpenAlex"]

    def test_crossref_alone_reporting_retraction_marks_it_retracted(self, fake_api, run_fetch):
        updated_by = [{"type": "retraction", "source": "retraction-watch", "DOI": "10.1/notice"}]
        fake_api.serve_everything(crossref={"updated_by": updated_by})
        out = run_ok(run_fetch, "--doi", DOI)
        assert out["retraction"]["status"] == "retracted"
        assert out["retraction"]["reported_by"] == ["Crossref"]
        assert out["article"]["crossref"]["retractions"][0]["source"] == "retraction-watch"

    def test_both_sources_are_named_when_both_report_it(self, fake_api, run_fetch):
        fake_api.serve_everything(
            openalex={"is_retracted": True},
            crossref={"updated_by": [{"type": "retraction", "source": "publisher"}]},
        )
        retraction = run_ok(run_fetch, "--doi", DOI)["retraction"]
        assert retraction["status"] == "retracted"
        assert retraction["reported_by"] == ["OpenAlex", "Crossref"]

    def test_no_report_from_either_source_says_no_record_found(self, fake_api, run_fetch):
        fake_api.serve_everything()
        result = run_fetch("--doi", DOI)
        retraction = parse_output(result)["retraction"]
        assert retraction["status"] == "no_record_found"
        assert retraction["text"] == "查無撤稿紀錄"
        assert retraction["reported_by"] == []
        assert retraction["checked_sources"] == ["OpenAlex", "Crossref"]
        # "no record found" must never be worded as "not retracted"
        assert "未撤稿" not in result.stdout.decode("utf-8")

    def test_a_correction_is_not_a_retraction(self, fake_api, run_fetch):
        fake_api.serve_everything(crossref={"updated_by": [{"type": "correction"}]})
        out = run_ok(run_fetch, "--doi", DOI)
        assert out["retraction"]["status"] == "no_record_found"
        assert out["article"]["crossref"]["updates"] == [
            {"type": "correction", "source": None, "doi": None}
        ]


class TestDoiHandling:
    @pytest.mark.parametrize("given", [
        f"https://doi.org/{DOI}", f"http://dx.doi.org/{DOI}", f"doi:{DOI}", f"  {DOI}  ",
    ])
    def test_doi_prefixes_are_stripped(self, fake_api, run_fetch, given):
        fake_api.serve_everything()
        out = run_ok(run_fetch, "--doi", given)
        assert out["query"]["doi"] == DOI
        assert out["article"]["openalex"]["ok"] and out["article"]["crossref"]["ok"]

    @pytest.mark.parametrize("bad", ["not-a-doi", "11.1234/x", "10.1/short-registrant", ""])
    def test_something_that_is_not_a_doi_is_rejected_before_any_request(
            self, fake_api, run_fetch, bad):
        result = run_fetch("--doi", bad)
        assert result.returncode == 2
        assert b"DOI" in result.stderr
        assert not fake_api.requests

    def test_doi_is_required(self, run_fetch):
        assert run_fetch().returncode == 2


class TestKeylessAndPrivate:
    def test_no_key_is_ever_sent(self, fake_api, run_fetch):
        fake_api.serve_everything()
        run_ok(run_fetch, "--doi", DOI,
               env={"OPENALEX_API_KEY": "secret-key", "CROSSREF_API_KEY": "secret-key"})
        assert fake_api.requests
        for request in fake_api.requests:
            assert "api_key" not in request["query"]
            assert "authorization" not in request["headers"]
            assert "crossref-api-key" not in request["headers"]

    def test_user_agent_is_a_generic_client_name(self, fake_api, run_fetch):
        fake_api.serve_everything()
        run_ok(run_fetch, "--doi", DOI)
        for request in fake_api.requests:
            assert request["headers"]["user-agent"].startswith("evaluate-paper")
            assert "@" not in request["headers"]["user-agent"]

    def test_mailto_goes_only_to_crossref_and_never_into_the_output(self, fake_api, run_fetch):
        fake_api.serve_everything()
        address = "someone@example.org"
        result = run_fetch("--doi", DOI, env={"CROSSREF_MAILTO": address})
        assert result.returncode == 0

        crossref_requests = fake_api.requests_to("/crossref")
        assert crossref_requests and all(r["query"]["mailto"] == [address]
                                         for r in crossref_requests)
        assert all("mailto" not in r["query"] for r in fake_api.requests_to("/openalex"))

        text = result.stdout.decode("utf-8") + result.stderr.decode("utf-8")
        assert address not in text and "someone%40example.org" not in text
        assert "mailto=REDACTED" in parse_output(result)["article"]["crossref"]["url"]

    def test_without_mailto_nothing_is_added_to_crossref_requests(self, fake_api, run_fetch):
        fake_api.serve_everything()
        run_ok(run_fetch, "--doi", DOI)
        assert all("mailto" not in r["query"] for r in fake_api.requests)

    def test_mailto_is_not_leaked_through_an_error_message(self, fake_api, run_fetch):
        fake_api.serve_openalex_work()
        fake_api.serve_openalex_source()
        # Crossref route missing -> 404, so the failure record is built from that request
        address = "someone@example.org"
        result = run_fetch("--doi", DOI, env={"CROSSREF_MAILTO": address})
        assert result.returncode == 0
        assert address not in result.stdout.decode("utf-8")


class TestFailuresDoNotCrash:
    def test_one_failing_source_leaves_the_other_intact(self, fake_api, run_fetch):
        fake_api.serve_openalex_work()
        fake_api.serve_openalex_source()
        # no Crossref route -> HTTP 404
        out = run_ok(run_fetch, "--doi", DOI)

        assert out["article"]["openalex"]["ok"]
        crossref = out["article"]["crossref"]
        assert crossref["ok"] is False and "404" in crossref["error"]
        assert out["retraction"]["failed_sources"] == ["Crossref"]
        assert out["retraction"]["checked_sources"] == ["OpenAlex"]

    def test_every_source_failing_exits_nonzero_but_still_reports(self, run_fetch):
        result = run_fetch("--doi", DOI)  # fake server has no routes at all
        assert result.returncode == 1
        out = parse_output(result)
        assert not out["article"]["openalex"]["ok"] and not out["article"]["crossref"]["ok"]
        assert out["retraction"]["checked_sources"] == []


class TestSideEffects:
    def test_script_reads_and_writes_no_files(self, fake_api, run_fetch):
        fake_api.serve_everything()
        run_ok(run_fetch, "--doi", DOI)
        assert list(run_fetch.workdir.iterdir()) == []

    def test_help_documents_the_options(self, run_fetch):
        result = run_fetch("--help", use_fake_api=False)
        assert result.returncode == 0
        assert b"--doi" in result.stdout and b"--api-base" in result.stdout
