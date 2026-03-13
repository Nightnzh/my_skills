# Ordering Cashier TW Skill Design

## Goal

Create a Codex skill that can take a single natural-language ordering request and complete the full ordering flow on the Taiwan Cashier online ordering site at:

`https://indev-webapp.cashier.tw/online/store/d1beb4d0-420b-4198-a802-28141ef7ba3a/welcome?customUuid=b3c22cc0-c3b9-4b5f-b6bb-a2d1de47de43&welcomeLocale=zh-TW`

The skill should use HTTP or background requests rather than an interactive browser session. It should be able to proceed through protocol discovery, menu loading, cart validation, and final order submission. It should stop only when the site requires information or validation that cannot be safely inferred or reconstructed.

## User Intent

The user wants a reusable skill for direct ordering, not a one-off script. The expected interaction style is:

- user gives one natural-language ordering command
- the skill parses the order
- the skill maps the request against the live menu on the site
- the skill asks only when a choice cannot be uniquely resolved
- the skill can submit the order directly when all required information is available
- the skill should avoid opening an interactive browser and instead operate through HTTP/background request flows when the protocol can be derived

## Non-Goals

- building a generic ordering framework for arbitrary sites
- persisting a long-term cached menu across sessions
- auto-substituting sold-out items
- bypassing login, OTP, CAPTCHA, or other explicit verification gates
- guessing missing required fields when multiple valid choices remain
- relying on interactive browser clicks as the primary execution path

## Recommended Approach

Use a two-phase workflow:

1. Extract bootstrap configuration and derive the live request protocol used by the site.
2. Capture the live menu and normalize it into a temporary structured model for the current session.
3. Resolve the user's natural-language request against that model before performing direct HTTP/background requests.

This approach is preferred over UI-only automation because it keeps the skill compatible with the user's new requirement, grounds decisions in the actual live protocol, and makes failures easier to explain and validate.

## Architecture

The skill should describe six internal modules with clear boundaries.

### 1. Bootstrap Extractor

Responsibility:

- fetch the welcome page and related static assets needed for protocol discovery
- extract store identifiers, locale data, config objects, bundle paths, API base URLs, and request bootstrap values
- provide raw initialization data for deeper protocol analysis

This module does not place orders or interpret user intent.

### 2. Protocol Analyzer

Responsibility:

- analyze HTML, scripts, static strings, and API responses to derive the request protocol
- identify menu, cart, and order-submission endpoints
- determine required headers, cookies, tokens, nonces, timestamps, and payload shapes
- infer which returned fields must be reused in later requests

This module does not decide what the user wants to order. It determines how the site expects to be called.

### 3. Menu Snapshot

Responsibility:

- call the derived live menu endpoints
- inspect categories, items, option groups, sold-out flags, and pricing data
- build a structured snapshot of what is orderable right now

Captured data should include, when available:

- category names
- item names
- prices
- sold-out status
- option groups
- whether each option group is required
- candidate values for each group
- quantity controls
- free-text note fields or constraints

### 4. Order Parser

Responsibility:

- parse one natural-language ordering request into a structured intent

Expected fields per item:

- `name`
- `quantity`
- `size`
- `temperature`
- `sweetness`
- `toppings`
- `notes`

This module interprets language only. It does not decide whether the requested configuration is actually available on the live site.

### 5. Resolver

Responsibility:

- compare parsed order intent against the menu snapshot
- determine whether each requested field has exactly one valid match
- emit either executable actions or a minimal clarification question

Rules:

- if an item or option maps to exactly one live choice, proceed automatically
- if multiple valid matches remain, stop and ask one focused question
- if a required option is missing, ask only for that missing field
- if an item is sold out, stop immediately and report it

This module is the main safety boundary between language interpretation and protocol execution.

### 6. Request Executor

Responsibility:

- perform the resolved HTTP/background requests against the site
- verify after each major interaction that the expected state change occurred

Execution checks should include:

- protocol bootstrap completed successfully
- expected request prerequisites were attached
- item was added to cart
- cart reflects the intended quantity and price
- final submission reached a recognizable success state

## End-to-End Flow

1. Fetch the welcome URL and bootstrap resources.
2. Extract identifiers, config, and request bootstrap data.
3. Derive the live request protocol for menu, cart, and order submission.
4. Check whether ordering can proceed.
5. Build a live menu snapshot for the current session.
6. Parse the user's natural-language request into structured intent.
7. Resolve intent against the menu snapshot.
8. If resolution is incomplete, ask a single minimal clarification question.
9. Execute the order through direct requests.
10. Validate cart and intermediate state after each item.
11. Submit the order if no unresolved issues remain.
12. Confirm success only if the site shows a recognizable completion state.

## Safety And Stop Conditions

The skill is allowed to submit the order directly, but only inside explicit boundaries.

The skill must stop immediately when any of the following occurs:

- the site requires login or membership state that is not already satisfied
- the site requests OTP, CAPTCHA, SMS verification, or any manual identity check
- a required field cannot be uniquely inferred from the menu and the request
- an item is sold out
- the menu, cart, or order API cannot be identified with sufficient confidence
- required request parameters depend on logic that cannot be reconstructed reliably
- the protocol requires a browser-only execution primitive that cannot be replaced by direct requests
- the final page requires additional data that the user did not provide

The skill must not:

- auto-replace a sold-out item with a similar item
- invent missing options
- continue after a failed request or unverifiable response without detecting and reporting the failure

## Clarification Strategy

Clarification should be minimal and sequential.

Examples:

- "你要的是紅茶拿鐵還是英式紅茶？"
- "這個品項需要選大小杯，你要大杯還是中杯？"
- "這個品項必須選甜度，你要全糖、半糖還是無糖？"

The skill should not ask compound questions when only one field blocks progress.

## Failure Handling

Failure policy is conservative:

- stop immediately on ambiguity that cannot be uniquely resolved
- stop immediately on sold-out items
- stop immediately on login or verification requirements
- stop immediately when protocol derivation becomes unreliable or unverifiable

When stopping, the skill should report:

- where it failed
- why it failed
- what single next input or manual step would unblock progress, if applicable

## Verification Strategy

Verification should happen in three layers.

### Preflight Verification

- confirm the welcome page and bootstrap assets load
- confirm the store appears open and ordering is available
- confirm protocol discovery yields interpretable menu access

### In-Flow Verification

- confirm each configured item is actually added to cart
- confirm quantity and pricing update as expected through response data or cart queries
- confirm required options remain attached in the request/response model

### Final Verification

- confirm final submission produces a recognizable success page, order number, or completion message
- never claim success based only on an HTTP 200 or raw request completion

## Skill Deliverables

The implementation phase should add at least:

- `skills/ordering-cashier-tw/SKILL.md`
- `skills/ordering-cashier-tw/skill.yaml`
- `skills/ordering-cashier-tw/CHANGELOG.md`
- `docs/skills/ordering-cashier-tw.md`

Suggested examples for the skill:

- `幫我點大杯紅茶拿鐵無糖少冰 2 杯`
- `幫我點雞腿便當加蛋，不要菜脯`
- `幫我點兩杯珍奶，一杯半糖少冰，一杯無糖去冰`

## Testing Expectations

This is a workflow-oriented skill, so validation should focus on correctness of guidance and packaging:

- metadata validation for `skill.yaml`
- generated catalog and docs staying in sync
- skill examples covering both direct execution and clarification cases
- explicit documentation of protocol discovery, stop conditions, and safety boundaries

If browser automation examples or helper scripts are later added, they should be validated separately from the base skill packaging.

## Open Execution Assumptions

- the site may require login, payment state, or stored profile data; the skill should detect this at runtime rather than assume a guest flow
- the menu is dynamic and should be treated as live session data, not static documentation
- final order submission is in scope only when the site exposes a request path that can be reconstructed and validated without an interactive browser session
