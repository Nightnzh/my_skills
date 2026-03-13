---
name: "ordering-cashier-tw"
description: "Use when the task is to place a natural-language order on the Taiwan Cashier online ordering site through protocol discovery and direct HTTP/background requests."
---

# Ordering Cashier TW

Use this skill when the user wants to place an order on the Taiwan Cashier online ordering site with one natural-language request and expects the workflow to continue through final submission without relying on an interactive browser session.

Target entry URL:

`https://indev-webapp.cashier.tw/online/store/d1beb4d0-420b-4198-a802-28141ef7ba3a/welcome?customUuid=b3c22cc0-c3b9-4b5f-b6bb-a2d1de47de43&welcomeLocale=zh-TW`

## When To Use

- the user wants to order from the specific Cashier Taiwan store above
- the user provides one natural-language ordering request
- the task requires deriving the live request protocol before placing the order
- final order submission is in scope if the site does not require extra manual verification

## Workflow

1. Fetch the welcome URL and bootstrap resources.
2. Extract identifiers, config, and request bootstrap data.
3. Derive the live request protocol for menu, cart, and order submission.
4. Check whether ordering can proceed.
5. Build a live menu snapshot for the current session from direct requests.
6. Parse the user's request into structured fields such as item name, quantity, size, sweetness, temperature, toppings, and notes.
7. Resolve each requested field against the live menu snapshot.
8. If any required field is missing or multiple choices remain, ask one focused clarification question.
9. Execute direct HTTP/background requests for cart and order submission.
10. Verify cart and final order state from responses, not UI state.

## Resolution Rules

- Prefer current live responses over assumptions or stale knowledge.
- Only auto-select when the user's request maps to one valid live choice.
- When clarification is required, ask only the smallest question that unblocks progress.
- Keep language operational and direct.

Expected structured fields:

- `name`
- `quantity`
- `size`
- `temperature`
- `sweetness`
- `toppings`
- `notes`

## Clarification Examples

- `你要的是紅茶拿鐵還是英式紅茶？`
- `這個品項需要選大小杯，你要大杯還是中杯？`
- `這個品項必須選甜度，你要全糖、半糖還是無糖？`

Do not ask multiple unrelated questions at once when only one field blocks progress.

## Guardrails

- stop on sold-out items
- stop on login, OTP, CAPTCHA, SMS verification, or other identity checks
- stop when menu, cart, or order APIs cannot be identified with sufficient confidence
- stop when required request parameters cannot be reconstructed reliably
- stop when a required field cannot be uniquely resolved from the request and live menu
- stop when the protocol appears to require a browser-only execution primitive
- do not auto-substitute items
- do not invent missing options
- do not claim success based only on HTTP 200 or raw request completion

## Failure Handling

When stopping, report:

- where the flow failed
- why it failed
- what single next input or manual action would unblock it, if known

## Verification

Verify at three levels:

- preflight: the welcome page and bootstrap assets load, the store appears open, and protocol discovery yields interpretable menu access
- in-flow: each configured item is added to the cart with expected quantity and pricing in response data or cart queries
- final: submission reaches a recognizable success state such as an order ID, completion message, or equivalent success payload

## Examples

- `幫我點大杯紅茶拿鐵無糖少冰 2 杯`
- `幫我點雞腿便當加蛋，不要菜脯`
- `幫我點兩杯珍奶，一杯半糖少冰，一杯無糖去冰`
