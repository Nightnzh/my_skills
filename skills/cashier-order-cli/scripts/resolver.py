from __future__ import annotations

from dataclasses import dataclass, field

from menu import MenuItem, calculate_total, find_closest_matches, find_items_by_term


@dataclass
class ResolutionInput:
    prompt: str | None
    target_total: int | None = None
    item_names: list[str] = field(default_factory=list)


@dataclass
class ResolutionResult:
    status: str
    selected_items: list[MenuItem]
    total_price: int
    question: str | None = None


def _extract_candidate_terms(request: ResolutionInput) -> list[str]:
    if request.item_names:
        return [name.strip() for name in request.item_names if name.strip()]

    if not request.prompt:
        return []

    cleaned = (
        request.prompt.replace("幫我點", " ")
        .replace("最接近", " ")
        .replace("元", " ")
        .replace("一張單", " ")
        .replace("的", " ")
        .replace("加", " ")
    )
    raw_terms = [token.strip() for token in cleaned.split() if token.strip()]
    return [term for term in raw_terms if not term.isdigit()]


def _deduplicate(items: list[MenuItem]) -> list[MenuItem]:
    seen: set[str] = set()
    deduped: list[MenuItem] = []
    for item in items:
        if item.item_id in seen:
            continue
        deduped.append(item)
        seen.add(item.item_id)
    return deduped


def resolve_order(request: ResolutionInput, items: list[MenuItem]) -> ResolutionResult:
    selected: list[MenuItem] = []
    for term in _extract_candidate_terms(request):
        matches = find_items_by_term(items, term)
        if not matches:
            continue
        if len(matches) > 1:
            return ResolutionResult(
                status="needs-input",
                selected_items=[],
                total_price=0,
                question="你要的是 " + " 還是 ".join(item.name for item in matches) + "？",
            )
        selected.append(matches[0])

    selected = _deduplicate(selected)

    if request.target_total is not None:
        if selected:
            current_total = calculate_total(selected)
            if current_total == request.target_total:
                return ResolutionResult("resolved", selected, current_total)

            best_selection = selected
            best_gap = abs(request.target_total - current_total)
            remaining_pool = [item for item in items if item.item_id not in {chosen.item_id for chosen in selected}]
            remaining_target = max(request.target_total - current_total, 0)
            if remaining_target > 0 and remaining_pool:
                matches = find_closest_matches(remaining_pool, remaining_target, max_items=2)
                if matches:
                    candidate_selection = _deduplicate(selected + matches[0])
                    candidate_gap = abs(request.target_total - calculate_total(candidate_selection))
                    if candidate_gap < best_gap:
                        best_selection = candidate_selection
                        best_gap = candidate_gap
            selected = best_selection

        if not selected:
            closest = find_closest_matches(items, request.target_total)
            if closest:
                selected = closest[0]

    return ResolutionResult(
        status="resolved",
        selected_items=selected,
        total_price=calculate_total(selected),
    )
