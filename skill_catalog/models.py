from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SkillMetadata:
    slug: str
    name: str
    version: str
    summary: str
    description: str
    authors: list[str]
    tags: list[str]
    platforms: list[str]
    install: dict[str, Any]
    entrypoint: str
    compatibility: dict[str, Any]
    status: str
    created_at: str
    updated_at: str
    depends_on: list[str] = field(default_factory=list)
    provides: list[str] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)
    repository: str | None = None
    homepage: str | None = None
    deprecation: dict[str, Any] | None = None
    assets: list[str] = field(default_factory=list)
    skill_dir: Path | None = None

    def to_catalog_entry(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "name": self.name,
            "version": self.version,
            "summary": self.summary,
            "description": self.description,
            "authors": self.authors,
            "tags": self.tags,
            "platforms": self.platforms,
            "install": self.install,
            "entrypoint": self.entrypoint,
            "compatibility": self.compatibility,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "depends_on": self.depends_on,
            "provides": self.provides,
            "examples": self.examples,
            "repository": self.repository,
            "homepage": self.homepage,
            "deprecation": self.deprecation,
            "assets": self.assets,
        }

