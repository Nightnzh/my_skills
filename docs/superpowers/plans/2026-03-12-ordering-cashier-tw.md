# Ordering Cashier TW Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new installable `ordering-cashier-tw` skill package that documents a safe, natural-language, full-flow ordering workflow for the Cashier Taiwan site and integrates it into the monorepo's generated catalog outputs.

**Architecture:** Keep the implementation intentionally lightweight: the first version is a documentation-first skill package with precise execution rules, stop conditions, and examples, not a bundled automation framework. Source-of-truth files live under `skills/ordering-cashier-tw/`, and generated repo outputs are refreshed through the existing catalog builder so installer metadata, docs, and readmes stay synchronized.

**Tech Stack:** Markdown, YAML metadata, Python 3 repository tooling, unittest, generated catalog/docs pipeline

---

## File Structure

- Create: `skills/ordering-cashier-tw/SKILL.md`
  Defines when to use the skill, the live-menu-first workflow, clarification rules, stop conditions, and example prompts.
- Create: `skills/ordering-cashier-tw/skill.yaml`
  Machine-readable metadata used by validation, installation, and generated docs.
- Create: `skills/ordering-cashier-tw/CHANGELOG.md`
  Versioned release history starting at `0.1.0`.
- Create: `docs/skills/ordering-cashier-tw.md`
  Generated file produced by `./tools/build_catalog`; do not hand-edit during implementation.
- Modify: `catalog.json`
  Generated skill index updated by `./tools/build_catalog`.
- Modify: `docs/index.md`
  Generated skill listing updated by `./tools/build_catalog`.
- Modify: `README.md`
  Generated English readme updated by `./tools/build_catalog`.
- Modify: `README.zh-TW.md`
  Generated Traditional Chinese readme updated by `./tools/build_catalog`.
- Modify: `tests/test_install.py`
  Add installer coverage for the new skill package.
- Modify: `tests/test_catalog.py`
  Add catalog-generation coverage for the new skill metadata and generated docs visibility.

## Chunk 1: Workspace And Failing Tests

### Task 1: Create an isolated implementation workspace

**Files:**
- Reference: `docs/superpowers/specs/2026-03-12-ordering-cashier-tw-design.md`

- [ ] **Step 1: Create a dedicated worktree with `@using-git-worktrees`**

Run: `git worktree add ../my_skills-ordering-skill -b codex/ordering-cashier-tw`
Expected: a new worktree is created at `../my_skills-ordering-skill` on branch `codex/ordering-cashier-tw`

- [ ] **Step 2: Confirm the spec is present in the worktree**

Run: `test -f ../my_skills-ordering-skill/docs/superpowers/specs/2026-03-12-ordering-cashier-tw-design.md`
Expected: exit code `0`

### Task 2: Add failing tests for installer and generated catalog visibility

**Files:**
- Modify: `tests/test_install.py`
- Modify: `tests/test_catalog.py`

- [ ] **Step 1: Write the failing installer test in `tests/test_install.py`**

```python
def test_install_skill_copies_ordering_cashier_skill_package(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "repo"
        repo.mkdir()
        skill_dir = repo / "skills" / "ordering-cashier-tw"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Ordering Cashier TW\n", encoding="utf-8")
        (skill_dir / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
            encoding="utf-8",
        )
        (skill_dir / "skill.yaml").write_text(
            \"\"\"
slug: ordering-cashier-tw
name: Ordering Cashier TW
version: 0.1.0
summary: Handles natural-language ordering for the Taiwan Cashier site.
description: Adds a documented ordering workflow skill package.
authors:
  - Skills Team
tags:
  - ordering
  - cashier
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/ordering-cashier-tw
entrypoint: SKILL.md
compatibility:
  notes: Requires a browser-capable host for execution.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
\"\"\".strip()
            + "\n",
            encoding="utf-8",
        )
        target = Path(tmp) / "target"

        result = install_skill(repo=repo, slug="ordering-cashier-tw", target_host="codex", target_root=target)

        self.assertEqual(result.installed_version, "0.1.0")
        self.assertTrue((target / "ordering-cashier-tw" / "SKILL.md").exists())
        self.assertTrue((target / "ordering-cashier-tw" / "skill.yaml").exists())
        self.assertTrue((target / "ordering-cashier-tw" / "CHANGELOG.md").exists())
```

- [ ] **Step 2: Run the installer test to verify failure**

Run: `. .venv/bin/activate && python -m unittest tests.test_install.InstallSkillTests.test_install_skill_copies_ordering_cashier_skill_package -v`
Expected: FAIL because the new test does not exist yet

- [ ] **Step 3: Write the failing catalog-generation test in `tests/test_catalog.py`**

```python
def test_build_outputs_includes_ordering_cashier_skill_in_generated_docs(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        skill_dir = repo / "skills" / "ordering-cashier-tw"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Ordering Cashier TW\n", encoding="utf-8")
        (skill_dir / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 0.1.0\n\n- Initial release.\n",
            encoding="utf-8",
        )
        (skill_dir / "skill.yaml").write_text(
            \"\"\"
slug: ordering-cashier-tw
name: Ordering Cashier TW
version: 0.1.0
summary: Handles natural-language ordering for the Taiwan Cashier site.
description: Documents a full-flow ordering skill for the Taiwan Cashier site.
authors:
  - Skills Team
tags:
  - ordering
  - cashier
  - browser
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/ordering-cashier-tw
entrypoint: SKILL.md
compatibility:
  notes: Requires a browser-capable host for execution.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
examples:
  - prompt: 幫我點大杯紅茶拿鐵無糖少冰 2 杯
    outcome: Resolves the menu options and submits the order when unambiguous.
\"\"\".strip()
            + "\n",
            encoding="utf-8",
        )

        outputs = build_outputs(repo)

        self.assertIn("Ordering Cashier TW", outputs.docs_index)
        self.assertIn("ordering-cashier-tw", outputs.catalog_json)
        self.assertIn("幫我點大杯紅茶拿鐵無糖少冰 2 杯", outputs.skill_docs["ordering-cashier-tw"])
```

- [ ] **Step 4: Run the catalog test to verify failure**

Run: `. .venv/bin/activate && python -m unittest tests.test_catalog.CatalogBuildTests.test_build_outputs_includes_ordering_cashier_skill_in_generated_docs -v`
Expected: FAIL because the new test does not exist yet

- [ ] **Step 5: Commit the failing tests**

```bash
git add tests/test_install.py tests/test_catalog.py
git commit -m "test: add ordering cashier skill coverage"
```

## Chunk 2: Add The Skill Package

### Task 3: Create the source-of-truth skill files

**Files:**
- Create: `skills/ordering-cashier-tw/SKILL.md`
- Create: `skills/ordering-cashier-tw/skill.yaml`
- Create: `skills/ordering-cashier-tw/CHANGELOG.md`
- Reference: `docs/superpowers/specs/2026-03-12-ordering-cashier-tw-design.md`

- [ ] **Step 1: Create `skills/ordering-cashier-tw/SKILL.md` from the approved design**

Include these sections:

```md
---
name: "ordering-cashier-tw"
description: "Use when the task is to place a natural-language order on the Taiwan Cashier online ordering site, resolving live menu options before submitting the order."
---

# Ordering Cashier TW

## When To Use
- user wants to order from the specified Cashier Taiwan store URL
- user provides one natural-language ordering request
- full order submission is in scope if the site does not require extra manual verification

## Workflow
1. Open the welcome URL and verify ordering can proceed.
2. Build a live menu snapshot for the current session.
3. Parse the user's order into structured fields.
4. Resolve fields against the live menu.
5. Ask one clarification question only when resolution is not unique.
6. Execute the UI flow and validate cart state after each item.
7. Submit only when no unresolved issues remain.

## Guardrails
- stop on sold-out items
- stop on login, OTP, CAPTCHA, or unknown required fields
- do not auto-substitute items
- do not claim success without a recognizable completion state
```

- [ ] **Step 2: Create `skills/ordering-cashier-tw/skill.yaml`**

Use this initial metadata:

```yaml
slug: ordering-cashier-tw
name: Ordering Cashier TW
version: 0.1.0
summary: Documents a safe natural-language ordering workflow for the Taiwan Cashier site.
description: Adds a full-flow ordering skill package that requires live menu resolution, minimal clarification, and strict stop conditions before final submission.
authors:
  - Skills Team
tags:
  - ordering
  - cashier
  - browser
  - workflow
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/ordering-cashier-tw
entrypoint: SKILL.md
compatibility:
  minimum_host_version: "0.1"
  notes: Requires a browser-capable host and should stop when manual verification is required.
status: active
created_at: 2026-03-12
updated_at: 2026-03-12
depends_on: []
provides:
  - cashier-ordering
  - natural-language-order-resolution
examples:
  - prompt: 幫我點大杯紅茶拿鐵無糖少冰 2 杯
    outcome: Resolves the live menu choices and submits the order when no clarification is needed.
  - prompt: 幫我點兩杯珍奶，一杯半糖少冰，一杯無糖去冰
    outcome: Parses multiple items, resolves each against the live menu, and stops if any required option is ambiguous.
repository: https://example.com/skills-monorepo
homepage: https://example.com/skills-monorepo/docs/ordering-cashier-tw
assets: []
```

- [ ] **Step 3: Create `skills/ordering-cashier-tw/CHANGELOG.md`**

```md
# Changelog

## 0.1.0

- Initial release of the Taiwan Cashier ordering skill.
```

- [ ] **Step 4: Run repository validation**

Run: `. .venv/bin/activate && ./tools/validate_skills`
Expected: PASS for repository metadata validation

- [ ] **Step 5: Run the new focused tests**

Run: `. .venv/bin/activate && python -m unittest tests.test_install tests.test_catalog -v`
Expected: PASS

- [ ] **Step 6: Commit the skill package**

```bash
git add skills/ordering-cashier-tw tests/test_install.py tests/test_catalog.py
git commit -m "feat: add ordering cashier tw skill package"
```

## Chunk 3: Generate Catalog Outputs

### Task 4: Regenerate the repository outputs from source metadata

**Files:**
- Modify: `catalog.json`
- Modify: `docs/index.md`
- Modify: `README.md`
- Modify: `README.zh-TW.md`
- Create: `docs/skills/ordering-cashier-tw.md`

- [ ] **Step 1: Build the generated outputs**

Run: `. .venv/bin/activate && ./tools/build_catalog`
Expected: generated files are updated to include `ordering-cashier-tw`

- [ ] **Step 2: Inspect the generated skill doc**

Run: `sed -n '1,220p' docs/skills/ordering-cashier-tw.md`
Expected: includes metadata, installation URL, usage note, and both example prompts

- [ ] **Step 3: Validate generated output freshness**

Run: `. .venv/bin/activate && ./tools/validate_skills --check-generated`
Expected: PASS

- [ ] **Step 4: Commit the generated outputs**

```bash
git add catalog.json docs/index.md docs/skills/ordering-cashier-tw.md README.md README.zh-TW.md
git commit -m "docs: generate ordering cashier skill catalog outputs"
```

## Chunk 4: Final Verification And Handoff

### Task 5: Run full verification before completion

**Files:**
- Reference: `skills/ordering-cashier-tw/SKILL.md`
- Reference: `skills/ordering-cashier-tw/skill.yaml`
- Reference: `docs/skills/ordering-cashier-tw.md`

- [ ] **Step 1: Run the full test suite**

Run: `. .venv/bin/activate && python -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 2: Verify installer behavior against the real repo content**

Run: `tmpdir=$(mktemp -d) && . .venv/bin/activate && ./tools/install_skill ordering-cashier-tw --target codex --target-root "$tmpdir" && find "$tmpdir/ordering-cashier-tw" -maxdepth 2 -type f | sort`
Expected: output includes `SKILL.md`, `skill.yaml`, and `CHANGELOG.md`

- [ ] **Step 3: Review the final diff for unintended generated changes**

Run: `git diff --stat main...HEAD`
Expected: only the new skill package, test updates, generated catalog outputs, and plan-relevant docs appear

- [ ] **Step 4: Request review with `@requesting-code-review`**

Capture review findings before merge or branch handoff.

- [ ] **Step 5: Verify completion with `@verification-before-completion`**

Re-run the exact verification commands that support any claim of success and record their results in the handoff note.
