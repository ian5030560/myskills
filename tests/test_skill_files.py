"""Checks every skill folder in the repo against the Agent Skills specification.

Rules and sources: .scratch/evaluate-paper/research/agent-skills-spec.md
(hard rules #1-#18, #22, plus the cheap recommendations #20, #23).
Writing quality (e.g. third-person descriptions) is deliberately not tested.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
RESOURCE_DIRS = ("scripts", "references", "assets")
RESERVED_WORDS = ("anthropic", "claude")
MAX_SKILL_MD_LINES = 500  # spec: "Keep your main SKILL.md under 500 lines"

_XML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")  # no leading/trailing/double hyphen
# Local targets of markdown links `[text](target)`; URLs and in-page anchors are skipped.
_MD_LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)#\s]+)")


def discover_skills():
    """Skill folders are top-level, non-hidden directories that hold a SKILL.md.

    Hidden folders (.agents, .claude) and the gitignored venv folders have no SKILL.md.
    """
    return sorted(
        p for p in REPO_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".") and (p / "SKILL.md").is_file()
    )


def _split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "SKILL.md must start with a '---' frontmatter line"
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i]), None
    return None, "frontmatter is not closed with '---'"


def _resource_pattern(skill_name):
    # A path into one of the skill's own resource dirs, e.g. `scripts/extract_text.py`. SKILL.md may
    # also write it repo-relative (`pdf/scripts/x.py`), so the skill's own folder name is an
    # optional prefix. Stops at `<` so placeholders like `references/<type>.md` resolve to their
    # real parent.
    dirs = "|".join(RESOURCE_DIRS)
    return re.compile(rf"(?<![\w<>/.-])(?:{re.escape(skill_name)}/)?((?:{dirs})/[\w./-]*\w)")


def referenced_paths(skill_dir, text):
    """Skill-relative paths mentioned in `text`: resource-dir paths and local markdown links."""
    found = set(_resource_pattern(skill_dir.name).findall(text))
    found.update(m.strip("/") for m in _MD_LINK.findall(text))
    return found


def _check_frontmatter(skill_dir, fm):
    errors = []
    unexpected = sorted(set(fm) - ALLOWED_FIELDS)
    if unexpected:
        errors.append(f"unexpected frontmatter fields: {unexpected}")

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name is required and must be a non-empty string")
    else:
        if len(name) > 64:
            errors.append(f"name is {len(name)} characters, max is 64")
        if not _NAME.fullmatch(name):
            errors.append(f"name {name!r} must be lowercase letters, digits and single hyphens, "
                          "not starting or ending with a hyphen")
        if name != skill_dir.name:
            errors.append(f"name {name!r} must match the folder name {skill_dir.name!r}")
        if any(word in name for word in RESERVED_WORDS):
            errors.append(f"name {name!r} must not contain {RESERVED_WORDS}")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("description is required and must be a non-empty string")
    else:
        if len(desc) > 1024:
            errors.append(f"description is {len(desc)} characters, max is 1024")
        if _XML_TAG.search(desc):
            errors.append("description must not contain XML tags")

    if "license" in fm and not isinstance(fm["license"], str):
        errors.append("license must be a string")
    if "compatibility" in fm:
        compat = fm["compatibility"]
        if not isinstance(compat, str) or not 1 <= len(compat) <= 500:
            errors.append("compatibility must be a string of 1-500 characters")
    if "metadata" in fm:
        meta = fm["metadata"]
        if not isinstance(meta, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in meta.items()
        ):
            errors.append("metadata must be a map from string keys to string values")
    if "allowed-tools" in fm and not isinstance(fm["allowed-tools"], str):
        errors.append("allowed-tools must be a space-separated string")
    return errors


def _check_references(skill_dir, text):
    errors = []
    referenced = referenced_paths(skill_dir, text)

    missing = sorted(p for p in referenced if not (skill_dir / p).exists())
    if missing:
        errors.append(f"SKILL.md references missing paths: {missing}")

    # One level deep: a markdown file SKILL.md points to must not point at other skill files.
    for rel in sorted(p for p in referenced if p.endswith(".md") and (skill_dir / p).is_file()):
        nested = referenced_paths(skill_dir, (skill_dir / rel).read_text(encoding="utf-8"))
        nested.discard(rel)
        if nested:
            errors.append(f"{rel} references other skill files {sorted(nested)}; "
                          "references must stay one level deep from SKILL.md")

    # Orphans: every file under the resource dirs must be mentioned by SKILL.md.
    for res in RESOURCE_DIRS:
        base = skill_dir / res
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(skill_dir).as_posix()
            if rel not in text:
                errors.append(f"{rel} is not referenced by SKILL.md")
    return errors


def check_skill(skill_dir):
    """Return a list of human-readable spec violations for one skill folder (empty = valid)."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md is missing"]
    text = skill_md.read_text(encoding="utf-8")

    raw, problem = _split_frontmatter(text)
    if problem:
        return [problem]
    try:
        fm = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return [f"frontmatter is not valid YAML: {exc}"]
    if not isinstance(fm, dict):
        return ["frontmatter must be a YAML mapping"]

    errors = _check_frontmatter(skill_dir, fm)
    line_count = len(text.splitlines())
    if line_count >= MAX_SKILL_MD_LINES:
        errors.append(f"SKILL.md has {line_count} lines, keep it under {MAX_SKILL_MD_LINES}")
    errors.extend(_check_references(skill_dir, text))
    return errors


# ── real skills ───────────────────────────────────────────────────────


def test_repo_has_skills():
    names = [p.name for p in discover_skills()]
    assert {"pdf", "write-paper-notes"} <= set(names)


@pytest.mark.parametrize("skill_dir", discover_skills(), ids=lambda p: p.name)
def test_skill_follows_the_spec(skill_dir):
    errors = check_skill(skill_dir)
    assert not errors, f"{skill_dir.name}: " + "; ".join(errors)


# ── the checks themselves: each violation must be caught ─────────────


def make_skill(root, name="demo", frontmatter=None, body="Do the thing.\n", files=None):
    """Build a fake skill folder; `frontmatter` is the raw text between the '---' lines."""
    skill_dir = root / name
    skill_dir.mkdir()
    if frontmatter is None:
        frontmatter = f"name: {name}\ndescription: Does the demo thing."
    (skill_dir / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
    for rel, content in (files or {}).items():
        target = skill_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return skill_dir


def test_a_minimal_valid_skill_passes(tmp_path):
    assert check_skill(make_skill(tmp_path)) == []


def test_a_fully_featured_valid_skill_passes(tmp_path):
    fm = (
        "name: demo\n"
        "description: Does the demo thing.\n"
        "license: MIT\n"
        "compatibility: Needs network access.\n"
        "allowed-tools: Read Bash\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
    )
    body = "Run `scripts/run.py` and read `references/guide.md`.\n"
    skill = make_skill(tmp_path, frontmatter=fm, body=body,
                       files={"scripts/run.py": "", "references/guide.md": "# Guide\n"})
    assert check_skill(skill) == []


def test_repo_relative_paths_in_skill_md_count_as_references(tmp_path):
    skill = make_skill(tmp_path, body="Run `python demo/scripts/run.py`.\n",
                       files={"scripts/run.py": ""})
    assert check_skill(skill) == []


@pytest.mark.parametrize("frontmatter, expected", [
    ("name: demo\ndescription: Fine.\nversion: 1.0.0", "unexpected frontmatter fields"),
    ("name: demo\ndescription: Fine.\nuser-invocable: true", "unexpected frontmatter fields"),
    ("description: Fine.", "name is required"),
    ("name: ''\ndescription: Fine.", "name is required"),
    ("name: other\ndescription: Fine.", "must match the folder name"),
    ("name: Demo\ndescription: Fine.", "lowercase"),
    ("name: de_mo\ndescription: Fine.", "lowercase"),
    ("name: -demo\ndescription: Fine.", "hyphen"),
    ("name: demo-\ndescription: Fine.", "hyphen"),
    ("name: de--mo\ndescription: Fine.", "hyphen"),
    ("name: demo\n", "description is required"),
    ("name: demo\ndescription: ''", "description is required"),
    ("name: demo\ndescription: Use <b>bold</b> text.", "XML tags"),
    ("name: demo\ndescription: Fine.\ncompatibility: ''", "compatibility"),
    ("name: demo\ndescription: Fine.\nmetadata:\n  version: 2", "metadata"),
    ("name: demo\ndescription: Fine.\nmetadata:\n  nested:\n    key: value", "metadata"),
    ("name: demo\ndescription: Fine.\nallowed-tools:\n  - Read", "allowed-tools"),
    ("- just\n- a list", "mapping"),
])
def test_frontmatter_violations_are_caught(tmp_path, frontmatter, expected):
    errors = check_skill(make_skill(tmp_path, frontmatter=frontmatter))
    assert any(expected in e for e in errors), errors


@pytest.mark.parametrize("name", ["claude-helper", "my-anthropic-tool"])
def test_reserved_words_in_name_are_caught(tmp_path, name):
    skill = make_skill(tmp_path, name=name)
    assert any("must not contain" in e for e in check_skill(skill))


def test_name_over_64_characters_is_caught(tmp_path):
    skill = make_skill(tmp_path, name="a" * 65)
    assert any("max is 64" in e for e in check_skill(skill))


def test_description_over_1024_characters_is_caught(tmp_path):
    fm = f"name: demo\ndescription: {'x' * 1025}"
    assert any("max is 1024" in e for e in check_skill(make_skill(tmp_path, frontmatter=fm)))


def test_compatibility_over_500_characters_is_caught(tmp_path):
    fm = f"name: demo\ndescription: Fine.\ncompatibility: {'x' * 501}"
    assert any("compatibility" in e for e in check_skill(make_skill(tmp_path, frontmatter=fm)))


def test_missing_skill_md_is_caught(tmp_path):
    (tmp_path / "demo").mkdir()
    assert check_skill(tmp_path / "demo") == ["SKILL.md is missing"]


def test_missing_or_unclosed_frontmatter_is_caught(tmp_path):
    no_fm = tmp_path / "nofm"
    no_fm.mkdir()
    (no_fm / "SKILL.md").write_text("# Just a heading\n", encoding="utf-8")
    assert any("must start with" in e for e in check_skill(no_fm))

    unclosed = tmp_path / "unclosed"
    unclosed.mkdir()
    (unclosed / "SKILL.md").write_text("---\nname: unclosed\n", encoding="utf-8")
    assert any("not closed" in e for e in check_skill(unclosed))


def test_invalid_yaml_is_caught(tmp_path):
    skill = make_skill(tmp_path, frontmatter="name: [unclosed")
    assert any("not valid YAML" in e for e in check_skill(skill))


def test_skill_md_of_500_lines_is_caught(tmp_path):
    long_body = "line\n" * 500
    errors = check_skill(make_skill(tmp_path, body=long_body))
    assert any("lines" in e for e in errors)


def test_skill_md_just_under_500_lines_passes(tmp_path):
    body = "line\n" * 490  # 4 frontmatter lines + 490 body lines = 494 total
    assert check_skill(make_skill(tmp_path, body=body)) == []


def test_reference_to_a_missing_file_is_caught(tmp_path):
    skill = make_skill(tmp_path, body="Run `scripts/gone.py`.\n")
    assert any("missing paths" in e and "scripts/gone.py" in e for e in check_skill(skill))


def test_markdown_link_to_a_missing_file_is_caught(tmp_path):
    skill = make_skill(tmp_path, body="See [guide](GUIDE.md).\n")
    assert any("missing paths" in e and "GUIDE.md" in e for e in check_skill(skill))


def test_urls_and_anchors_in_links_are_not_treated_as_paths(tmp_path):
    body = "See [docs](https://example.com/a.md) and [top](#top).\n"
    assert check_skill(make_skill(tmp_path, body=body)) == []


def test_unreferenced_file_in_a_resource_dir_is_caught(tmp_path):
    skill = make_skill(tmp_path, body="Run `scripts/used.py`.\n",
                       files={"scripts/used.py": "", "scripts/orphan.py": "",
                              "references/orphan.md": "x", "assets/orphan.png": "x"})
    errors = check_skill(skill)
    for orphan in ("scripts/orphan.py", "references/orphan.md", "assets/orphan.png"):
        assert any(orphan in e and "not referenced" in e for e in errors), errors


def test_pycache_is_not_an_orphan(tmp_path):
    skill = make_skill(tmp_path, body="Run `scripts/used.py`.\n",
                       files={"scripts/used.py": "", "scripts/__pycache__/used.pyc": "x"})
    assert check_skill(skill) == []


def test_files_outside_resource_dirs_are_not_checked_for_orphans(tmp_path):
    skill = make_skill(tmp_path, files={"README.md": "x", "LICENSE": "x"})
    assert check_skill(skill) == []


def test_reference_that_points_at_another_reference_is_caught(tmp_path):
    skill = make_skill(
        tmp_path,
        body="Read `references/a.md` and `references/b.md`.\n",
        files={"references/a.md": "Also read references/b.md.\n", "references/b.md": "end\n"},
    )
    assert any("one level deep" in e and "references/a.md" in e for e in check_skill(skill))


def test_a_reference_that_mentions_only_itself_is_fine(tmp_path):
    skill = make_skill(tmp_path, body="Read `references/a.md`.\n",
                       files={"references/a.md": "This is references/a.md.\n"})
    assert check_skill(skill) == []


def test_discover_skills_ignores_hidden_and_non_skill_folders():
    names = {p.name for p in discover_skills()}
    assert not any(n.startswith(".") for n in names)
    assert not names & {"tests", "docs", "Lib", "Scripts", "Include"}
