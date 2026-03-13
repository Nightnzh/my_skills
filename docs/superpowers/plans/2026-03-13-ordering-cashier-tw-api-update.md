# Ordering Cashier TW API Update Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the existing `ordering-cashier-tw` skill so it no longer depends on an interactive browser workflow and instead documents an HTTP/API-first ordering approach with protocol discovery, direct requests, and stricter request-validation boundaries.

**Architecture:** Treat this as a documentation-and-metadata update to an already-installed skill package. The source of truth remains `skills/ordering-cashier-tw/`, but the workflow description, metadata, generated docs, and regression tests must all be updated to reflect protocol discovery and direct request execution rather than UI automation.

**Tech Stack:** Markdown, YAML metadata, Python 3 repository tooling, unittest, generated catalog/docs pipeline

---

## File Structure

- Modify: `skills/ordering-cashier-tw/SKILL.md`
  Rewrite the skill guidance from interactive browser steps to bootstrap extraction, protocol derivation, live menu requests, and direct order submission.
- Modify: `skills/ordering-cashier-tw/skill.yaml`
  Update summary, description, tags, and compatibility notes to describe the HTTP/API-first model.
- Modify: `skills/ordering-cashier-tw/CHANGELOG.md`
  Add a new entry describing the API-oriented workflow update.
- Modify: `tests/test_install.py`
  Keep installer coverage but update fixture metadata wording so it matches the revised skill contract.
- Modify: `tests/test_catalog.py`
  Update generated-doc expectations so the fixture reflects protocol discovery and no longer references browser-first execution.
- Modify: `catalog.json`
  Generated skill index refreshed by `./tools/build_catalog`.
- Modify: `docs/index.md`
  Generated skill listing refreshed by `./tools/build_catalog`.
- Modify: `README.md`
  Generated English readme refreshed if featured summaries change.
- Modify: `README.zh-TW.md`
  Generated Traditional Chinese readme refreshed if featured summaries change.
- Modify: `docs/skills/ordering-cashier-tw.md`
  Generated skill page refreshed by `./tools/build_catalog`.

## Chunk 1: Update Tests For The API-Oriented Skill Contract

### Task 1: Revise fixture-based tests to match the new workflow language

**Files:**
- Modify: `tests/test_install.py`
- Modify: `tests/test_catalog.py`

- [ ] **Step 1: Update the installer fixture metadata in `tests/test_install.py`**

Change the `ordering-cashier-tw` fixture strings so they describe an HTTP/API-first ordering workflow. Use wording like:

```python
summary: Handles HTTP/API-first natural-language ordering for the Taiwan Cashier site.
description: Adds a documented ordering workflow skill package based on protocol discovery and direct requests.
compatibility:
  notes: Requires a host that can inspect and send HTTP requests without relying on an interactive browser.
```

- [ ] **Step 2: Run the focused installer test**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python -m unittest tests.test_install.InstallSkillTests.test_install_skill_copies_ordering_cashier_skill_package -v`
Expected: PASS

- [ ] **Step 3: Update the catalog fixture metadata in `tests/test_catalog.py`**

Change the `ordering-cashier-tw` fixture strings so generated docs expectations match the new protocol-oriented language. Use wording like:

```python
summary: Handles HTTP/API-first natural-language ordering for the Taiwan Cashier site.
description: Documents a protocol-discovery ordering skill for the Taiwan Cashier site.
tags:
  - ordering
  - cashier
  - api
  - protocol
examples:
  - prompt: 幫我點大杯紅茶拿鐵無糖少冰 2 杯
    outcome: Resolves the live menu through direct requests and submits the order when no clarification is needed.
```

- [ ] **Step 4: Run the focused catalog test**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python -m unittest tests.test_catalog.CatalogBuildTests.test_build_outputs_includes_ordering_cashier_skill_in_generated_docs -v`
Expected: PASS

- [ ] **Step 5: Commit the test updates**

```bash
git add tests/test_install.py tests/test_catalog.py
git commit -m "test: update ordering cashier api skill coverage"
```

## Chunk 2: Rewrite The Skill Package Source Files

### Task 2: Update the skill guidance and metadata

**Files:**
- Modify: `skills/ordering-cashier-tw/SKILL.md`
- Modify: `skills/ordering-cashier-tw/skill.yaml`
- Modify: `skills/ordering-cashier-tw/CHANGELOG.md`
- Reference: `docs/superpowers/specs/2026-03-12-ordering-cashier-tw-design.md`

- [ ] **Step 1: Rewrite `skills/ordering-cashier-tw/SKILL.md`**

Update the skill so it describes:

```md
## Workflow
1. Fetch the welcome URL and bootstrap resources.
2. Extract identifiers, config, and request bootstrap data.
3. Derive the live request protocol for menu, cart, and order submission.
4. Build a live menu snapshot for the current session.
5. Parse and resolve the user's natural-language order.
6. Ask one focused clarification question only when required.
7. Execute direct HTTP/background requests.
8. Verify cart and final order state from responses, not UI state.
```

Also update guardrails so they mention:

- login / OTP / CAPTCHA stop conditions
- protocol discovery failures
- unreconstructable request parameters
- no claims of success based only on HTTP 200

- [ ] **Step 2: Update `skills/ordering-cashier-tw/skill.yaml`**

Set metadata to match the new contract. Use values along these lines:

```yaml
summary: Documents an HTTP/API-first natural-language ordering workflow for the Taiwan Cashier site.
description: Adds a full-flow ordering skill package that derives live request protocols, resolves menu options, and submits orders through direct requests with strict stop conditions.
tags:
  - ordering
  - cashier
  - api
  - protocol
compatibility:
  minimum_host_version: "0.1"
  notes: Requires a host that can inspect bootstrap resources and send direct HTTP requests without relying on an interactive browser session.
provides:
  - cashier-ordering
  - protocol-driven-order-resolution
```

- [ ] **Step 3: Append a new changelog entry in `skills/ordering-cashier-tw/CHANGELOG.md`**

Add a new version section or unreleased section such as:

```md
## 0.1.1

- Reworked the skill from an interactive browser workflow to an HTTP/API-first protocol-discovery workflow.
```

If the repo expects explicit version bumps for behavior changes, also update `skill.yaml` from `0.1.0` to `0.1.1`.

- [ ] **Step 4: Run repository validation**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python ./tools/validate_skills`
Expected: PASS

- [ ] **Step 5: Run the focused installer and catalog tests**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python -m unittest tests.test_install tests.test_catalog -v`
Expected: PASS

- [ ] **Step 6: Commit the source-of-truth updates**

```bash
git add skills/ordering-cashier-tw tests/test_install.py tests/test_catalog.py
git commit -m "feat: update ordering cashier skill for api workflow"
```

## Chunk 3: Regenerate Repository Outputs

### Task 3: Refresh generated docs and catalog outputs

**Files:**
- Modify: `catalog.json`
- Modify: `docs/index.md`
- Modify: `docs/skills/ordering-cashier-tw.md`
- Modify: `README.md`
- Modify: `README.zh-TW.md`

- [ ] **Step 1: Rebuild generated outputs**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python ./tools/build_catalog`
Expected: generated files reflect the new summary/description/tag changes

- [ ] **Step 2: Inspect the generated skill doc**

Run: `sed -n '1,220p' docs/skills/ordering-cashier-tw.md`
Expected: installation and examples remain, while the lead description reflects the HTTP/API-first workflow

- [ ] **Step 3: Validate generated output freshness**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python ./tools/validate_skills --check-generated`
Expected: PASS

- [ ] **Step 4: Commit the regenerated outputs**

```bash
git add catalog.json docs/index.md docs/skills/ordering-cashier-tw.md README.md README.zh-TW.md
git commit -m "docs: regenerate ordering cashier api skill outputs"
```

## Chunk 4: Final Verification And Handoff

### Task 4: Verify the revised skill end-to-end at the packaging level

**Files:**
- Reference: `skills/ordering-cashier-tw/SKILL.md`
- Reference: `skills/ordering-cashier-tw/skill.yaml`
- Reference: `docs/skills/ordering-cashier-tw.md`

- [ ] **Step 1: Run the full test suite**

Run: `/Users/en/Desktop/code/my_skills/.venv/bin/python -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 2: Verify installer behavior against the real repo content**

Run: `tmpdir=$(mktemp -d) && /Users/en/Desktop/code/my_skills/.venv/bin/python ./tools/install_skill ordering-cashier-tw --target codex --target-root "$tmpdir" && find "$tmpdir/ordering-cashier-tw" -maxdepth 2 -type f | sort`
Expected: output includes `SKILL.md`, `skill.yaml`, and `CHANGELOG.md`

- [ ] **Step 3: Review the final diff**

Run: `git diff --stat main...HEAD`
Expected: only the skill source files, tests, generated outputs, and approved spec/plan updates appear

- [ ] **Step 4: Request review with `@requesting-code-review`**

Capture review findings before merge or branch handoff. If no subagent reviewer is available in the harness, perform an explicit manual diff review and note that limitation in the handoff.

- [ ] **Step 5: Verify completion with `@verification-before-completion`**

Re-run the exact verification commands that support any claim of success and record their results in the handoff note.
