from __future__ import annotations

import argparse
import json
import sys
from typing import TextIO

from client import CashierClient
from menu import MenuItem
from resolver import ResolutionInput, ResolutionResult, resolve_order


class SubmissionAdapter:
    def __init__(self, client: CashierClient | None = None) -> None:
        self.client = client

    def submit_resolved_order(self, selected_items: list[MenuItem]) -> dict:
        raise NotImplementedError("Live submit flow is not wired for this CLI invocation.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Place Cashier orders through a pure CLI workflow.")
    parser.add_argument("--welcome-url", required=True)
    parser.add_argument("--prompt")
    parser.add_argument("--target-total", type=int)
    parser.add_argument("--item", action="append", dest="items", default=[])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--max-questions", type=int, default=1)
    parser.add_argument("--payment", choices=("store", "online", "auto"), default="auto")
    return parser


def _serialize_result(result: ResolutionResult) -> dict:
    return {
        "status": result.status,
        "selected_items": [item.name for item in result.selected_items],
        "total_price": result.total_price,
        "question": result.question,
    }


def _write_payload(stdout: TextIO, payload: dict, as_json: bool) -> None:
    if as_json:
        stdout.write(json.dumps(payload, ensure_ascii=False))
        stdout.write("\n")
        return

    stdout.write(f"status: {payload['status']}\n")
    if payload.get("selected_items"):
        stdout.write(f"selected_items: {', '.join(payload['selected_items'])}\n")
    stdout.write(f"total_price: {payload['total_price']}\n")
    if payload.get("question"):
        stdout.write(f"question: {payload['question']}\n")
    if payload.get("order_uuid"):
        stdout.write(f"order_uuid: {payload['order_uuid']}\n")


def _default_menu_items() -> list[MenuItem]:
    return []


def main(
    argv: list[str] | None = None,
    *,
    menu_items: list[MenuItem] | None = None,
    client: object | None = None,
    stdout: TextIO | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    stdout = stdout or sys.stdout
    client = client or SubmissionAdapter(CashierClient(api_base_url="https://indev-api.cashier.tw"))
    menu_items = menu_items if menu_items is not None else _default_menu_items()

    resolution = resolve_order(
        ResolutionInput(
            prompt=args.prompt,
            target_total=args.target_total,
            item_names=args.items,
        ),
        menu_items,
    )

    if resolution.status == "needs-input":
        payload = _serialize_result(resolution)
        _write_payload(stdout, payload, args.json_output)
        return min(args.max_questions + 1, 2)

    if args.dry_run:
        payload = _serialize_result(resolution)
        _write_payload(stdout, payload, args.json_output)
        return 0

    submission = client.submit_resolved_order(resolution.selected_items)
    payload = _serialize_result(resolution)
    payload.update(submission)
    _write_payload(stdout, payload, args.json_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
