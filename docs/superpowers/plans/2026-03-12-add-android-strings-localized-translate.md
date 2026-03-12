# Add Android Strings Localized Translate Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the existing `android-strings-localized-translate` skill into this monorepo as a fully installable, documented, versioned skill entry.

**Architecture:** Copy the upstream skill package into `skills/android-strings-localized-translate`, add monorepo metadata and changelog, then regenerate catalog outputs so installer, docs, and machine-readable indexes include the new skill. Protect the behavior with tests that verify recursive installation and generated catalog visibility.

**Tech Stack:** Python 3, unittest, YAML metadata, generated Markdown docs

---

## Chunk 1: Test Coverage

### Task 1: Add failing tests for recursive install and catalog visibility

**Files:**
- Modify: `tests/test_install.py`
- Modify: `tests/test_catalog.py`

- [ ] **Step 1: Write the failing install test**

Add a test that installs `android-strings-localized-translate` from a temporary repo fixture and asserts that `scripts/sync_strings_localized.py` and `agents/openai.yaml` are copied into the destination.

- [ ] **Step 2: Run the tests to verify failure**

Run: `. .venv/bin/activate && python -m unittest tests.test_install tests.test_catalog`
Expected: FAIL because the new skill fixture or generated docs expectations do not exist yet.

- [ ] **Step 3: Write the failing catalog test**

Add a test that includes a second skill and asserts generated docs/readme/catalog expose both slugs and that the Android translation skill summary appears in generated output.

- [ ] **Step 4: Run the tests to verify failure**

Run: `. .venv/bin/activate && python -m unittest tests.test_install tests.test_catalog`
Expected: FAIL with missing skill content assertions.

## Chunk 2: Skill Import

### Task 2: Import the upstream skill package

**Files:**
- Create: `skills/android-strings-localized-translate/SKILL.md`
- Create: `skills/android-strings-localized-translate/skill.yaml`
- Create: `skills/android-strings-localized-translate/CHANGELOG.md`
- Create: `skills/android-strings-localized-translate/scripts/sync_strings_localized.py`
- Create: `skills/android-strings-localized-translate/scripts/validate_strings_localized.py`
- Create: `skills/android-strings-localized-translate/agents/openai.yaml`

- [ ] **Step 1: Copy the upstream files**

Copy the upstream `SKILL.md`, `scripts/`, and `agents/openai.yaml` from `/Users/en/.codex/skills/android-strings-localized-translate/`.

- [ ] **Step 2: Add monorepo metadata**

Create `skill.yaml` with:
- `slug: android-strings-localized-translate`
- `version: 0.1.0`
- `status: active`
- `platforms: [codex, generic]`
- `install.method: script`
- `install.copy.source: skills/android-strings-localized-translate`

- [ ] **Step 3: Add changelog**

Create `CHANGELOG.md` with a `## 0.1.0` heading describing the initial import.

## Chunk 3: Generated Outputs And Verification

### Task 3: Regenerate outputs and verify behavior

**Files:**
- Modify: `README.md`
- Modify: `catalog.json`
- Modify: `docs/index.md`
- Create: `docs/skills/android-strings-localized-translate.md`

- [ ] **Step 1: Build generated outputs**

Run: `. .venv/bin/activate && ./tools/build_catalog`

- [ ] **Step 2: Verify generated content**

Run: `. .venv/bin/activate && ./tools/validate_skills --check-generated`
Expected: PASS

- [ ] **Step 3: Verify tests**

Run: `. .venv/bin/activate && python -m unittest discover -s tests`
Expected: PASS

- [ ] **Step 4: Verify installer on real repo content**

Run: `tmpdir=$(mktemp -d) && . .venv/bin/activate && ./tools/install_skill android-strings-localized-translate --target codex --target-root "$tmpdir" && find "$tmpdir/android-strings-localized-translate" -maxdepth 3 -type f | sort`
Expected: output includes `SKILL.md`, `skill.yaml`, `CHANGELOG.md`, `scripts/sync_strings_localized.py`, `scripts/validate_strings_localized.py`, and `agents/openai.yaml`.
