# Repository Guidelines

## Project Structure & Module Organization
Core Python code lives in `skill_catalog/` and provides catalog models, repository helpers, install logic, and the CLI entrypoints. Versioned skills are stored under `skills/<slug>/`, with each skill containing `SKILL.md`, `skill.yaml`, and `CHANGELOG.md`. Generated and hand-written documentation lives in `docs/`, schemas are in `schemas/`, and repository checks are covered by `tests/`. Use `tools/` for repo-local command wrappers such as `build_catalog` and `validate_skills`.

## Build, Test, and Development Commands
- `python3 -m unittest discover -s tests`: run the full test suite.
- `./tools/validate_skills --check-generated`: validate skill metadata, generated docs, and catalog outputs.
- `./tools/build_catalog`: rebuild `catalog.json`, README content, and skill docs from current metadata.
- `python3 -m skill_catalog.cli validate`: run the validator directly during local debugging.

Run validation before and after rebuilding generated files when changing skill metadata or documentation.

## Coding Style & Naming Conventions
Target Python `>=3.11` and follow the existing style: 4-space indentation, standard-library-first imports, and type hints where behavior is non-trivial. Keep module names lowercase with underscores, and match skill folder names exactly to their `slug` values in `skill.yaml`. Markdown docs should use short sections, concrete examples, and relative repository paths like `skills/catalog-maintainer/`.

## Testing Guidelines
Tests use the standard `unittest` framework. Add new test files under `tests/` with names like `test_<area>.py`, and keep test methods descriptive, for example `test_build_outputs_generates_catalog_docs`. When changing generation or validation behavior, add or update tests in the same change. Prefer focused fixture setup with `tempfile.TemporaryDirectory()` as seen in existing catalog tests.

## Commit & Pull Request Guidelines
Recent history follows Conventional Commit prefixes such as `feat:` and `docs:`. Keep commits scoped and imperative, for example `docs: add contributor guide` or `feat: validate deprecated skill metadata`. PRs should describe the user-visible effect, list validation commands run, and note any regenerated files. Include screenshots only when documentation rendering or generated output formatting materially changes.

## Skill Maintenance Notes
When adding or updating a skill, keep `version`, `updated_at`, and `CHANGELOG.md` in sync. Rebuild generated outputs with `./tools/build_catalog`, then rerun `./tools/validate_skills --check-generated` before submitting.
