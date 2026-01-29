## Trading Bot - Binance Futures Testnet (USDT-M)

This is a minimal, production-quality Python 3 command-line application for placing
MARKET and LIMIT orders on the **Binance USDT-M Futures Testnet** using the
official REST API and HMAC-SHA256 request signing.

The project is structured with clear separation of concerns:

- `bot/client.py`: Binance API wrapper
- `bot/orders.py`: Order placement logic
- `bot/validators.py`: Input validation helpers
- `bot/logging_config.py`: File-based logging configuration
- `cli.py`: CLI entry point

Logs for orders are written to `logs/market_order.log` and `logs/limit_order.log`.

---

### 1. Setup Instructions

#### 1.1. Requirements

- Python 3.8 or newer
- `pip` (Python package manager)

Install Python dependencies from the project root:

```bash
cd trading_bot
pip install -r requirements.txt
```

#### 1.2. Directory Layout

- `bot/` – Core trading bot logic (client, validators, orders, logging).
- `cli.py` – Command-line interface for placing orders.
- `logs/` – Contains log files for market and limit orders.

---

### 2. Binance Futures Testnet Account Setup

1. Visit the Binance Futures Testnet page: `https://testnet.binancefuture.com`
2. Create an account or log in using your existing Binance account (if supported).
3. After logging in, go to **API Management** on the Testnet site.
4. Create a new **API Key** for the Futures Testnet.
5. Copy your **API Key** and **Secret Key** and store them securely.

These keys are **for the Testnet only** and will not place real trades.

---

### 3. Environment Variables

The application reads your Binance credentials from the following environment variables:

- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`

#### 3.1. Windows (PowerShell)

```powershell
$env:BINANCE_API_KEY="your_api_key_here"
$env:BINANCE_API_SECRET="your_secret_key_here"
```

#### 3.2. Windows (Command Prompt)

```bat
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_secret_key_here
```

#### 3.3. Unix-like (bash/zsh)

```bash
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_secret_key_here"
```

Make sure these variables are set in the same shell session where you run the bot.

---

### 4. Usage

All commands are run from inside the `trading_bot` directory:

```bash
cd trading_bot
python -m cli --help
```

The CLI expects:

- `--symbol` – Trading pair, e.g. `BTCUSDT`
- `--side` – `BUY` or `SELL`
- `--order-type` – `MARKET` or `LIMIT`
- `--quantity` – Positive float quantity
- `--price` – Required only for `LIMIT` orders

Before sending the order, the bot prints a **request summary** and then attempts to
place the order on the Binance Futures Testnet.

On success, it prints:

- `orderId`
- `status`
- `executedQty`
- `avgPrice` (if available; otherwise `N/A`)

---

### 5. Example Commands

#### 5.1. MARKET Order

Place a MARKET BUY order for `0.001` BTC on `BTCUSDT`:

```bash
python -m cli --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

#### 5.2. LIMIT Order

Place a LIMIT SELL order for `0.001` BTC at price `60000` USDT on `BTCUSDT`:

```bash
python -m cli --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 60000
```

---

### 6. Logging

The application writes concise logs for each order:

- MARKET orders: `logs/market_order.log`
- LIMIT orders: `logs/limit_order.log`

Each log entry contains:

- Timestamp
- Log level
- Request payload (symbol, side, type, quantity, price if applicable)
- Raw response payload from Binance
- Any error messages, if raised

Logs are intended to be informative but not noisy, suitable for later audit or debugging.

---

### 7. Validation and Error Handling

The application validates:

- Symbol is non-empty and alphanumeric.
- Side is one of `BUY` or `SELL`.
- Order type is one of `MARKET` or `LIMIT`.
- Quantity is a positive number.
- Price is:
  - **Not provided** for `MARKET` orders.
  - **Required** and positive for `LIMIT` orders.

Typical error types:

- **Input validation errors** – Clear messages about invalid CLI arguments.
- **Configuration errors** – Missing Binance API environment variables.
- **BinanceAPIException** – Binance API-level errors (4xx/5xx, invalid params, etc.).
- **Network errors/timeouts** – Underlying `requests` exceptions are caught and summarized.

---

### 8. Assumptions and Notes

- This project uses the **Binance USDT-M Futures Testnet** base URL:
  `https://testnet.binancefuture.com`.
- Only two order types are supported: **MARKET** and **LIMIT**.
- Only two sides are supported: **BUY** and **SELL**.
- Order precision (quantity/price step sizes) is **not** enforced client-side; the exchange
  will return a clear error if the quantity/price does not conform to symbol filters.
- HMAC-SHA256 signing is performed on the query string using the API secret, as required
  by Binance.
- This code is intended as a clean, educational starting point and can be extended with
  more advanced trading logic, risk management, and configuration layers.

