# Cashier Order CLI

Installs a runnable Cashier ordering CLI skill package with protocol discovery, order resolution, and direct request submission.

## Metadata

- Slug: `cashier-order-cli`
- Version: `0.1.0`
- Status: `active`
- Platforms: codex
- Entry point: `SKILL.md`

## Installation

- Skill URL: `https://github.com/Nightnzh/my_skills/tree/main/skills/cashier-order-cli`
- Prompt: `請安裝這個 skill：https://github.com/Nightnzh/my_skills/tree/main/skills/cashier-order-cli`
- Prompt (EN): `install https://github.com/Nightnzh/my_skills/tree/main/skills/cashier-order-cli skill`

## Usage

Read `SKILL.md` inside `skills/cashier-order-cli` after installation.

## Examples

- `cashier-order "幫我點最接近 50 元的炸蛋加白飯"`: Resolves a unique combination and submits it without asking follow-up questions.
- `cashier-order --welcome-url "<url>" --target-total 10 --dry-run`: Finds the closest available combination and prints the result without submitting an order.

## Dependencies

- Depends on: None

## Changelog

- See `skills/cashier-order-cli/CHANGELOG.md`
