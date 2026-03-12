#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


TARGET_LOCALES = [
    "values-de-rDE",
    "values-fr",
    "values-ja",
    "values-ko",
    "values-ms",
    "values-th",
    "values-vi",
    "values-zh-rCN",
    "values-zh-rTW",
]

STRING_LINE_RE = re.compile(
    r'^(?P<prefix>\s*<string\b[^>]*\bname="(?P<name>[^"]+)"[^>]*>)(?P<value>.*)(?P<suffix></string>\s*)$'
)
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[sd]")


@dataclass(frozen=True)
class StringEntry:
    name: str
    value: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report and sync Android strings_localized.xml files against the base English template."
    )
    parser.add_argument("--repo-root", required=True, help="Absolute or relative repository root path.")
    parser.add_argument("--translations-file", help="JSON file containing only missing translations.")
    parser.add_argument("--report", action="store_true", help="Print JSON report and exit.")
    parser.add_argument("--write", action="store_true", help="Rewrite locale files using the base template.")
    args = parser.parse_args()

    if not args.report and not args.write:
        parser.error("one of --report or --write is required")
    if args.write and not args.translations_file:
        parser.error("--translations-file is required with --write")
    return args


def read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def parse_string_map(path: Path) -> Dict[str, StringEntry]:
    entries: Dict[str, StringEntry] = {}
    for line in read_lines(path):
        match = STRING_LINE_RE.match(line.rstrip("\n"))
        if not match:
            continue
        name = match.group("name")
        if name in entries:
            raise ValueError(f"duplicate key {name} in {path}")
        entries[name] = StringEntry(name=name, value=match.group("value"))
    return entries


def collect_base_template(base_path: Path) -> Tuple[List[str], List[str]]:
    lines = read_lines(base_path)
    keys: List[str] = []
    seen = set()
    for line in lines:
        match = STRING_LINE_RE.match(line.rstrip("\n"))
        if not match:
            continue
        name = match.group("name")
        if name in seen:
            raise ValueError(f"duplicate key {name} in {base_path}")
        seen.add(name)
        keys.append(name)
    return lines, keys


def placeholder_tokens(value: str) -> Tuple[str, ...]:
    return tuple(PLACEHOLDER_RE.findall(value))


def locale_path(repo_root: Path, locale_dir: str) -> Path:
    return repo_root / "app" / "src" / "main" / "res" / locale_dir / "strings_localized.xml"


def build_report(repo_root: Path) -> dict:
    base_path = locale_path(repo_root, "values")
    base_lines, base_keys = collect_base_template(base_path)
    base_map = parse_string_map(base_path)
    report = {
        "base_file": str(base_path),
        "base_line_count": len(base_lines),
        "base_key_count": len(base_keys),
        "locales": {},
    }
    base_key_set = set(base_keys)
    for locale_dir in TARGET_LOCALES:
        path = locale_path(repo_root, locale_dir)
        locale_lines = read_lines(path)
        locale_map = parse_string_map(path)
        locale_keys = list(locale_map.keys())
        locale_key_set = set(locale_keys)
        missing = [key for key in base_keys if key not in locale_key_set]
        extra = [key for key in locale_keys if key not in base_key_set]
        wrong_placeholders = []
        for key in base_keys:
            if key not in locale_map:
                continue
            if placeholder_tokens(base_map[key].value) != placeholder_tokens(locale_map[key].value):
                wrong_placeholders.append(key)
        report["locales"][locale_dir] = {
            "file": str(path),
            "line_count": len(locale_lines),
            "key_count": len(locale_keys),
            "missing_keys": missing,
            "extra_keys": extra,
            "placeholder_mismatches": wrong_placeholders,
        }
    return report


def load_translations(path: Path) -> Dict[str, Dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("translations file must be a JSON object")
    normalized: Dict[str, Dict[str, str]] = {}
    for locale_dir, values in data.items():
        if locale_dir not in TARGET_LOCALES:
            raise ValueError(f"unsupported locale key in translations file: {locale_dir}")
        if not isinstance(values, dict):
            raise ValueError(f"translations for {locale_dir} must be an object")
        normalized[locale_dir] = {}
        for key, value in values.items():
            if not isinstance(value, str):
                raise ValueError(f"translation value for {locale_dir}:{key} must be a string")
            normalized[locale_dir][key] = value
    return normalized


def rewrite_locale(
    base_lines: List[str],
    base_map: Dict[str, StringEntry],
    locale_map: Dict[str, StringEntry],
    translated_values: Dict[str, str],
) -> List[str]:
    output: List[str] = []
    for line in base_lines:
        stripped = line.rstrip("\n")
        match = STRING_LINE_RE.match(stripped)
        if not match:
            output.append(line)
            continue
        name = match.group("name")
        if name in locale_map:
            value = locale_map[name].value
        else:
            if name not in translated_values:
                raise ValueError(f"missing translation for key {name}")
            value = translated_values[name]
            if placeholder_tokens(base_map[name].value) != placeholder_tokens(value):
                raise ValueError(f"placeholder mismatch for key {name}")
        newline = "\n" if line.endswith("\n") else ""
        output.append(f"{match.group('prefix')}{value}{match.group('suffix')}{newline}")
    return output


def ensure_complete_translations(
    base_keys: Iterable[str],
    locale_map: Dict[str, StringEntry],
    provided: Dict[str, str],
) -> List[str]:
    missing = [key for key in base_keys if key not in locale_map]
    absent = [key for key in missing if key not in provided]
    return absent


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    report = build_report(repo_root)
    if args.report:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not args.write:
            return 0

    base_path = locale_path(repo_root, "values")
    base_lines, base_keys = collect_base_template(base_path)
    base_map = parse_string_map(base_path)
    translations = load_translations(Path(args.translations_file)) if args.translations_file else {}

    for locale_dir in TARGET_LOCALES:
        path = locale_path(repo_root, locale_dir)
        locale_map = parse_string_map(path)
        provided = translations.get(locale_dir, {})
        absent = ensure_complete_translations(base_keys, locale_map, provided)
        if absent:
            missing_preview = ", ".join(absent[:10])
            raise ValueError(f"{locale_dir} is missing translations for {len(absent)} keys: {missing_preview}")
        extra_provided = [key for key in provided if key in locale_map]
        if extra_provided:
            raise ValueError(f"{locale_dir} translations file includes existing keys: {', '.join(extra_provided[:10])}")

        rewritten = rewrite_locale(base_lines, base_map, locale_map, provided)
        path.write_text("".join(rewritten), encoding="utf-8")
        print(f"rewrote {path}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
