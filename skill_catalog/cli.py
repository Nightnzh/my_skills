from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from skill_catalog.catalog import build_outputs, write_outputs
from skill_catalog.install import install_skill, list_installable_skills
from skill_catalog.validation import validate_generated_outputs, validate_repository


def _default_codex_target() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return codex_home / "skills"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-catalog")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--repo", default=".")
    build_parser.add_argument("--check", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--repo", default=".")
    validate_parser.add_argument("--check-generated", action="store_true")

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("slug", nargs="?")
    install_parser.add_argument("--repo", default=".")
    install_parser.add_argument("--version")
    install_parser.add_argument("--target", default="codex")
    install_parser.add_argument("--target-root")
    install_parser.add_argument("--allow-deprecated", action="store_true")
    install_parser.add_argument("--list", action="store_true")

    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.command == "build":
        outputs = build_outputs(repo)
        if args.check:
            report = validate_generated_outputs(repo)
            if report.errors:
                for error in report.errors:
                    print(error, file=sys.stderr)
                return 1
            print("Generated outputs are up to date.")
            return 0
        write_outputs(repo, outputs)
        print("Generated catalog and docs.")
        return 0

    if args.command == "validate":
        report = validate_repository(repo)
        if args.check_generated:
            generated_report = validate_generated_outputs(repo)
            report.errors.extend(generated_report.errors)
        if report.errors:
            for error in report.errors:
                print(error, file=sys.stderr)
            return 1
        print("Validation passed.")
        return 0

    if args.command == "install":
        if args.list:
            for skill in list_installable_skills(repo):
                print(f"{skill.slug}\t{skill.version}\t{skill.status}\t{skill.summary}")
            return 0
        if not args.slug:
            print("slug is required unless --list is used", file=sys.stderr)
            return 2
        target_root = Path(args.target_root).expanduser().resolve() if args.target_root else _default_codex_target()
        result = install_skill(
            repo=repo,
            slug=args.slug,
            version=args.version,
            target_host=args.target,
            target_root=target_root,
            allow_deprecated=args.allow_deprecated,
        )
        print(f"Installed {result.slug}@{result.installed_version} to {result.destination}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
