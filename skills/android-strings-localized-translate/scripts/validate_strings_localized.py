#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from sync_strings_localized import (
    TARGET_LOCALES,
    collect_base_template,
    locale_path,
    parse_string_map,
    placeholder_tokens,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Android strings_localized.xml locale files against the base English file."
    )
    parser.add_argument("--repo-root", required=True, help="Absolute or relative repository root path.")
    parser.add_argument(
        "--check-placeholders",
        action="store_true",
        help="Also fail on placeholder mismatches in existing locale translations.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    base_path = locale_path(repo_root, "values")
    base_lines, base_keys = collect_base_template(base_path)
    base_map = parse_string_map(base_path)
    base_line_count = len(base_lines)
    base_key_set = set(base_keys)

    problems: List[str] = []
    for locale_dir in TARGET_LOCALES:
        path = locale_path(repo_root, locale_dir)
        locale_lines = path.read_text(encoding="utf-8").splitlines()
        locale_map = parse_string_map(path)
        locale_keys = list(locale_map.keys())
        locale_key_set = set(locale_keys)

        missing = [key for key in base_keys if key not in locale_key_set]
        extra = [key for key in locale_keys if key not in base_key_set]
        if missing:
            problems.append(f"{locale_dir}: missing keys: {', '.join(missing[:10])}")
        if extra:
            problems.append(f"{locale_dir}: extra keys: {', '.join(extra[:10])}")
        if locale_keys != base_keys:
            problems.append(f"{locale_dir}: key order differs from base")
        if len(locale_lines) != base_line_count:
            problems.append(
                f"{locale_dir}: line count {len(locale_lines)} does not match base {base_line_count}"
            )
        if args.check_placeholders:
            for key in base_keys:
                if key not in locale_map:
                    continue
                if placeholder_tokens(base_map[key].value) != placeholder_tokens(locale_map[key].value):
                    problems.append(f"{locale_dir}: placeholder mismatch for {key}")

    if problems:
        for problem in problems:
            print(problem)
        return 1

    message = f"validated {len(TARGET_LOCALES) + 1} files; all line counts, keys, and order match"
    if args.check_placeholders:
        message += "; placeholders also match"
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
