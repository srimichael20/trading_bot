"""
Trading bot package initialization.

Exposes key classes and functions for external use.
"""

from .client import BinanceFuturesClient, BinanceAPIException
from .orders import place_order

__all__ = ["BinanceFuturesClient", "BinanceAPIException", "place_order"]

