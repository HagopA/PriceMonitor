# CLAUDE.md — PriceMonitor

## Project Overview

PriceMonitor is a lightweight Python script that polls product prices on Canadian retail websites (BestBuy CA, Home Depot CA) and sends Discord webhook alerts when a tracked product's sale price drops at or below a configured target price.

- No web framework, no database, no async code
- Dependencies: `requests`, `schedule` (standard library only otherwise)
- Runs as a persistent process with an infinite `while True` loop

---

## Repository Structure

```
PriceMonitor/
├── price_monitor.py        # Entry point: logging setup, product lists, scheduler
├── utils.py                # Shared utilities used by all retailer modules
├── bestbuy/
│   └── monitor.py          # BestBuy CA API integration + Discord alert logic
└── homedepot/
    └── monitor.py          # Home Depot CA API integration + Discord alert logic
```

---

## Running the Application

```bash
pip install requests schedule
python price_monitor.py
```

The process runs indefinitely. Kill with `Ctrl+C`.

Logs are written to both stdout and `logs/price_monitor_YYYY_MM_DD.log`. The `logs/` directory is created automatically on startup. Log files rotate daily at midnight and are retained for 7 days.

---

## Configuration

All configuration is hardcoded in source — there is no `.env` file, no config file, and no CLI arguments.

### Product Lists (`price_monitor.py`)

Each product is a dict with four keys:

```python
{'product_id': '<retailer-specific-id>', 'product_name': 'Human-readable name', 'target_price': 1500, 'alerted': False}
```

- `product_id` — the retailer's internal SKU/product identifier
- `target_price` — alert fires when `sale_price <= target_price`
- `alerted` — in-memory flag; prevents duplicate alerts within a cycle; starts as `False`

**Current product lists:**
- `bestbuy_products` — 1 stroller (Cybex Gazelle S 2 Second Seat); 13 TVs commented out
- `homedepot_products` — 1 baseboard heater

### Scheduling (`price_monitor.py`)

```python
# BestBuy runs every hour on the hour
schedule.every(1).hours.at(':00').do(bestbuy.monitor.monitor_products, bestbuy_products)

# Home Depot monitoring is DISABLED (commented out)
# schedule.every(1).hours.at(':00').do(homedepot.monitor.monitor_products, homedepot_products)

# Resets `alerted` flags every 2 days at 06:00 AM
schedule.every(2).days.at("06:00").do(reset_alerted_status, bestbuy_products)
```

> **Note:** Home Depot monitoring is intentionally commented out. Re-enable by uncommenting and adding its product list to `reset_alerted_status` if needed.

### Discord Webhook URLs

Each retailer's `monitor.py` defines a module-level `WEBHOOK_URL` constant at the top of the file.

---

## Shared Utilities (`utils.py`)

`utils.py` contains logic common to all retailer modules:

| Name | Type | Purpose |
|---|---|---|
| `BROWSER_HEADERS` | constant | Spoofed browser `User-Agent` headers sent with every API request |
| `monitor_products` | `(products, check_price_fn)` | Iterates products, calls the retailer's `check_price`, writes blank log separator |
| `fetch_json` | `(url, product_id, valid_status_codes=(200,))` | Makes HTTP GET with `BROWSER_HEADERS`; returns parsed JSON or `None` on failure |
| `post_discord_alert` | `(webhook_url, message_content, log_message)` | POSTs to a Discord webhook and logs the alert |

---

## Retailer Module Pattern

Each retailer module (`bestbuy/monitor.py`, `homedepot/monitor.py`) exposes the same four functions:

| Function | Signature | Purpose |
|---|---|---|
| `monitor_products` | `(products: list)` | Delegates to `utils.monitor_products` with the retailer's `check_price` |
| `check_price` | `(product: dict) -> bool` | Fetches price, logs it, triggers alert if threshold met; returns new `alerted` state |
| `fetch_product_data` | `(product_id: str) -> list\|None` | Builds the retailer API URL, delegates HTTP call to `utils.fetch_json` |
| `send_alert` | `(...)` | Builds retailer-specific message strings, delegates POST to `utils.post_discord_alert` |

### API Endpoints

**BestBuy CA:**
```
GET https://www.bestbuy.ca/api/offers/v1/products/{product_id}/offers
```
- Accepts HTTP 200 or 304 as success
- Response fields used: `regularPrice`, `salePrice`, `saleEndDate`

**Home Depot CA:**
```
GET https://www.homedepot.ca/api/productsvc/v1/products-localized-basic?products={product_id}&store=7159&lang=en
```
- Accepts HTTP 200 only
- Response fields used: `optimizedPrice.displayPrice.value`, `optimizedPrice.wasprice.value`, `optimizedPrice.percentSaving`
- Store ID `7159` and language `en` are hardcoded

---

## Adding a New Retailer

1. Create the package directory and module file:
   ```
   <retailer>/
   └── monitor.py
   ```

2. At the top of `monitor.py`, define a `WEBHOOK_URL` constant with the Discord webhook URL.

3. Implement the four standard functions in `monitor.py`, using `utils.monitor_products`, `utils.fetch_json`, and `utils.post_discord_alert` for the shared logic.

4. In `price_monitor.py`:
   - Add `import <retailer>.monitor`
   - Add a `<retailer>_products` list inside `main()`
   - Add a `schedule.every(...)` line
   - Pass the product list to `reset_alerted_status` in its schedule entry

---

## Code Conventions

- **Naming:** `snake_case` for all functions and variables; `UPPER_CASE` for module-level constants
- **Error handling:** `try`/`except` is not used; instead, non-200 HTTP responses are caught via status code checks, logged as warnings, and return `None` — the caller skips gracefully
- **Logging:** Root logger is configured in `price_monitor.py`; all modules use `logging.info()` and `logging.warning()` directly
- **State:** The `alerted` flag on each product dict is mutated in place by `monitor_products` (`product['alerted'] = check_price(product)`). This state lives only in memory and resets on restart.
- **No tests:** There is no test suite. Validate changes by running the script and observing log output / Discord messages.

---

## Known Gotchas

- **Home Depot is disabled.** The Home Depot schedule line in `price_monitor.py` is commented out. Do not assume Home Depot monitoring is running.
- **State resets on restart.** All `alerted` flags return to `False` when the process restarts, so alerts may fire again immediately for products already at or below target.
- **No `requirements.txt`.** Install `requests` and `schedule` manually before running.
- **`reset_alerted_status` only covers BestBuy.** If Home Depot is re-enabled, add `homedepot_products` to the reset schedule call too.
- **Home Depot `was_price` can be `None`** when the item is not on sale. The `check_price` function in `homedepot/monitor.py` falls back to `sale_price` for both the regular and sale price in that case.
