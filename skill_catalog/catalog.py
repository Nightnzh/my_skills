from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from skill_catalog.models import SkillMetadata
from skill_catalog.repository import load_repository_skills


@dataclass(slots=True)
class BuildOutputs:
    catalog_json: str
    docs_index: str
    skill_docs: dict[str, str]
    readme: str


def build_outputs(repo: Path) -> BuildOutputs:
    skills = load_repository_skills(repo)
    catalog = {
        "generated_at": "static-build",
        "skills": [skill.to_catalog_entry() for skill in skills],
    }
    docs_index = _build_docs_index(skills)
    skill_docs = {skill.slug: _build_skill_doc(skill) for skill in skills}
    readme = _build_readme(skills)
    return BuildOutputs(
        catalog_json=json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        docs_index=docs_index,
        skill_docs=skill_docs,
        readme=readme,
    )


def write_outputs(repo: Path, outputs: BuildOutputs) -> None:
    (repo / "docs" / "skills").mkdir(parents=True, exist_ok=True)
    (repo / "catalog.json").write_text(outputs.catalog_json, encoding="utf-8")
    (repo / "docs" / "index.md").write_text(outputs.docs_index, encoding="utf-8")
    for slug, content in outputs.skill_docs.items():
        (repo / "docs" / "skills" / f"{slug}.md").write_text(content, encoding="utf-8")
    (repo / "README.md").write_text(outputs.readme, encoding="utf-8")


def _build_docs_index(skills: list[SkillMetadata]) -> str:
    lines = [
        "# Skill Catalog",
        "",
        "This index is generated from each skill's `skill.yaml` metadata.",
        "",
        "| Skill | Version | Status | Platforms | Summary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for skill in skills:
        lines.append(
            f"| [{skill.name}](skills/{skill.slug}.md) | {skill.version} | {skill.status} | "
            f"{', '.join(skill.platforms)} | {skill.summary} |"
        )
    lines.append("")
    return "\n".join(lines)


def _build_skill_doc(skill: SkillMetadata) -> str:
    examples = "\n".join(
        f"- `{example.get('prompt', '').strip()}`: {example.get('outcome', '').strip()}"
        for example in skill.examples
    ) or "- None documented yet."
    depends = ", ".join(skill.depends_on) or "None"
    install_method = skill.install.get("method", "unknown")
    return "\n".join(
        [
            f"# {skill.name}",
            "",
            skill.description,
            "",
            "## Metadata",
            "",
            f"- Slug: `{skill.slug}`",
            f"- Version: `{skill.version}`",
            f"- Status: `{skill.status}`",
            f"- Platforms: {', '.join(skill.platforms)}",
            f"- Entry point: `{skill.entrypoint}`",
            "",
            "## Installation",
            "",
            f"- Preferred method: `{install_method}`",
            f"- Installer: `./tools/install_skill {skill.slug}`",
            f"- Git path: `skills/{skill.slug}`",
            "",
            "## Usage",
            "",
            f"Read `{skill.entrypoint}` inside `skills/{skill.slug}` after installation.",
            "",
            "## Examples",
            "",
            examples,
            "",
            "## Dependencies",
            "",
            f"- Depends on: {depends}",
            "",
            "## Changelog",
            "",
            f"- See `skills/{skill.slug}/CHANGELOG.md`",
            "",
        ]
    )


def _build_readme(skills: list[SkillMetadata]) -> str:
    latest = max((skill.updated_at for skill in skills), default="n/a")
    featured = "\n".join(f"- `{skill.slug}`: {skill.summary}" for skill in skills[:5]) or "- No skills yet."
    return "\n".join(
        [
            "# Skills Monorepo Catalog",
            "",
            "A monorepo for versioned skills, installation workflows, and generated documentation.",
            "",
            "## Quick Start",
            "",
            "- Install the latest version of a skill with `./tools/install_skill <slug>`.",
            "- Browse generated docs in `docs/index.md`.",
            "- Validate metadata and generated outputs with `./tools/validate_skills --check-generated`.",
            "",
            "## Featured Skills",
            "",
            featured,
            "",
            "## Repository Facts",
            "",
            f"- Skills tracked: {len(skills)}",
            f"- latest version metadata updated: {latest}",
            "",
            "## Docs",
            "",
            "- [Installation](docs/installation.md)",
            "- [Versioning](docs/versioning.md)",
            "- [Contributing](docs/contributing.md)",
            "- [Catalog Index](docs/index.md)",
            "",
        ]
    )

