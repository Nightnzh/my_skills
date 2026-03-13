---
name: "ordering-cashier-tw"
description: "Use when the task is to place a natural-language order on the Taiwan Cashier online ordering site through protocol discovery and direct HTTP/background requests."
---

# Ordering Cashier TW

Use this skill when the user wants to place an order on the Taiwan Cashier online ordering site with one natural-language request and expects the workflow to continue through order creation without relying on an interactive browser session. Final completion depends on the payment state returned by the site, not just a submit response.

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
4. Check whether ordering can proceed after the page and protocol stabilize.
5. If the welcome payload returns an empty menu, satisfy required preconditions such as order time or serve type before stopping.
6. Build a live menu snapshot for the current session from direct requests.
7. Parse the user's request into structured fields such as item name, quantity, size, sweetness, temperature, toppings, and notes.
8. Resolve each requested field against the live menu snapshot.
9. If any required field is missing or multiple choices remain, ask one focused clarification question.
10. Execute direct HTTP/background requests for cart and order submission.
11. Verify cart, order, and payment state from responses, not UI state.

## Protocol Discovery Workflow

For Cashier-style stores, prefer this request sequence:

1. `GET /online/v2/store/<store-id>/welcome?customUuid=<custom-uuid>`
2. If the store is orderable, satisfy required preconditions such as order time and serve type.
3. `POST /online/v2/store/<store-id>/welcome`
4. Read the returned or redirected `order UUID`.
5. Query order-scoped endpoints such as:
   - `GET /online/v2/order/<order-uuid>`
   - `GET /online/v2/order/<order-uuid>/menu`
   - `GET /online/menu/order/<order-uuid>/info`
   - `GET /online/menu/order/<order-uuid>/detail`
   - `GET /online/menu/order/<order-uuid>/customer-info`
   - `GET /online/menu/order/<order-uuid>/menu`
6. If needed, query store-scoped endpoints such as:
   - `GET /online/menu/store/<store-id>/detail?serveType=<serve-type>`
   - `GET /online/menu/store/<store-id>/init-data?serveType=<serve-type>&country=<country>`
7. Add items with:
   - `POST /online/menu/order/<order-uuid>/cart-items?webUrlPrefix=<prefix>`
8. Submit the order with:
   - `POST /online/menu/order/<order-uuid>/submit?webUrlPrefix=<prefix>`
9. Validate the created order with:
   - `GET /online/v2/order/<new-order-uuid>`
   - `GET /online/v2/order/<new-order-uuid>/payment`

Treat the `order UUID` as the primary correlation key for all later requests.

## Verified Cashier Flow

The following path was verified against the Night store:

- welcome page:
  - `https://indev-webapp.cashier.tw/online/store/d1beb4d0-420b-4198-a802-28141ef7ba3a/welcome?customUuid=b3c22cc0-c3b9-4b5f-b6bb-a2d1de47de43&welcomeLocale=zh-TW`
- welcome API:
  - `GET https://indev-api.cashier.tw/online/v2/store/d1beb4d0-420b-4198-a802-28141ef7ba3a/welcome?customUuid=b3c22cc0-c3b9-4b5f-b6bb-a2d1de47de43`
- order bootstrap:
  - select `儘快取餐`
  - `POST https://indev-api.cashier.tw/online/v2/store/d1beb4d0-420b-4198-a802-28141ef7ba3a/welcome`
- order-scoped APIs observed:
  - `GET https://indev-api.cashier.tw/online/v2/order/<order-uuid>`
  - `GET https://indev-api.cashier.tw/online/v2/order/<order-uuid>/menu`
  - `GET https://indev-api.cashier.tw/online/menu/order/<order-uuid>/info`
  - `GET https://indev-api.cashier.tw/online/menu/order/<order-uuid>/detail`
  - `GET https://indev-api.cashier.tw/online/menu/order/<order-uuid>/customer-info`
  - `GET https://indev-api.cashier.tw/online/menu/order/<order-uuid>/menu`
- cart item creation:
  - `POST https://indev-api.cashier.tw/online/menu/order/<order-uuid>/cart-items?webUrlPrefix=indev`
- submit:
  - `POST https://indev-api.cashier.tw/online/menu/order/<order-uuid>/submit?webUrlPrefix=indev`
- post-submit validation:
  - `GET https://indev-api.cashier.tw/online/v2/order/<new-order-uuid>`
  - `GET https://indev-api.cashier.tw/online/v2/order/<new-order-uuid>/payment`

Observed behavior from this verified flow:

- the initial welcome response may expose an empty `webMenuVos` array
- an empty welcome menu is not enough to conclude the store is unavailable
- selecting required preconditions can still produce a valid order and non-empty order-scoped menu APIs
- a successful submit can still land in a payment flow with status `待付款`
- `店內付款` creates an order that is submitted but not fully paid

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
- do not treat a transient page message as final store state without checking stabilized page state and API availability
- do not stop only because the welcome payload exposes an empty menu; first check whether the order flow requires preconditions
- do not auto-substitute items
- do not invent missing options
- do not claim success based only on HTTP 200 or raw request completion
- do not treat `submit` as fully complete until the resulting order/payment status is classified

## Status Classification

Use these states distinctly:

- `menu-readable`: the store is reachable and the active menu can be read
- `cart-created`: one or more items are present in the active order/cart
- `order-submitted`: the submit request completed and a new order exists
- `order-pending-payment`: the order exists but the site still reports `待付款` or equivalent
- `order-complete`: the site reports a paid/completed state

For store-payment flows, report `order-pending-payment` unless the site explicitly confirms payment completion.

## Failure Handling

When stopping, report:

- where the flow failed
- why it failed
- what single next input or manual action would unblock it, if known

Common examples:

- welcome shows a temporary blocking message but order/menu APIs are still unresolved
- submit succeeds but the payment API still reports `待付款`
- welcome menu is empty until order-time preconditions are selected

## Verification

Verify at three levels:

- preflight: the welcome page and bootstrap assets load, the store appears open, and protocol discovery yields interpretable menu access
- in-flow: each configured item is added to the cart with expected quantity and pricing in response data or cart queries
- final: submission reaches a recognizable order state such as an order ID, payment record, pending-payment state, or equivalent success payload

Minimum completion checklist:

- confirm an `order UUID` exists before reading order-scoped menu APIs
- confirm the active menu is non-empty before matching the user's requested item
- confirm cart quantity and total changed after `cart-items`
- confirm `submit` created a new order or moved the existing order to a new state
- confirm whether the resulting order is `待付款`, `已付款`, or otherwise complete

## Examples

- `幫我點大杯紅茶拿鐵無糖少冰 2 杯`
- `幫我點雞腿便當加蛋，不要菜脯`
- `幫我點兩杯珍奶，一杯半糖少冰，一杯無糖去冰`
