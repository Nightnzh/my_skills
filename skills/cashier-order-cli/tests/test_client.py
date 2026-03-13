import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from bootstrap import derive_order_creation_payload, parse_welcome_url
from client import CashierClient, PaymentStateError


class FakeTransport:
    def __init__(self, responses: dict[tuple[str, str], dict]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, str, dict | None]] = []

    def request(self, method: str, url: str, *, json: dict | None = None, headers: dict | None = None) -> dict:
        self.calls.append((method, url, json))
        return self.responses[(method, url)]


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_can_parse_welcome_url_and_extract_store_params(self) -> None:
        context = parse_welcome_url(
            "https://indev-webapp.cashier.tw/online/store/store-123/welcome?customUuid=custom-456&welcomeLocale=zh-TW"
        )

        self.assertEqual(context.store_id, "store-123")
        self.assertEqual(context.custom_uuid, "custom-456")
        self.assertEqual(context.locale, "zh-TW")

    def test_bootstrap_accepts_empty_welcome_menu_if_order_menu_later_exists(self) -> None:
        payload = derive_order_creation_payload(
            {
                "webMenuVos": [],
                "serveTypes": [{"code": "TAKE_OUT", "enabled": True}],
                "orderTimeOptions": [{"type": "ASAP", "enabled": True}],
            }
        )

        self.assertEqual(payload["serveType"], "TAKE_OUT")
        self.assertEqual(payload["orderTime"], "ASAP")


class ClientTests(unittest.TestCase):
    def test_client_classifies_pending_payment_after_submit(self) -> None:
        transport = FakeTransport(
            {
                ("GET", "https://indev-api.cashier.tw/online/v2/order/order-1"): {"status": "PENDING_PAYMENT"},
                ("GET", "https://indev-api.cashier.tw/online/v2/order/order-1/payment"): {
                    "paymentStatus": "UNPAID",
                    "paymentType": "STORE",
                },
            }
        )
        client = CashierClient(api_base_url="https://indev-api.cashier.tw", transport=transport)

        state = client.fetch_payment_state("order-1")

        self.assertEqual(state, "order-pending-payment")

    def test_client_rejects_submit_without_validated_payment_state(self) -> None:
        transport = FakeTransport(
            {
                ("GET", "https://indev-api.cashier.tw/online/v2/order/order-2"): {"status": "SUBMITTED"},
                ("GET", "https://indev-api.cashier.tw/online/v2/order/order-2/payment"): {},
            }
        )
        client = CashierClient(api_base_url="https://indev-api.cashier.tw", transport=transport)

        with self.assertRaises(PaymentStateError):
            client.fetch_payment_state("order-2")


if __name__ == "__main__":
    unittest.main()
