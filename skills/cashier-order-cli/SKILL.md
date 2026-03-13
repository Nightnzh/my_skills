# Cashier Order CLI

Use this skill when you want a pure CLI workflow for ordering from Cashier-style online ordering sites without opening an interactive browser.

## When To Use

- You have a Cashier welcome URL and want to place an order through terminal commands.
- You want the tool to auto-resolve the order whenever there is a unique answer.
- You only want follow-up questions when the order cannot be determined safely.

## Command

Run the bundled script from this skill package:

```bash
python scripts/cashier_order.py --welcome-url "<welcome-url>" --prompt "幫我點最接近 50 元的炸蛋加白飯"
```

Structured arguments are also supported:

```bash
python scripts/cashier_order.py --welcome-url "<welcome-url>" --target-total 50 --item 炸蛋 --item 白飯
```

## Statuses

- `menu-readable`
- `cart-created`
- `order-submitted`
- `order-pending-payment`
- `order-complete`
- `needs-input`
- `blocked`

`order-pending-payment` means the order was created but payment is still outstanding. Do not treat it as complete.

## Workflow

1. Parse the welcome URL and bootstrap order context.
2. Discover or reuse the request protocol needed for the store.
3. Load the live menu for the active order.
4. Resolve natural-language or structured order input.
5. Ask one focused clarification question only if the result is ambiguous.
6. Submit the resolved order through direct HTTP requests, or stop earlier in `--dry-run` mode.
7. Validate the post-submit payment state before reporting completion.

## Options

- `--welcome-url`
- `--prompt`
- `--target-total`
- `--item`
- `--dry-run`
- `--json`
- `--max-questions`
- `--payment store|online|auto`

## Guardrails

- Do not guess through unresolved ambiguity.
- Do not treat a transient page message as final truth.
- Do not report success based only on HTTP 200.
- Stop if login, OTP, CAPTCHA, or equivalent identity checks are required.
- Stop if order creation fails, the menu remains unavailable, or payment state cannot be validated.

## Notes

- The bundled CLI can be tested locally with the files in `tests/`.
- The existing `ordering-cashier-tw` skill remains the protocol-guidance companion for this executable skill.
