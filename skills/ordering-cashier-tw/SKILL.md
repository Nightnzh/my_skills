---
name: "ordering-cashier-tw"
description: "Use when the task is to place a natural-language order on the Taiwan Cashier online ordering site, resolving live menu options before submitting the order."
---

# Ordering Cashier TW

Use this skill when the user wants to place an order on the Taiwan Cashier online ordering site with one natural-language request and expects the workflow to continue through final submission when the site does not require extra manual verification.

Target entry URL:

`https://indev-webapp.cashier.tw/online/store/d1beb4d0-420b-4198-a802-28141ef7ba3a/welcome?customUuid=b3c22cc0-c3b9-4b5f-b6bb-a2d1de47de43&welcomeLocale=zh-TW`

## When To Use

- the user wants to order from the specific Cashier Taiwan store above
- the user provides one natural-language ordering request
- the task requires resolving live menu choices before clicking through the site
- final order submission is in scope if the site does not require extra manual verification

## Workflow

1. Open the welcome URL and verify ordering can proceed.
2. Build a live menu snapshot for the current session from the site itself.
3. Parse the user's request into structured fields such as item name, quantity, size, sweetness, temperature, toppings, and notes.
4. Resolve each requested field against the live menu snapshot.
5. If the request maps to exactly one valid choice, continue automatically.
6. If any required field is missing or multiple choices remain, ask one focused clarification question.
7. Execute the site interactions and validate cart state after each item.
8. Submit the order only when no unresolved issues remain.
9. Report success only if the site reaches a recognizable completion state.

## Resolution Rules

- Prefer the current page state over assumptions or stale knowledge.
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
- stop when a required field cannot be uniquely resolved from the request and live menu
- stop when the UI flow diverges or relevant controls cannot be located reliably
- do not auto-substitute items
- do not invent missing options
- do not claim success without a recognizable completion state

## Failure Handling

When stopping, report:

- where the flow failed
- why it failed
- what single next input or manual action would unblock it, if known

## Verification

Verify at three levels:

- preflight: the welcome page loads, the store appears open, and ordering can enter the menu
- in-flow: each configured item is added to the cart with expected quantity and visible pricing
- final: submission reaches a recognizable success state such as an order completion page or confirmation message

## Examples

- `幫我點大杯紅茶拿鐵無糖少冰 2 杯`
- `幫我點雞腿便當加蛋，不要菜脯`
- `幫我點兩杯珍奶，一杯半糖少冰，一杯無糖去冰`
