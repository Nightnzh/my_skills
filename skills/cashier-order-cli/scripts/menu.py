from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class MenuItem:
    item_id: str
    name: str
    price: int
    sold_out: bool = False


def available_items(items: list[MenuItem]) -> list[MenuItem]:
    return [item for item in items if not item.sold_out]


def find_items_by_term(items: list[MenuItem], term: str) -> list[MenuItem]:
    normalized_term = term.strip()
    return [item for item in available_items(items) if normalized_term and normalized_term in item.name]


def calculate_total(items: list[MenuItem]) -> int:
    return sum(item.price for item in items)


def find_closest_matches(items: list[MenuItem], target_total: int, max_items: int = 3) -> list[list[MenuItem]]:
    candidates = available_items(items)
    best_gap: int | None = None
    best_matches: list[list[MenuItem]] = []

    for size in range(1, min(max_items, len(candidates)) + 1):
        for combo in combinations(candidates, size):
            combo_list = list(combo)
            gap = abs(target_total - calculate_total(combo_list))
            if best_gap is None or gap < best_gap:
                best_gap = gap
                best_matches = [combo_list]
            elif gap == best_gap:
                best_matches.append(combo_list)

    best_matches.sort(
        key=lambda combo: (-calculate_total(combo), tuple(item.name for item in combo)),
    )
    return best_matches
