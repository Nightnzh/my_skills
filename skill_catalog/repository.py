from __future__ import annotations

from pathlib import Path

import yaml

from skill_catalog.models import SkillMetadata

REQUIRED_FIELDS = {
    "slug",
    "name",
    "version",
    "summary",
    "description",
    "authors",
    "tags",
    "platforms",
    "install",
    "entrypoint",
    "compatibility",
    "status",
    "created_at",
    "updated_at",
}


def load_skill_metadata(skill_dir: Path) -> SkillMetadata:
    data = yaml.safe_load((skill_dir / "skill.yaml").read_text(encoding="utf-8")) or {}
    for field in REQUIRED_FIELDS:
        data.setdefault(field, None)
    return SkillMetadata(
        slug=data["slug"],
        name=data["name"],
        version=data["version"],
        summary=data["summary"],
        description=data["description"],
        authors=list(data["authors"] or []),
        tags=list(data["tags"] or []),
        platforms=list(data["platforms"] or []),
        install=dict(data["install"] or {}),
        entrypoint=data["entrypoint"],
        compatibility=dict(data["compatibility"] or {}),
        status=data["status"],
        created_at=str(data["created_at"]),
        updated_at=str(data["updated_at"]),
        depends_on=list(data.get("depends_on") or []),
        provides=list(data.get("provides") or []),
        examples=list(data.get("examples") or []),
        repository=data.get("repository"),
        homepage=data.get("homepage"),
        deprecation=data.get("deprecation"),
        assets=list(data.get("assets") or []),
        skill_dir=skill_dir,
    )


def iter_skill_dirs(repo: Path) -> list[Path]:
    skills_root = repo / "skills"
    if not skills_root.exists():
        return []
    return sorted(path for path in skills_root.iterdir() if path.is_dir())


def load_repository_skills(repo: Path) -> list[SkillMetadata]:
    return [load_skill_metadata(skill_dir) for skill_dir in iter_skill_dirs(repo) if (skill_dir / "skill.yaml").exists()]

