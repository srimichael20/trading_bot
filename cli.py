"""
Command-line interface for placing orders on Binance Futures Testnet (USDT-M).
"""

import argparse
import os
import sys
from typing import Optional

import requests

from bot.client import BinanceAPIException, BinanceFuturesClient
from bot.orders import place_order
from bot.validators import ValidationError, validate_cli_args


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple Binance Futures Testnet trading bot CLI.",
    )
    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT.",
    )
    parser.add_argument(
        "--side",
        required=True,
        help="Order side: BUY or SELL.",
    )
    parser.add_argument(
        "--order-type",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type: MARKET or LIMIT.",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        help="Order quantity as a positive number.",
    )
    parser.add_argument(
        "--price",
        type=float,
        help="Price for LIMIT orders (ignored for MARKET).",
    )
    return parser.parse_args(argv)


def get_env_api_credentials() -> tuple[str, str]:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise RuntimeError(
            "Environment variables BINANCE_API_KEY and BINANCE_API_SECRET must be set."
        )
    return api_key, api_secret


def print_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float],
) -> None:
    print("\nOrder request summary:")
    print("----------------------")
    print(f"Symbol     : {symbol}")
    print(f"Side       : {side}")
    print(f"Order Type : {order_type}")
    print(f"Quantity   : {quantity}")
    if order_type == "LIMIT":
        print(f"Price      : {price}")
    print()


def main(argv: Optional[list] = None) -> int:
    try:
        args = parse_args(argv)

        # Validate and normalize inputs
        validated = validate_cli_args(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )

        symbol = validated["symbol"]
        side = validated["side"]
        order_type = validated["order_type"]
        quantity = validated["quantity"]
        price = validated["price"]

        print_order_summary(symbol, side, order_type, quantity, price)

        api_key, api_secret = get_env_api_credentials()

        client = BinanceFuturesClient(
            api_key=api_key,
            api_secret=api_secret,
            base_url="https://testnet.binancefuture.com",
        )

        result = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        print("Order placed successfully.")
        print("-------------------------")
        print(f"orderId     : {result.order_id}")
        print(f"status      : {result.status}")
        print(f"executedQty : {result.executed_qty}")
        if result.avg_price is not None:
            print(f"avgPrice    : {result.avg_price}")
        else:
            print("avgPrice    : N/A")
        print()
        return 0

    except ValidationError as exc:
        print(f"Input validation error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    except BinanceAPIException as exc:
        print(f"Binance API error: {exc}", file=sys.stderr)
        return 1
    except requests.Timeout:
        print("Network timeout while communicating with Binance API.", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

