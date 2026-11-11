import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent.parent / "write-paper-notes"
SKILL_MD = SKILL_DIR / "SKILL.md"

# A relative path into one of the skill's own subdirectories, e.g. `scripts/extract.py`.
# Stops at `<` so placeholder paths like `references/<type>.md` resolve to their real parent dir.
_SKILL_PATH = re.compile(r"(?<![\w<>/.-])((?:scripts|references|templates|assets)/[\w./-]*\w)")


def _referenced_paths():
    return sorted(set(_SKILL_PATH.findall(SKILL_MD.read_text(encoding="utf-8"))))


class TestSkillFiles:
    def test_skill_md_references_some_paths(self):
        assert _referenced_paths(), "expected SKILL.md to reference at least one skill file"

    def test_every_referenced_path_exists(self):
        missing = [p for p in _referenced_paths() if not (SKILL_DIR / p).exists()]
        assert not missing, f"SKILL.md references missing paths: {missing}"

    def test_only_the_v2_instruction_files_remain(self):
        instruction_files = sorted(
            p.relative_to(SKILL_DIR).as_posix()
            for p in SKILL_DIR.rglob("*.md")
        )
        assert instruction_files == ["SKILL.md", "references/style-guide.md"]
