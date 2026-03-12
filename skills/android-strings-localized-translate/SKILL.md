---
name: "android-strings-localized-translate"
description: "Use when the task is to fill missing translations for `app/src/main/res/values/strings_localized.xml` into the 9 non-English `values-*` locale files, while preserving existing translations and forcing all 10 `strings_localized.xml` files to match the base file's line layout exactly."
---

# Android Strings Localized Translate

Use this skill when the repo contains Android resource files under `app/src/main/res/values*` and the user wants to complete the 9 non-English `strings_localized.xml` translations from the base English file.

This skill is specific to:

- base file: `app/src/main/res/values/strings_localized.xml`
- locale files:
  - `app/src/main/res/values-de-rDE/strings_localized.xml`
  - `app/src/main/res/values-fr/strings_localized.xml`
  - `app/src/main/res/values-ja/strings_localized.xml`
  - `app/src/main/res/values-ko/strings_localized.xml`
  - `app/src/main/res/values-ms/strings_localized.xml`
  - `app/src/main/res/values-th/strings_localized.xml`
  - `app/src/main/res/values-vi/strings_localized.xml`
  - `app/src/main/res/values-zh-rCN/strings_localized.xml`
  - `app/src/main/res/values-zh-rTW/strings_localized.xml`

## Requirements

- Only translate missing keys.
- Never overwrite an existing translated value.
- Rebuild each locale file using the base file as the exact line template.
- After completion, all 10 files must have:
  - identical key order
  - identical comment placement
  - identical blank-line placement
  - identical total line count
- Preserve placeholders and escapes exactly:
  - `%s`, `%d`, `%1$s`
  - `\n`
  - `\"`, `\'`
  - XML escapes such as `&quot;`

## Workflow

### 1. Inspect missing keys

Run:

```bash
python3 "$CODEX_HOME/skills/android-strings-localized-translate/scripts/sync_strings_localized.py" \
  --repo-root /absolute/path/to/repo \
  --report
```

This prints JSON containing missing keys, extra keys, and line-count facts per locale.

### 2. Translate only missing keys

Create a JSON file containing only the missing translations. Schema:

```json
{
  "values-ja": {
    "some_key": "translated text"
  },
  "values-zh-rTW": {
    "some_other_key": "translated text"
  }
}
```

Rules for translation:

- Translate from the base English text in `values/strings_localized.xml`.
- Keep tone appropriate for kiosk UI text: short, direct, operational.
- Preserve placeholders and escaping exactly.
- If the base line contains English-only product or brand wording, keep proper nouns unchanged unless the locale already localizes that concept elsewhere.
- Output only the XML inner text value, not full `<string>` lines.

### 3. Rebuild locale files

Run:

```bash
python3 "$CODEX_HOME/skills/android-strings-localized-translate/scripts/sync_strings_localized.py" \
  --repo-root /absolute/path/to/repo \
  --translations-file /absolute/path/to/translations.json \
  --write
```

This keeps existing translations, fills only missing keys, and rewrites all 9 locale files so their structure matches the base file exactly.

### 4. Validate

Run:

```bash
python3 "$CODEX_HOME/skills/android-strings-localized-translate/scripts/validate_strings_localized.py" \
  --repo-root /absolute/path/to/repo
```

Validation must pass before the task is considered complete:

```bash
python3 "$CODEX_HOME/skills/android-strings-localized-translate/scripts/validate_strings_localized.py" \
  --repo-root /absolute/path/to/repo
```

If you also want to audit pre-existing placeholder issues without rewriting existing translations, run:

```bash
python3 "$CODEX_HOME/skills/android-strings-localized-translate/scripts/validate_strings_localized.py" \
  --repo-root /absolute/path/to/repo \
  --check-placeholders
```

## Guardrails

- Do not translate the base English file.
- Do not add or remove keys.
- Do not reorder keys independently from the base file.
- Do not preserve locale-specific comment formatting; the base file's layout is the source of truth.
- If a translation JSON omits some missing keys, stop with an error instead of writing partial output.
- For newly added translations, placeholder tokens must match the base exactly.
- Pre-existing placeholder mismatches should be reported, not silently changed, because this skill does not rewrite existing translated values.
