# Versioning Policy

Each skill is versioned independently with SemVer.

## Bump rules

- `MAJOR`: breaking changes in prompts, required inputs, outputs, or compatibility.
- `MINOR`: backward-compatible capability additions.
- `PATCH`: fixes, documentation improvements, examples, or metadata-only corrections that do not break consumers.

## Changelog rules

- Every skill must maintain `skills/<slug>/CHANGELOG.md`.
- The newest heading must match the `version` in `skill.yaml`.
- Do not rely on repo tags as the source of truth for skill versioning.

## Lifecycle states

- `active`: normal installation path.
- `experimental`: available but subject to change.
- `deprecated`: preserved for compatibility; installer requires explicit opt-in.
