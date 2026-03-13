import tempfile
import unittest
from pathlib import Path

from skill_catalog.install import install_skill, list_installable_skills


class InstallSkillTests(unittest.TestCase):
    def test_install_skill_copies_active_skill_into_codex_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            skill_dir = repo / "skills" / "copy-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Copy Skill\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.0.0\n\n- Initial release.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: copy-skill
name: Copy Skill
version: 1.0.0
summary: Copies into the target skills directory.
description: Used to verify installer behavior.
authors:
  - Example
tags:
  - install
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/copy-skill
entrypoint: SKILL.md
compatibility:
  notes: Works for Codex.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )
            target = Path(tmp) / "target"

            result = install_skill(repo=repo, slug="copy-skill", target_host="codex", target_root=target)

            self.assertEqual(result.installed_version, "1.0.0")
            self.assertTrue((target / "copy-skill" / "SKILL.md").exists())

    def test_list_installable_skills_returns_sorted_summary_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            for slug in ("z-skill", "a-skill"):
                skill_dir = repo / "skills" / slug
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(f"# {slug}\n", encoding="utf-8")
                (skill_dir / "CHANGELOG.md").write_text(
                    "# Changelog\n\n## 1.0.0\n\n- Initial release.\n",
                    encoding="utf-8",
                )
                (skill_dir / "skill.yaml").write_text(
                    f"""
slug: {slug}
name: {slug}
version: 1.0.0
summary: Summary for {slug}.
description: Description for {slug}.
authors:
  - Example
tags:
  - install
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/{slug}
entrypoint: SKILL.md
compatibility:
  notes: Works for Codex.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                    + "\n",
                    encoding="utf-8",
                )

            skills = list_installable_skills(repo)

            self.assertEqual([skill.slug for skill in skills], ["a-skill", "z-skill"])

    def test_install_skill_rejects_deprecated_skill_without_explicit_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            skill_dir = repo / "skills" / "old-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Old Skill\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 2.0.0\n\n- Deprecated.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: old-skill
name: Old Skill
version: 2.0.0
summary: Deprecated skill.
description: Used to verify status checks.
authors:
  - Example
tags:
  - install
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/old-skill
entrypoint: SKILL.md
compatibility:
  notes: Deprecated.
status: deprecated
created_at: 2026-03-12
updated_at: 2026-03-12
deprecation:
  replacement: copy-skill
  message: Use copy-skill instead.
""".strip()
                + "\n",
                encoding="utf-8",
            )
            target = Path(tmp) / "target"

            with self.assertRaisesRegex(ValueError, "deprecated"):
                install_skill(repo=repo, slug="old-skill", target_host="codex", target_root=target)

    def test_install_skill_copies_nested_scripts_and_agent_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            skill_dir = repo / "skills" / "android-strings-localized-translate"
            (skill_dir / "scripts").mkdir(parents=True)
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Android Skill\n", encoding="utf-8")
            (skill_dir / "scripts" / "sync_strings_localized.py").write_text(
                "print('sync')\n",
                encoding="utf-8",
            )
            (skill_dir / "scripts" / "validate_strings_localized.py").write_text(
                "print('validate')\n",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text("model: gpt-5\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.0\n\n- Initial import.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: android-strings-localized-translate
name: Android Strings Localized Translate
version: 0.1.0
summary: Fills missing translations for nine Android locales.
description: Imports the full Android translation skill package into the monorepo.
authors:
  - Example
tags:
  - android
  - localization
platforms:
  - codex
  - generic
install:
  method: script
  copy:
    source: skills/android-strings-localized-translate
entrypoint: SKILL.md
compatibility:
  notes: Works as a copied skill package.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )
            target = Path(tmp) / "target"

            result = install_skill(
                repo=repo,
                slug="android-strings-localized-translate",
                target_host="codex",
                target_root=target,
            )

            self.assertEqual(result.installed_version, "0.1.0")
            self.assertTrue((target / "android-strings-localized-translate" / "scripts" / "sync_strings_localized.py").exists())
            self.assertTrue((target / "android-strings-localized-translate" / "scripts" / "validate_strings_localized.py").exists())
            self.assertTrue((target / "android-strings-localized-translate" / "agents" / "openai.yaml").exists())

    def test_install_skill_copies_ordering_cashier_skill_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            skill_dir = repo / "skills" / "ordering-cashier-tw"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Ordering Cashier TW\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: ordering-cashier-tw
name: Ordering Cashier TW
version: 0.1.0
summary: Handles HTTP/API-first natural-language ordering for the Taiwan Cashier site.
description: Adds a documented ordering workflow skill package based on protocol discovery and direct requests.
authors:
  - Skills Team
tags:
  - ordering
  - cashier
  - api
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/ordering-cashier-tw
entrypoint: SKILL.md
compatibility:
  notes: Requires a host that can inspect and send HTTP requests without relying on an interactive browser.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )
            target = Path(tmp) / "target"

            result = install_skill(
                repo=repo,
                slug="ordering-cashier-tw",
                target_host="codex",
                target_root=target,
            )

            self.assertEqual(result.installed_version, "0.1.0")
            self.assertTrue((target / "ordering-cashier-tw" / "SKILL.md").exists())
            self.assertTrue((target / "ordering-cashier-tw" / "skill.yaml").exists())
            self.assertTrue((target / "ordering-cashier-tw" / "CHANGELOG.md").exists())


if __name__ == "__main__":
    unittest.main()
