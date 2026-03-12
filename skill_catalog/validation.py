from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from skill_catalog.catalog import build_outputs
from skill_catalog.repository import iter_skill_dirs, load_skill_metadata

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")
VALID_STATUSES = {"active", "experimental", "deprecated"}
VALID_INSTALL_METHODS = {"script", "git"}


@dataclass(slots=True)
class ValidationReport:
    errors: list[str] = field(default_factory=list)


def validate_repository(repo: Path) -> ValidationReport:
    report = ValidationReport()
    for skill_dir in iter_skill_dirs(repo):
        _validate_skill_dir(skill_dir, report)
    if not report.errors:
        build_outputs(repo)
    return report


def validate_generated_outputs(repo: Path) -> ValidationReport:
    report = ValidationReport()
    outputs = build_outputs(repo)
    expected_files = {
        repo / "README.md": outputs.readme,
        repo / "catalog.json": outputs.catalog_json,
        repo / "docs" / "index.md": outputs.docs_index,
    }
    for slug, content in outputs.skill_docs.items():
        expected_files[repo / "docs" / "skills" / f"{slug}.md"] = content

    for path, expected in expected_files.items():
        if not path.exists():
            report.errors.append(f"{path.relative_to(repo)} is missing generated content")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            report.errors.append(f"{path.relative_to(repo)} is out of date; rebuild generated outputs")
    return report


def _validate_skill_dir(skill_dir: Path, report: ValidationReport) -> None:
    required_paths = ["skill.yaml", "SKILL.md", "CHANGELOG.md"]
    for required_path in required_paths:
        if not (skill_dir / required_path).exists():
            report.errors.append(f"{skill_dir.name}: missing required file `{required_path}`")
    if report.errors and not (skill_dir / "skill.yaml").exists():
        return

    skill = load_skill_metadata(skill_dir)
    if skill.slug != skill_dir.name:
        report.errors.append(f"{skill_dir.name}: slug must match folder name")
    if not SEMVER_RE.match(skill.version or ""):
        report.errors.append(f"{skill.slug}: version must be valid SemVer")
    if skill.status not in VALID_STATUSES:
        report.errors.append(f"{skill.slug}: status must be one of {sorted(VALID_STATUSES)}")
    if skill.install.get("method") not in VALID_INSTALL_METHODS:
        report.errors.append(f"{skill.slug}: install.method must be one of {sorted(VALID_INSTALL_METHODS)}")
    if not skill.entrypoint or not (skill_dir / skill.entrypoint).exists():
        report.errors.append(f"{skill.slug}: entrypoint must point to an existing file")
    changelog = (skill_dir / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {skill.version}" not in changelog:
        report.errors.append(f"{skill.slug}: CHANGELOG.md must contain heading for version {skill.version}")
    for field_name in ["name", "summary", "description", "created_at", "updated_at"]:
        if not getattr(skill, field_name):
            report.errors.append(f"{skill.slug}: missing required field `{field_name}`")
