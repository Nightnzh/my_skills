import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from cashier_order import main
from menu import MenuItem


class StubClient:
    def __init__(self) -> None:
        self.submissions: list[list[str]] = []

    def submit_resolved_order(self, selected_items: list[MenuItem]) -> dict:
        self.submissions.append([item.name for item in selected_items])
        return {
            "status": "order-pending-payment",
            "order_uuid": "order-123",
            "total_price": sum(item.price for item in selected_items),
        }


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.menu = [
            MenuItem(item_id="press", name="壓測品項", price=10),
            MenuItem(item_id="egg", name="雞蛋", price=15),
            MenuItem(item_id="fried-egg", name="炸蛋", price=30),
            MenuItem(item_id="rice", name="白飯", price=15),
        ]

    def test_dry_run_returns_resolution_without_submit(self) -> None:
        client = StubClient()
        stdout = io.StringIO()

        exit_code = main(
            [
                "--welcome-url",
                "https://example.com/welcome",
                "--prompt",
                "幫我點最接近 50 元的炸蛋加白飯",
                "--target-total",
                "50",
                "--dry-run",
            ],
            menu_items=self.menu,
            client=client,
            stdout=stdout,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(client.submissions, [])
        self.assertIn("resolved", stdout.getvalue())

    def test_unique_result_does_not_prompt_for_input(self) -> None:
        client = StubClient()
        stdout = io.StringIO()

        exit_code = main(
            [
                "--welcome-url",
                "https://example.com/welcome",
                "--prompt",
                "幫我點最接近 50 元的炸蛋加白飯",
                "--target-total",
                "50",
            ],
            menu_items=self.menu,
            client=client,
            stdout=stdout,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(client.submissions, [["炸蛋", "白飯"]])
        self.assertNotIn("你要的是", stdout.getvalue())

    def test_ambiguous_result_prompts_once_and_returns_needs_input(self) -> None:
        client = StubClient()
        stdout = io.StringIO()

        exit_code = main(
            [
                "--welcome-url",
                "https://example.com/welcome",
                "--prompt",
                "幫我點蛋",
                "--max-questions",
                "1",
            ],
            menu_items=self.menu,
            client=client,
            stdout=stdout,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(client.submissions, [])
        self.assertIn("你要的是", stdout.getvalue())

    def test_json_output_is_machine_readable(self) -> None:
        client = StubClient()
        stdout = io.StringIO()

        exit_code = main(
            [
                "--welcome-url",
                "https://example.com/welcome",
                "--prompt",
                "幫我點最接近 50 元的炸蛋加白飯",
                "--target-total",
                "50",
                "--json",
                "--dry-run",
            ],
            menu_items=self.menu,
            client=client,
            stdout=stdout,
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["status"], "resolved")
        self.assertEqual(payload["selected_items"], ["炸蛋", "白飯"])
        self.assertEqual(payload["total_price"], 45)


if __name__ == "__main__":
    unittest.main()
