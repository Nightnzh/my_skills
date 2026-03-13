from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse


@dataclass(frozen=True)
class BootstrapContext:
    welcome_url: str
    store_id: str
    custom_uuid: str | None
    locale: str | None


def parse_welcome_url(url: str) -> BootstrapContext:
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    store_id = path_parts[path_parts.index("store") + 1]
    query = parse_qs(parsed.query)
    custom_uuid = query.get("customUuid", [None])[0]
    locale = query.get("welcomeLocale", [None])[0]
    return BootstrapContext(
        welcome_url=url,
        store_id=store_id,
        custom_uuid=custom_uuid,
        locale=locale,
    )


def derive_order_creation_payload(
    welcome_payload: dict,
    preferred_serve_type: str | None = None,
    preferred_order_time: str | None = None,
) -> dict:
    serve_types = welcome_payload.get("serveTypes", [])
    order_time_options = welcome_payload.get("orderTimeOptions", [])

    serve_type = preferred_serve_type
    if serve_type is None:
        for option in serve_types:
            if option.get("enabled"):
                serve_type = option.get("code")
                break

    order_time = preferred_order_time
    if order_time is None:
        for option in order_time_options:
            if option.get("enabled"):
                order_time = option.get("type")
                break

    payload: dict[str, str] = {}
    if serve_type:
        payload["serveType"] = serve_type
    if order_time:
        payload["orderTime"] = order_time
    return payload
