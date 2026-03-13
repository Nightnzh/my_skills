from __future__ import annotations


class PaymentStateError(RuntimeError):
    pass


class UrllibTransport:
    def request(self, method: str, url: str, *, json: dict | None = None, headers: dict | None = None) -> dict:
        raise NotImplementedError("Real HTTP transport will be added when the CLI flow is wired end-to-end.")


class CashierClient:
    def __init__(self, api_base_url: str, transport: object | None = None) -> None:
        self.api_base_url = api_base_url.rstrip("/")
        self.transport = transport or UrllibTransport()

    def fetch_welcome(self, welcome_url: str) -> dict:
        return self.transport.request("GET", welcome_url)

    def create_order(self, payload: dict) -> str:
        response = self.transport.request("POST", f"{self.api_base_url}/online/v2/store/order", json=payload)
        return response["orderUuid"]

    def fetch_order_menu(self, order_uuid: str) -> dict:
        return self.transport.request("GET", f"{self.api_base_url}/online/v2/order/{order_uuid}/menu")

    def add_cart_item(self, order_uuid: str, payload: dict) -> dict:
        return self.transport.request(
            "POST",
            f"{self.api_base_url}/online/menu/order/{order_uuid}/cart-items?webUrlPrefix=indev",
            json=payload,
        )

    def submit_order(self, order_uuid: str) -> dict:
        return self.transport.request(
            "POST",
            f"{self.api_base_url}/online/menu/order/{order_uuid}/submit?webUrlPrefix=indev",
        )

    def fetch_order_state(self, order_uuid: str) -> dict:
        return self.transport.request("GET", f"{self.api_base_url}/online/v2/order/{order_uuid}")

    def fetch_payment_payload(self, order_uuid: str) -> dict:
        return self.transport.request("GET", f"{self.api_base_url}/online/v2/order/{order_uuid}/payment")

    def classify_payment_state(self, order_payload: dict, payment_payload: dict | None) -> str:
        order_status = str(order_payload.get("status", "")).upper()
        payment_status = str((payment_payload or {}).get("paymentStatus", "")).upper()
        payment_type = str((payment_payload or {}).get("paymentType", "")).upper()

        if payment_status in {"PAID", "SUCCESS"}:
            return "order-complete"
        if order_status == "PENDING_PAYMENT" or payment_status in {"UNPAID", "PENDING"}:
            return "order-pending-payment"
        if order_status in {"SUBMITTED", "CREATED"} and payment_type:
            return "order-submitted"
        raise PaymentStateError("Unable to validate payment state from order/payment payloads.")

    def fetch_payment_state(self, order_uuid: str) -> str:
        order_payload = self.fetch_order_state(order_uuid)
        payment_payload = self.fetch_payment_payload(order_uuid)
        return self.classify_payment_state(order_payload, payment_payload)
