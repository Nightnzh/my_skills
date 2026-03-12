import tempfile
import unittest
from pathlib import Path

from skill_catalog.catalog import build_outputs, write_outputs
from skill_catalog.validation import validate_generated_outputs, validate_repository


class ValidationTests(unittest.TestCase):
    def test_validate_repository_accepts_valid_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "valid-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Valid Skill\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: valid-skill
name: Valid Skill
version: 0.1.0
summary: Valid summary.
description: Valid description.
authors:
  - Example
tags:
  - utility
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/valid-skill
entrypoint: SKILL.md
compatibility:
  notes: None.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )

            report = validate_repository(repo)

            self.assertEqual(report.errors, [])

    def test_validate_generated_outputs_detects_stale_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "stale-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Stale Skill\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: stale-skill
name: Stale Skill
version: 0.1.0
summary: Fresh summary.
description: Generated files should stay in sync.
authors:
  - Example
tags:
  - generated
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/stale-skill
entrypoint: SKILL.md
compatibility:
  notes: None.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )
            write_outputs(repo, build_outputs(repo))
            (repo / "README.md").write_text("# stale\n", encoding="utf-8")

            report = validate_generated_outputs(repo)

            self.assertIn("README.md", "\n".join(report.errors))

    def test_validate_repository_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "broken-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Broken Skill\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.0.0\n\n- Initial release.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: mismatch-slug
name: Broken Skill
version: bad-version
summary: Broken summary.
description: Broken description.
authors:
  - Example
tags:
  - invalid
platforms:
  - codex
install:
  method: script
entrypoint: MISSING.md
compatibility:
  notes: None.
status: unsupported
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )

            report = validate_repository(repo)

            combined = "\n".join(report.errors)
            self.assertIn("folder name", combined)
            self.assertIn("SemVer", combined)
            self.assertIn("entrypoint", combined)
            self.assertIn("status", combined)


if __name__ == "__main__":
    unittest.main()
