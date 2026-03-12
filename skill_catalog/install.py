from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from skill_catalog.models import SkillMetadata
from skill_catalog.repository import load_repository_skills


@dataclass(slots=True)
class InstallResult:
    slug: str
    installed_version: str
    destination: Path


def list_installable_skills(repo: Path) -> list[SkillMetadata]:
    return sorted(load_repository_skills(repo), key=lambda skill: skill.slug)


def install_skill(
    repo: Path,
    slug: str,
    target_host: str,
    target_root: Path,
    version: str | None = None,
    allow_deprecated: bool = False,
) -> InstallResult:
    skills = [skill for skill in load_repository_skills(repo) if skill.slug == slug]
    if not skills:
        raise ValueError(f"Unknown skill: {slug}")
    skill = skills[0]
    if version is not None and version != skill.version:
        raise ValueError(f"Requested version {version} is not available for {slug}")
    if skill.status == "deprecated" and not allow_deprecated:
        raise ValueError(f"Skill {slug} is deprecated and requires --allow-deprecated")
    if target_host not in skill.platforms:
        raise ValueError(f"Skill {slug} does not support target host {target_host}")

    destination = target_root / slug
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(skill.skill_dir, destination)
    return InstallResult(slug=slug, installed_version=skill.version, destination=destination)
