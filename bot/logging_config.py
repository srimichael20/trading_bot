"""
Centralized logging configuration for the trading bot.

Creates separate log files for market and limit orders.
"""

import logging
import os
from typing import Dict


LOG_DIR_NAME = "logs"
MARKET_LOG_FILE = "market_order.log"
LIMIT_LOG_FILE = "limit_order.log"


_order_type_to_file: Dict[str, str] = {
    "MARKET": MARKET_LOG_FILE,
    "LIMIT": LIMIT_LOG_FILE,
}


def _get_logs_directory() -> str:
    """
    Resolve the absolute path to the logs directory.

    The logs directory lives at project_root/logs relative to this file:
    trading_bot/bot/logging_config.py -> project_root/logs
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    logs_dir = os.path.join(project_root, LOG_DIR_NAME)
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def configure_root_logger() -> None:
    """
    Configure the root logger for the trading bot.

    This sets a consistent format and INFO-level logging.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def get_order_logger(order_type: str) -> logging.Logger:
    """
    Return a logger configured to write to the appropriate order log file.

    :param order_type: 'MARKET' or 'LIMIT'
    """
    configure_root_logger()

    normalized_type = order_type.strip().upper()
    if normalized_type not in _order_type_to_file:
        normalized_type = "MARKET"  # Fallback to market log

    logger_name = f"trading_bot.{normalized_type.lower()}_order"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        logs_dir = _get_logs_directory()
        file_name = _order_type_to_file[normalized_type]
        file_path = os.path.join(logs_dir, file_name)

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger

