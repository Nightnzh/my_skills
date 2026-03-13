# Ordering Cashier TW

Adds a full-flow ordering skill package that derives live request protocols, resolves menu options, and submits orders through direct requests with strict stop conditions.

## Metadata

- Slug: `ordering-cashier-tw`
- Version: `0.1.2`
- Status: `active`
- Platforms: codex
- Entry point: `SKILL.md`

## Installation

- Skill URL: `https://github.com/Nightnzh/my_skills/tree/main/skills/ordering-cashier-tw`
- Prompt: `請安裝這個 skill：https://github.com/Nightnzh/my_skills/tree/main/skills/ordering-cashier-tw`
- Prompt (EN): `install https://github.com/Nightnzh/my_skills/tree/main/skills/ordering-cashier-tw skill`

## Usage

Read `SKILL.md` inside `skills/ordering-cashier-tw` after installation.

## Examples

- `幫我點大杯紅茶拿鐵無糖少冰 2 杯`: Resolves the live menu through direct requests and submits the order when no clarification is needed.
- `幫我點兩杯珍奶，一杯半糖少冰，一杯無糖去冰`: Parses multiple items, resolves each against the live menu, and stops if any required option or protocol step is ambiguous.

## Dependencies

- Depends on: None

## Changelog

- See `skills/ordering-cashier-tw/CHANGELOG.md`
