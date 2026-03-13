# Cashier Order CLI Skill Design

## Goal

Create a new Codex skill package named `cashier-order-cli` that provides a pure CLI workflow for ordering from Cashier-style online ordering sites without relying on an interactive browser session.

The skill should support direct command-line execution, protocol discovery, menu loading, item resolution, cart creation, and order submission through HTTP/background requests. It should ask the user questions only when the CLI cannot uniquely determine the intended order.

## Relationship To Existing Skills

This skill is intended to coexist with `ordering-cashier-tw`.

- `ordering-cashier-tw` remains the protocol and workflow guidance skill
- `cashier-order-cli` becomes the executable pure CLI companion skill

The new skill should not replace the existing one. It should build on the same domain knowledge but deliver a runnable tool.

## User Intent

The user wants:

- a pure CLI version
- natural-language or concise parameter input
- automatic decision-making whenever the requested order can be determined uniquely
- interactive clarification only when the tool cannot proceed safely

The CLI must classify order state precisely and avoid claiming completion when the order is only pending payment.

## Non-Goals

- replacing the repository-level `skill_catalog` CLI
- creating a generic ordering framework for arbitrary non-Cashier websites
- depending on Playwright or interactive browser automation as the primary path
- silently guessing through unresolved ambiguities
- claiming full success on store-payment flows that are still waiting for payment

## Recommended Approach

Build the skill as a small tool package with focused modules:

1. bootstrap and order creation
2. HTTP client for Cashier endpoints
3. menu normalization and search
4. natural-language/argument resolution
5. CLI entrypoint

This approach is preferred over a single large script because it keeps protocol handling, menu search, and CLI interaction testable and easier to extend to other Cashier stores later.

## Architecture

The new skill package should include the following source layout:

- `skills/cashier-order-cli/SKILL.md`
- `skills/cashier-order-cli/skill.yaml`
- `skills/cashier-order-cli/CHANGELOG.md`
- `skills/cashier-order-cli/scripts/cashier_order.py`
- `skills/cashier-order-cli/scripts/bootstrap.py`
- `skills/cashier-order-cli/scripts/client.py`
- `skills/cashier-order-cli/scripts/menu.py`
- `skills/cashier-order-cli/scripts/resolver.py`
- `skills/cashier-order-cli/tests/test_resolver.py`
- `skills/cashier-order-cli/tests/test_client.py`
- `skills/cashier-order-cli/tests/test_cli.py`

### 1. Bootstrap Module

Responsibility:

- parse the welcome URL
- derive store identifiers and custom UUIDs
- fetch the welcome payload
- detect required preconditions such as order time and serve type
- create an order and return the active order UUID

This module should be responsible for converting a store entry URL into an actionable order context.

### 2. Client Module

Responsibility:

- wrap Cashier HTTP requests
- manage headers, cookies, query params, and order-scoped routing
- expose methods such as:
  - `fetch_welcome()`
  - `create_order()`
  - `fetch_order_menu()`
  - `add_cart_item()`
  - `submit_order()`
  - `fetch_payment_state()`

This module should isolate network details from resolution logic.

### 3. Menu Module

Responsibility:

- normalize menu payloads into a stable in-memory representation
- expose utilities for:
  - item lookup
  - sold-out filtering
  - closest-total selection
  - category-aware searches
  - price-based ranking

This module should handle the fact that welcome payloads may be empty while order-scoped menu payloads are populated later.

### 4. Resolver Module

Responsibility:

- parse natural-language and structured CLI arguments into order intent
- resolve item names, quantities, and target total constraints against the normalized menu
- detect when the result is uniquely determined
- emit a minimal clarification prompt when not uniquely determined

Examples of ambiguity:

- `蛋` could mean `雞蛋` or `炸蛋`
- a target total may yield multiple equally close valid combinations

### 5. CLI Entrypoint

Responsibility:

- parse arguments and prompt text
- execute the bootstrap, menu, resolver, and client flow
- print clear terminal output
- ask follow-up questions only when necessary
- optionally emit machine-readable JSON

## CLI Interface

The CLI should support both natural-language mode and structured argument mode.

### Natural-Language Mode

Examples:

- `cashier-order "幫我點最接近 50 元的炸蛋加白飯"`
- `cashier-order "幫我點 10 元的一張單"`

### Structured Mode

Examples:

- `cashier-order --welcome-url <url> --target-total 50 --item 炸蛋 --addon 白飯`
- `cashier-order --welcome-url <url> --closest-total 10`

Suggested options:

- `--welcome-url`
- `--prompt`
- `--target-total`
- `--dry-run`
- `--json`
- `--max-questions`
- `--payment store|online|auto`

## Interaction Rules

The default interaction policy should be:

- automatically detect the protocol
- automatically load the menu
- automatically resolve the order whenever a unique valid result exists
- only ask a question when the tool cannot safely continue

Examples:

- if `炸蛋 + 白飯` is the only intended combination, proceed without asking
- if `蛋` is ambiguous between `雞蛋` and `炸蛋`, ask one focused question

## Status Classification

The CLI should classify outcomes using explicit states:

- `menu-readable`
- `cart-created`
- `order-submitted`
- `order-pending-payment`
- `order-complete`
- `needs-input`
- `blocked`

For store-payment flows, `order-pending-payment` must be reported instead of `order-complete` unless the site explicitly confirms payment completion.

## Verified Cashier Behavior To Support

The CLI must account for behavior already verified in the Night store flow:

- the welcome payload may expose an empty menu initially
- selecting order-time preconditions can still yield a valid order UUID and a populated order-scoped menu
- order-scoped APIs are the authoritative menu source once an order exists
- `cart-items` updates must be verified through cart totals and item presence
- `submit` may successfully create an order that is still in `待付款`

This behavior should inform both client logic and tests.

## Failure And Stop Conditions

The CLI must stop and report `blocked` or `needs-input` when:

- it cannot create or recover an order UUID
- the menu remains empty and no further valid preconditions can be derived
- login, OTP, CAPTCHA, or equivalent identity checks are required
- an item is sold out
- request parameters cannot be reconstructed reliably
- the ambiguity count exceeds `--max-questions`
- submit succeeds but no order/payment state can be validated afterward

The CLI must not:

- guess through unresolved ambiguity
- treat a transient UI message as final truth
- claim success based only on HTTP 200
- report `order-complete` when the site still says `待付款`

## Testing Strategy

Testing should cover three layers.

### 1. Resolver Tests

Examples:

- `蛋` produces an ambiguity result
- `炸蛋加白飯 50 元` resolves to a 45-dollar combination
- `最接近 10 元` resolves to a 10-dollar item when present

### 2. Client And Menu Tests

Use fixture payloads to verify:

- empty welcome menu followed by populated order menu
- cart totals update after adding items
- submit transitions into an order/payment state
- `待付款` is classified as `order-pending-payment`

### 3. CLI Tests

Examples:

- `--dry-run` does not submit
- unique orders do not ask questions
- ambiguous orders do ask questions
- `--json` emits stable machine-readable results

## Deliverables

Implementation should produce:

- a new installable skill package at `skills/cashier-order-cli/`
- executable CLI scripts under `skills/cashier-order-cli/scripts/`
- tests under `skills/cashier-order-cli/tests/`
- generated repository outputs:
  - `docs/skills/cashier-order-cli.md`
  - updated `catalog.json`
  - updated `docs/index.md`
  - updated `README.md`
  - updated `README.zh-TW.md`

## Open Assumptions

- the first supported target is the Cashier-style ordering flow already validated against Night
- the tool should be structured for reuse on similar Cashier stores later
- exact payment completion still depends on the site-provided payment state and may require a later phase for online payment automation
