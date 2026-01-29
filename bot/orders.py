"""
Order placement logic, decoupled from CLI and client details.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .client import BinanceFuturesClient
from .logging_config import get_order_logger


@dataclass
class OrderResult:
    """Normalized view of an order response for CLI output."""

    order_id: Any
    status: str
    executed_qty: str
    avg_price: Optional[str]
    raw_response: Dict[str, Any]


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
) -> OrderResult:
    """
    Place an order through the Binance client with logging.

    :raises BinanceAPIException: When the API returns an error.
    :raises requests.RequestException: For network-related issues.
    """
    logger = get_order_logger(order_type)

    request_payload: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }
    if order_type == "LIMIT" and price is not None:
        request_payload["price"] = price
        request_payload["timeInForce"] = "GTC"

    logger.info("Placing order with payload: %s", request_payload)

    response = client.new_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )

    logger.info("Order response: %s", response)

    # Extract common fields, using defaults where appropriate
    order_id = response.get("orderId")
    status = response.get("status", "UNKNOWN")
    executed_qty = response.get("executedQty", "0")

    # For futures, avgPrice field is often present
    avg_price = response.get("avgPrice")

    return OrderResult(
        order_id=order_id,
        status=status,
        executed_qty=executed_qty,
        avg_price=avg_price,
        raw_response=response,
    )

