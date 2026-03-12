import json
import tempfile
import unittest
from pathlib import Path

from skill_catalog.catalog import build_outputs


class CatalogBuildTests(unittest.TestCase):
    def test_build_outputs_generates_catalog_docs_and_readme_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "# Demo Skill\n\nUse this skill to demonstrate the catalog.\n",
                encoding="utf-8",
            )
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 1.2.0\n\n- Added a documented example.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: demo-skill
name: Demo Skill
version: 1.2.0
summary: Demonstrates the generated skill catalog.
description: A sample skill used to validate the catalog and docs pipeline.
authors:
  - Example Team
tags:
  - demo
  - docs
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/demo-skill
entrypoint: SKILL.md
compatibility:
  notes: Works with the local Codex skill loader.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
examples:
  - prompt: Show me the generated docs
    outcome: Returns the generated skill page.
""".strip()
                + "\n",
                encoding="utf-8",
            )

            outputs = build_outputs(repo)

            catalog = json.loads(outputs.catalog_json)
            self.assertEqual(catalog["skills"][0]["slug"], "demo-skill")
            self.assertEqual(catalog["skills"][0]["version"], "1.2.0")
            self.assertIn("Demo Skill", outputs.docs_index)
            self.assertIn("## Installation", outputs.skill_docs["demo-skill"])
            self.assertIn("latest version", outputs.readme)
            self.assertIn("README.zh-TW.md", outputs.readme)
            self.assertIn("繁體中文", outputs.readme_zh_tw)

    def test_build_outputs_lists_multiple_skills_in_generated_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            fixtures = [
                (
                    "demo-skill",
                    "Demo Skill",
                    "Demonstrates the generated skill catalog.",
                ),
                (
                    "android-strings-localized-translate",
                    "Android Strings Localized Translate",
                    "Fills missing translations for nine Android locales.",
                ),
            ]
            for slug, name, summary in fixtures:
                skill_dir = repo / "skills" / slug
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
                (skill_dir / "CHANGELOG.md").write_text(
                    "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
                    encoding="utf-8",
                )
                (skill_dir / "skill.yaml").write_text(
                    f"""
slug: {slug}
name: {name}
version: 0.1.0
summary: {summary}
description: Generated docs should include {name}.
authors:
  - Example
tags:
  - generated
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/{slug}
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

            outputs = build_outputs(repo)

            catalog = json.loads(outputs.catalog_json)
            self.assertEqual(
                [skill["slug"] for skill in catalog["skills"]],
                ["android-strings-localized-translate", "demo-skill"],
            )
            self.assertIn("android-strings-localized-translate", outputs.readme)
            self.assertIn("Android Strings Localized Translate", outputs.docs_index)

    def test_write_outputs_writes_traditional_chinese_readme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            skill_dir = repo / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Demo Skill\n", encoding="utf-8")
            (skill_dir / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
                encoding="utf-8",
            )
            (skill_dir / "skill.yaml").write_text(
                """
slug: demo-skill
name: Demo Skill
version: 0.1.0
summary: Demonstrates the generated skill catalog.
description: A sample skill used to validate the catalog and docs pipeline.
authors:
  - Example Team
tags:
  - demo
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/demo-skill
entrypoint: SKILL.md
compatibility:
  notes: Works with the local Codex skill loader.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
""".strip()
                + "\n",
                encoding="utf-8",
            )

            from skill_catalog.catalog import write_outputs

            outputs = build_outputs(repo)
            write_outputs(repo, outputs)

            readme_zh = (repo / "README.zh-TW.md").read_text(encoding="utf-8")
            self.assertIn("技能 Monorepo Catalog", readme_zh)
            self.assertIn("快速開始", readme_zh)


if __name__ == "__main__":
    unittest.main()
