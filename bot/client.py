"""
Binance Futures Testnet REST API client.

Uses HMAC-SHA256 for request signing and a shared requests.Session
for efficient HTTP connection reuse.
"""

import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests


class BinanceAPIException(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, status_code: int, error_code: Optional[int], message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"Binance API error {status_code} ({error_code}): {message}")


class BinanceFuturesClient:
    """Simple Binance USDT-M Futures Testnet REST client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 10,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided.")

        self.base_url = base_url.rstrip("/")
        self.api_secret = api_secret.encode("utf-8")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    def _build_signed_body(self, params: Dict[str, Any]) -> str:
        """
        Build a signed x-www-form-urlencoded body string.

        Important: The HMAC signature must be computed from the *exact* query string
        that is sent to Binance. Sending a dict can reorder/format parameters
        differently from the string used to sign, causing -1022.
        """
        items: List[Tuple[str, Any]] = list(params.items())
        items.append(("timestamp", int(time.time() * 1000)))
        if "recvWindow" not in params:
            items.append(("recvWindow", 5000))

        query_string = urlencode(items, doseq=True)
        signature = hmac.new(
            self.api_secret, query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return f"{query_string}&signature={signature}"

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Validate HTTP and API-level errors."""
        status_code = response.status_code
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            # If still here, raise a generic error
            raise BinanceAPIException(status_code, None, "Non-JSON response from Binance API.")

        if status_code >= 400:
            error_code = data.get("code")
            message = data.get("msg", "Unknown error")
            raise BinanceAPIException(status_code, error_code, message)

        return data

    def post(
        self,
        path: str,
        params: Dict[str, Any],
        signed: bool = True,
    ) -> Dict[str, Any]:
        """
        Send a POST request to the Binance Futures API.

        :param path: Endpoint path starting with '/fapi/'.
        :param params: Request parameters.
        :param signed: Whether the endpoint requires a signature.
        """
        url = f"{self.base_url}{path}"
        if signed:
            body = self._build_signed_body(params)
            response = self.session.post(url, data=body, timeout=self.timeout)
        else:
            response = self.session.post(url, data=params, timeout=self.timeout)
        return self._handle_response(response)

    def new_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:
        """
        Place a new order on Binance Futures.

        :param symbol: Trading pair, e.g. 'BTCUSDT'.
        :param side: 'BUY' or 'SELL'.
        :param order_type: 'MARKET' or 'LIMIT'.
        :param quantity: Order quantity.
        :param price: Price for LIMIT orders.
        :param time_in_force: Time in force for LIMIT orders.
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        return self.post("/fapi/v1/order", params=params, signed=True)

