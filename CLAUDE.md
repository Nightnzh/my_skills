# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A versioned skills monorepo for managing reusable agent skills installable into Claude Code and other compatible platforms. The Python tooling (`skill_catalog/`) handles validation, catalog generation, and installation. Skills live under `skills/<slug>/`.

## Common Commands

```bash
# Run tests
python3 -m unittest discover -s tests

# Run a single test file
python3 -m unittest tests.test_catalog

# Validate all skills (metadata + generated files in sync)
./tools/validate_skills --check-generated

# Rebuild catalog.json, READMEs, and docs/
./tools/build_catalog

# Install a skill locally (~/.codex/skills/<slug>)
./tools/install_skill <slug>
```

**Workflow before committing:** validate first, then rebuild, then commit generated files together with skill changes.

## Architecture

### Core Package: `skill_catalog/`

| Module | Responsibility |
|--------|---------------|
| `models.py` | `SkillMetadata` dataclass; `to_catalog_entry()` serializes to JSON |
| `repository.py` | Discovers and loads `skill.yaml` files from `skills/*/` |
| `validation.py` | SemVer checks, required-file checks, CHANGELOG heading match, slug-folder match, generated-file sync check |
| `catalog.py` | Generates `catalog.json`, `docs/index.md`, `docs/skills/<slug>.md`, `README.md`, `README.zh-TW.md` |
| `install.py` | Copies a skill directory to `~/.codex/skills/<slug>` via `shutil.copytree` |
| `cli.py` | Argparse CLI; three subcommands: `build`, `validate`, `install` |

All three scripts in `tools/` are thin wrappers that call `skill_catalog.cli.main()`.

### Skill Directory Structure

Every skill under `skills/<slug>/` **must** contain:
- `skill.yaml` — machine-readable metadata (slug, name, version, summary, description, authors, tags, platforms, install, entrypoint, compatibility, status, created_at, updated_at)
- `SKILL.md` — human-readable reference with YAML frontmatter (`name`, `description`)
- `CHANGELOG.md` — version history; must include a heading matching the version in `skill.yaml`

Optional subdirectories: `scripts/`, `agents/`, `tests/`.

### Generated Files

These are **auto-built** by `./tools/build_catalog` and must be committed in sync with skill changes:
- `catalog.json`
- `README.md` and `README.zh-TW.md`
- `docs/index.md` and `docs/skills/<slug>.md`

The CI job runs `--check-generated` to enforce this.

### Validation Rules

- `slug` must be lowercase with hyphens only and match the folder name
- `version` must be valid SemVer
- `status` must be one of `active`, `experimental`, `deprecated`
- `install.method` must be `script` or `git`
- `entrypoint` file must exist in the skill directory
- `CHANGELOG.md` must contain a heading for the current version

## Adding or Updating a Skill

1. Create/edit `skills/<slug>/skill.yaml`, `SKILL.md`, `CHANGELOG.md`
2. Run `./tools/validate_skills` — fix any errors
3. Run `./tools/build_catalog` — regenerates docs and catalog
4. Commit skill files **and** generated files together

When bumping a skill version: update `version` and `updated_at` in `skill.yaml` and add a heading in `CHANGELOG.md`.
