"""
Validation helpers for CLI inputs and order parameters.
"""

from typing import Optional


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol must be a non-empty string, e.g. 'BTCUSDT'.")
    symbol = symbol.strip().upper()
    # Basic sanity check – Binance symbols are typically alphanumeric.
    if not symbol.isalnum():
        raise ValidationError("Symbol must be alphanumeric, e.g. 'BTCUSDT'.")
    return symbol


def validate_side(side: str) -> str:
    if not side:
        raise ValidationError("Side is required and must be 'BUY' or 'SELL'.")
    side_up = side.strip().upper()
    if side_up not in {"BUY", "SELL"}:
        raise ValidationError("Side must be either 'BUY' or 'SELL'.")
    return side_up


def validate_order_type(order_type: str) -> str:
    if not order_type:
        raise ValidationError("Order type is required and must be 'MARKET' or 'LIMIT'.")
    order_type_up = order_type.strip().upper()
    if order_type_up not in {"MARKET", "LIMIT"}:
        raise ValidationError("Order type must be either 'MARKET' or 'LIMIT'.")
    return order_type_up


def validate_quantity(quantity: float) -> float:
    try:
        qty = float(quantity)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Quantity must be a number.") from exc
    if qty <= 0:
        raise ValidationError("Quantity must be greater than 0.")
    return qty


def validate_price_for_limit(order_type: str, price: Optional[float]) -> Optional[float]:
    order_type_up = validate_order_type(order_type)
    if order_type_up == "MARKET":
        if price is not None:
            raise ValidationError("Price must not be provided for MARKET orders.")
        return None

    # LIMIT order
    if price is None:
        raise ValidationError("Price is required for LIMIT orders.")
    try:
        prc = float(price)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Price must be a number for LIMIT orders.") from exc
    if prc <= 0:
        raise ValidationError("Price must be greater than 0 for LIMIT orders.")
    return prc


def validate_cli_args(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> dict:
    """
    Validate all CLI arguments and return a cleaned dict.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_order_type = validate_order_type(order_type)
    clean_quantity = validate_quantity(quantity)
    clean_price = validate_price_for_limit(clean_order_type, price)

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_order_type,
        "quantity": clean_quantity,
        "price": clean_price,
    }

