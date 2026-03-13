# Cashier Order CLI Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new installable `cashier-order-cli` skill that can discover Cashier ordering protocols, resolve natural-language or structured CLI input, submit orders through direct HTTP requests, and only ask follow-up questions when the order cannot be determined uniquely.

**Architecture:** Keep the new skill separate from `ordering-cashier-tw`: `ordering-cashier-tw` remains the protocol-guidance skill, while `cashier-order-cli` ships runnable Python scripts plus skill-local tests. Implement the CLI as a small tool package with focused modules for bootstrap/order creation, HTTP client calls, menu normalization, intent resolution, and terminal interaction, then wire that package into the repo's generated catalog and installer flow.

**Tech Stack:** Python 3.11, `argparse`, `json`, `dataclasses`, `requests`-style HTTP via stdlib or existing lightweight dependency policy, Markdown, YAML metadata, `unittest`, repo catalog/build tooling

---

## File Structure

- Create: `skills/cashier-order-cli/SKILL.md`
  Human-facing skill instructions that explain when to use the CLI skill, how to run the bundled script, supported modes, stop conditions, and status outputs.
- Create: `skills/cashier-order-cli/skill.yaml`
  Skill metadata for slug, version, summary, tags, compatibility notes, installation copy source, and examples.
- Create: `skills/cashier-order-cli/CHANGELOG.md`
  Initial release notes for the new skill.
- Create: `skills/cashier-order-cli/scripts/bootstrap.py`
  Parse welcome URLs, fetch welcome payloads, detect preconditions, and create/recover active order UUIDs.
- Create: `skills/cashier-order-cli/scripts/client.py`
  Encapsulate Cashier HTTP requests, cookies, headers, query params, and order-scoped endpoints.
- Create: `skills/cashier-order-cli/scripts/menu.py`
  Normalize menu payloads into stable data models and provide search/closest-total helpers.
- Create: `skills/cashier-order-cli/scripts/resolver.py`
  Convert natural-language or structured CLI input into order intent, detect ambiguity, and emit minimal clarification requests.
- Create: `skills/cashier-order-cli/scripts/cashier_order.py`
  CLI entrypoint that parses args, orchestrates the flow, renders terminal output, and optionally emits JSON.
- Create: `skills/cashier-order-cli/tests/test_resolver.py`
  Skill-local tests for ambiguity handling, closest-total logic, and structured/natural-language resolution.
- Create: `skills/cashier-order-cli/tests/test_client.py`
  Skill-local tests for welcome/order/menu/cart/payment state handling using fixtures.
- Create: `skills/cashier-order-cli/tests/test_cli.py`
  Skill-local tests for dry-run behavior, JSON output, no-question happy paths, and clarification prompts.
- Modify: `tests/test_install.py`
  Add installer coverage that verifies the new skill copies bundled scripts and local tests.
- Modify: `tests/test_catalog.py`
  Add generated-doc coverage for the new skill summary, examples, and installation output.
- Modify: `catalog.json`
  Generated skill index refreshed by `./tools/build_catalog`.
- Modify: `docs/index.md`
  Generated skill listing refreshed by `./tools/build_catalog`.
- Modify: `docs/skills/cashier-order-cli.md`
  Generated skill page for the new skill.
- Modify: `README.md`
  Generated English catalog output refreshed by `./tools/build_catalog`.
- Modify: `README.zh-TW.md`
  Generated Traditional Chinese catalog output refreshed by `./tools/build_catalog`.

## Chunk 1: Lock Down The Behavior With Tests And Fixtures

### Task 1: Add repo-level coverage for the new skill package

**Files:**
- Modify: `tests/test_install.py`
- Modify: `tests/test_catalog.py`

- [ ] **Step 1: Add an installer fixture for `cashier-order-cli` in `tests/test_install.py`**

Create a fixture skill tree that includes:

```python
(skill_dir / "scripts").mkdir(parents=True)
(skill_dir / "tests").mkdir(parents=True)
(skill_dir / "scripts" / "cashier_order.py").write_text("print('cli')\n", encoding="utf-8")
(skill_dir / "scripts" / "bootstrap.py").write_text("BOOTSTRAP = True\n", encoding="utf-8")
(skill_dir / "tests" / "test_cli.py").write_text("import unittest\n", encoding="utf-8")
```

and metadata like:

```yaml
slug: cashier-order-cli
name: Cashier Order CLI
version: 0.1.0
summary: Provides a pure CLI Cashier ordering workflow through direct HTTP requests.
description: Installs a runnable Cashier ordering CLI skill package with bundled scripts and tests.
```

- [ ] **Step 2: Write assertions that installer output includes nested scripts and tests**

Add assertions like:

```python
self.assertTrue((target / "cashier-order-cli" / "scripts" / "cashier_order.py").exists())
self.assertTrue((target / "cashier-order-cli" / "scripts" / "bootstrap.py").exists())
self.assertTrue((target / "cashier-order-cli" / "tests" / "test_cli.py").exists())
```

- [ ] **Step 3: Run the focused installer test**

Run: `python3 -m unittest tests.test_install.InstallSkillTests.test_install_skill_copies_cashier_order_cli_skill_package -v`
Expected: PASS

- [ ] **Step 4: Add a catalog fixture for `cashier-order-cli` in `tests/test_catalog.py`**

Create a fixture metadata block like:

```yaml
slug: cashier-order-cli
name: Cashier Order CLI
version: 0.1.0
summary: Provides a pure CLI Cashier ordering workflow through direct HTTP requests.
description: Generates docs for a CLI skill that discovers protocols, resolves orders, and submits them without an interactive browser.
tags:
  - ordering
  - cashier
  - cli
  - api
examples:
  - prompt: cashier-order "幫我點最接近 50 元的炸蛋加白飯"
    outcome: Resolves a unique combination and submits it without asking follow-up questions.
```

- [ ] **Step 5: Assert generated outputs mention the new skill**

Add checks like:

```python
self.assertIn("Cashier Order CLI", outputs.docs_index)
self.assertIn("cashier-order-cli", outputs.catalog_json)
self.assertIn("cashier-order \\\"幫我點最接近 50 元的炸蛋加白飯\\\"", outputs.skill_docs["cashier-order-cli"])
```

- [ ] **Step 6: Run the focused catalog test**

Run: `python3 -m unittest tests.test_catalog.CatalogBuildTests.test_build_outputs_includes_cashier_order_cli_skill_in_generated_docs -v`
Expected: PASS

- [ ] **Step 7: Commit the repo-level test coverage**

```bash
git add tests/test_install.py tests/test_catalog.py
git commit -m "test: add cashier order cli skill coverage"
```

## Chunk 2: Build The Executable CLI Modules With Skill-Local Tests

### Task 2: Implement the resolver and menu primitives first

**Files:**
- Create: `skills/cashier-order-cli/scripts/menu.py`
- Create: `skills/cashier-order-cli/scripts/resolver.py`
- Create: `skills/cashier-order-cli/tests/test_resolver.py`

- [ ] **Step 1: Write failing resolver tests**

Cover these cases with `unittest`:

```python
def test_resolve_ambiguous_item_name_returns_needs_input(self):
    ...

def test_resolve_closest_total_prefers_exact_match(self):
    ...

def test_resolve_fried_egg_and_rice_for_50_returns_45_combo(self):
    ...

def test_structured_arguments_and_prompt_share_same_resolution_path(self):
    ...
```

- [ ] **Step 2: Run resolver tests to verify they fail**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -p 'test_resolver.py' -v`
Expected: FAIL with missing modules or assertions

- [ ] **Step 3: Implement `menu.py` with stable item models and closest-total helpers**

Create small focused code such as:

```python
@dataclass
class MenuItem:
    item_id: str
    name: str
    price: int
    sold_out: bool = False

def find_closest_total(items: list[MenuItem], target_total: int) -> list[MenuItem]:
    ...
```

- [ ] **Step 4: Implement `resolver.py` with intent parsing and ambiguity detection**

Include explicit result types such as:

```python
@dataclass
class ResolutionResult:
    status: str
    selected_items: list[MenuItem]
    question: str | None = None
```

Use one path for both parsed prompt tokens and structured arguments.

- [ ] **Step 5: Re-run resolver tests**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -p 'test_resolver.py' -v`
Expected: PASS

- [ ] **Step 6: Commit resolver and menu work**

```bash
git add skills/cashier-order-cli/scripts/menu.py skills/cashier-order-cli/scripts/resolver.py skills/cashier-order-cli/tests/test_resolver.py
git commit -m "feat: add cashier order cli resolver primitives"
```

### Task 3: Implement the client and bootstrap modules against fixture payloads

**Files:**
- Create: `skills/cashier-order-cli/scripts/client.py`
- Create: `skills/cashier-order-cli/scripts/bootstrap.py`
- Create: `skills/cashier-order-cli/tests/test_client.py`

- [ ] **Step 1: Write failing client/bootstrap tests using fixture payloads**

Cover:

```python
def test_bootstrap_can_parse_welcome_url_and_extract_store_params(self):
    ...

def test_bootstrap_accepts_empty_welcome_menu_if_order_menu_later_exists(self):
    ...

def test_client_classifies_pending_payment_after_submit(self):
    ...

def test_client_rejects_submit_without_validated_payment_state(self):
    ...
```

- [ ] **Step 2: Run client tests to verify they fail**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -p 'test_client.py' -v`
Expected: FAIL with missing classes or methods

- [ ] **Step 3: Implement `client.py` with request wrappers and state classification**

Expose methods like:

```python
class CashierClient:
    def fetch_welcome(self, welcome_url: str) -> dict: ...
    def create_order(self, payload: dict) -> str: ...
    def fetch_order_menu(self, order_uuid: str) -> dict: ...
    def add_cart_item(self, order_uuid: str, payload: dict) -> dict: ...
    def submit_order(self, order_uuid: str) -> dict: ...
    def classify_payment_state(self, order_payload: dict, payment_payload: dict | None) -> str: ...
```

Keep transport injection simple so tests can stub responses without real network calls.

- [ ] **Step 4: Implement `bootstrap.py` with welcome parsing and precondition resolution**

Create helpers like:

```python
def parse_welcome_url(url: str) -> BootstrapContext: ...
def derive_order_creation_payload(welcome_payload: dict, preferred_serve_type: str | None = None) -> dict: ...
```

- [ ] **Step 5: Re-run client tests**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -p 'test_client.py' -v`
Expected: PASS

- [ ] **Step 6: Commit client and bootstrap work**

```bash
git add skills/cashier-order-cli/scripts/client.py skills/cashier-order-cli/scripts/bootstrap.py skills/cashier-order-cli/tests/test_client.py
git commit -m "feat: add cashier order cli protocol client"
```

### Task 4: Implement the CLI entrypoint and terminal interaction rules

**Files:**
- Create: `skills/cashier-order-cli/scripts/cashier_order.py`
- Create: `skills/cashier-order-cli/tests/test_cli.py`
- Modify: `skills/cashier-order-cli/scripts/bootstrap.py`
- Modify: `skills/cashier-order-cli/scripts/client.py`
- Modify: `skills/cashier-order-cli/scripts/menu.py`
- Modify: `skills/cashier-order-cli/scripts/resolver.py`

- [ ] **Step 1: Write failing CLI tests**

Cover:

```python
def test_dry_run_returns_resolution_without_submit(self):
    ...

def test_unique_result_does_not_prompt_for_input(self):
    ...

def test_ambiguous_result_prompts_once_and_returns_needs_input(self):
    ...

def test_json_output_is_machine_readable(self):
    ...
```

- [ ] **Step 2: Run CLI tests to verify they fail**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -p 'test_cli.py' -v`
Expected: FAIL with missing entrypoint behavior

- [ ] **Step 3: Implement `cashier_order.py` with `argparse` and dependency injection**

Include options:

```python
parser.add_argument("--welcome-url", required=True)
parser.add_argument("--prompt")
parser.add_argument("--target-total", type=int)
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--json", action="store_true")
parser.add_argument("--max-questions", type=int, default=1)
parser.add_argument("--payment", choices=("store", "online", "auto"), default="auto")
```

Add a `main(argv: list[str] | None = None) -> int` function so tests can call it directly.

- [ ] **Step 4: Keep prompting minimal and explicit**

Implement one-question behavior such as:

```python
if resolution.status == "needs-input":
    print(resolution.question)
    return 2
```

Do not loop forever; respect `--max-questions`.

- [ ] **Step 5: Re-run CLI tests**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -p 'test_cli.py' -v`
Expected: PASS

- [ ] **Step 6: Run the entire skill-local test suite**

Run: `python3 -m unittest discover -s skills/cashier-order-cli/tests -v`
Expected: PASS

- [ ] **Step 7: Commit the CLI entrypoint**

```bash
git add skills/cashier-order-cli/scripts/cashier_order.py skills/cashier-order-cli/tests/test_cli.py skills/cashier-order-cli/scripts/bootstrap.py skills/cashier-order-cli/scripts/client.py skills/cashier-order-cli/scripts/menu.py skills/cashier-order-cli/scripts/resolver.py
git commit -m "feat: add cashier order cli entrypoint"
```

## Chunk 3: Package The Skill And Integrate It Into Repo Metadata

### Task 5: Add the new installable skill package files

**Files:**
- Create: `skills/cashier-order-cli/SKILL.md`
- Create: `skills/cashier-order-cli/skill.yaml`
- Create: `skills/cashier-order-cli/CHANGELOG.md`
- Reference: `docs/superpowers/specs/2026-03-13-cashier-order-cli-design.md`

- [ ] **Step 1: Write `skills/cashier-order-cli/SKILL.md`**

Document:

```md
## When To Use
- Use when a Cashier site order should be placed through a bundled pure CLI.

## Commands
- python scripts/cashier_order.py --welcome-url <url> --prompt "幫我點最接近 50 元的炸蛋加白飯"

## Statuses
- menu-readable
- cart-created
- order-submitted
- order-pending-payment
- order-complete
- needs-input
- blocked
```

Also explain stop conditions, dry-run mode, and that `待付款` is not `order-complete`.

- [ ] **Step 2: Write `skills/cashier-order-cli/skill.yaml`**

Use metadata along these lines:

```yaml
slug: cashier-order-cli
name: Cashier Order CLI
version: 0.1.0
summary: Provides a pure CLI Cashier ordering workflow through direct HTTP requests.
description: Installs a runnable Cashier ordering CLI skill package with protocol discovery, order resolution, and direct request submission.
tags:
  - ordering
  - cashier
  - cli
  - api
platforms:
  - codex
install:
  method: script
  copy:
    source: skills/cashier-order-cli
entrypoint: SKILL.md
compatibility:
  minimum_host_version: "0.1"
  notes: Requires Python 3 and a host that can send direct HTTP requests to Cashier ordering endpoints.
provides:
  - cashier-order-cli
  - cashier-protocol-ordering
```

- [ ] **Step 3: Write `skills/cashier-order-cli/CHANGELOG.md`**

Start with:

```md
# Changelog

## 0.1.0

- Initial release of the pure CLI Cashier ordering skill.
```

- [ ] **Step 4: Run repo validation before regeneration**

Run: `python3 ./tools/validate_skills`
Expected: PASS

- [ ] **Step 5: Commit the new skill package source**

```bash
git add skills/cashier-order-cli
git commit -m "feat: add cashier order cli skill package"
```

## Chunk 4: Regenerate Outputs And Verify Installation

### Task 6: Regenerate generated docs and validate the package end-to-end

**Files:**
- Modify: `catalog.json`
- Modify: `docs/index.md`
- Modify: `docs/skills/cashier-order-cli.md`
- Modify: `README.md`
- Modify: `README.zh-TW.md`

- [ ] **Step 1: Rebuild generated outputs**

Run: `python3 ./tools/build_catalog`
Expected: new `cashier-order-cli` entries appear in generated catalog, docs index, and READMEs

- [ ] **Step 2: Verify generated doc content**

Run: `sed -n '1,240p' docs/skills/cashier-order-cli.md`
Expected: installation instructions, examples, and compatibility notes mention the CLI workflow and bundled scripts

- [ ] **Step 3: Validate generated freshness**

Run: `python3 ./tools/validate_skills --check-generated`
Expected: PASS

- [ ] **Step 4: Run the full repo test suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

- [ ] **Step 5: Verify installer behavior with the real new skill**

Run: `tmpdir=$(mktemp -d) && python3 ./tools/install_skill cashier-order-cli --target codex --target-root "$tmpdir" && find "$tmpdir/cashier-order-cli" -maxdepth 3 -type f | sort`
Expected: output includes `SKILL.md`, `skill.yaml`, `CHANGELOG.md`, `scripts/cashier_order.py`, `scripts/bootstrap.py`, `scripts/client.py`, `scripts/menu.py`, `scripts/resolver.py`, and skill-local test files

- [ ] **Step 6: Manually inspect the CLI help text**

Run: `python3 skills/cashier-order-cli/scripts/cashier_order.py --help`
Expected: options include `--welcome-url`, `--prompt`, `--target-total`, `--dry-run`, `--json`, `--max-questions`, and `--payment`

- [ ] **Step 7: Commit regenerated outputs**

```bash
git add catalog.json docs/index.md docs/skills/cashier-order-cli.md README.md README.zh-TW.md
git commit -m "docs: generate cashier order cli catalog outputs"
```

- [ ] **Step 8: Review and verification handoff**

Run:

```bash
git diff --stat origin/main...HEAD
python3 -m unittest discover -s tests -v
python3 ./tools/validate_skills --check-generated
```

Expected: only the new skill, its tests, repo-level tests, and generated outputs appear; all verification commands pass

If no subagent reviewer is available in the harness, perform an explicit manual diff review and record that limitation in the implementation handoff before merge.
