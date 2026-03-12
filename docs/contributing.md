# Contributing Skills

## Add a new skill

1. Create `skills/<slug>/`.
2. Add `SKILL.md`, `skill.yaml`, and `CHANGELOG.md`.
3. Fill every required metadata field in `skill.yaml`.
4. Run `./tools/validate_skills --check-generated`.
5. Run `./tools/build_catalog`.
6. Re-run `./tools/validate_skills --check-generated` and commit the generated files.

## Update an existing skill

1. Edit the skill content under `skills/<slug>/`.
2. Bump `version` in `skill.yaml`.
3. Add a new heading for the same version in `CHANGELOG.md`.
4. Rebuild generated outputs with `./tools/build_catalog`.
5. Run `./tools/validate_skills --check-generated`.

## Metadata conventions

- Keep `slug` identical to the folder name.
- Use SemVer for every `version`.
- Mark deprecations with `status: deprecated` plus a `deprecation` block.
- Keep `updated_at` current whenever you change behavior or documentation.
