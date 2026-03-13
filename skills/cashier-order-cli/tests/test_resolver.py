import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from menu import MenuItem, find_closest_matches
from resolver import ResolutionInput, resolve_order


class ResolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.menu = [
            MenuItem(item_id="press", name="壓測品項", price=10),
            MenuItem(item_id="egg", name="雞蛋", price=15),
            MenuItem(item_id="fried-egg", name="炸蛋", price=30),
            MenuItem(item_id="rice", name="白飯", price=15),
            MenuItem(item_id="vermicelli", name="冬粉", price=15),
        ]

    def test_resolve_ambiguous_item_name_returns_needs_input(self) -> None:
        result = resolve_order(
            ResolutionInput(prompt="幫我點蛋", target_total=None),
            self.menu,
        )

        self.assertEqual(result.status, "needs-input")
        self.assertIn("雞蛋", result.question or "")
        self.assertIn("炸蛋", result.question or "")

    def test_resolve_closest_total_prefers_exact_match(self) -> None:
        matches = find_closest_matches(self.menu, target_total=10)

        self.assertEqual(len(matches), 1)
        self.assertEqual([item.name for item in matches[0]], ["壓測品項"])

    def test_resolve_fried_egg_and_rice_for_50_returns_45_combo(self) -> None:
        result = resolve_order(
            ResolutionInput(
                prompt="幫我點最接近 50 元的炸蛋加白飯",
                target_total=50,
            ),
            self.menu,
        )

        self.assertEqual(result.status, "resolved")
        self.assertEqual([item.name for item in result.selected_items], ["炸蛋", "白飯"])
        self.assertEqual(result.total_price, 45)

    def test_structured_arguments_and_prompt_share_same_resolution_path(self) -> None:
        prompt_result = resolve_order(
            ResolutionInput(prompt="幫我點最接近 50 元的炸蛋加白飯", target_total=50),
            self.menu,
        )
        args_result = resolve_order(
            ResolutionInput(
                prompt=None,
                target_total=50,
                item_names=["炸蛋", "白飯"],
            ),
            self.menu,
        )

        self.assertEqual(prompt_result.status, args_result.status)
        self.assertEqual(prompt_result.total_price, args_result.total_price)
        self.assertEqual(
            [item.name for item in prompt_result.selected_items],
            [item.name for item in args_result.selected_items],
        )


if __name__ == "__main__":
    unittest.main()
