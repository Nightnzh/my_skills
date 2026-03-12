# Catalog Maintainer

Use this skill when you need to add, review, or update skills in this monorepo.

## What it covers

- verifies required metadata before merge
- reminds maintainers to bump versions and changelogs together
- points contributors to the generated documentation flow

## Usage

1. Review `skills/<slug>/skill.yaml`.
2. Confirm `CHANGELOG.md` includes the current version.
3. Run the repository tools to validate and rebuild generated docs.

## Guardrails

- do not merge a skill without a valid `slug`, `version`, and `status`
- keep human-readable guidance in `SKILL.md`
- keep machine-readable metadata in `skill.yaml`
