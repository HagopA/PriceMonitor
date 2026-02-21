# PriceMonitor

A lightweight Python script that monitors product prices on Canadian retail websites and sends Discord alerts when a tracked product drops to or below a target price.

## Supported Retailers

- BestBuy CA
- Home Depot CA

## Requirements

- Python 3.3+
- `requests`
- `schedule`

```bash
pip install requests schedule
```

## Setup

### 1. Configure products

Open `price_monitor.py` and edit the product lists inside `main()`. Each product is a dict with four keys:

```python
{'product_id': '16705056', 'product_name': 'Cybex Gazelle S 2 Second Seat', 'target_price': 300, 'alerted': False}
```

- `product_id` — the retailer's internal SKU (found in the product URL on the retailer's website)
- `product_name` — human-readable label used in logs and alerts
- `target_price` — alert fires when the sale price is at or below this value
- `alerted` — always set to `False`; managed automatically at runtime

### 2. Configure Discord webhooks

Each retailer module has a `WEBHOOK_URL` constant at the top of the file:

- `bestbuy/monitor.py`
- `homedepot/monitor.py`

Replace the value with your own Discord webhook URL.

### 3. Enable/disable retailers

Inside `main()` in `price_monitor.py`, comment or uncomment the `schedule.every(...)` lines to control which retailers are active.

## Running

```bash
python price_monitor.py
```

The script runs indefinitely. Stop it with `Ctrl+C`.

Each enabled retailer is polled once per hour. Logs are written to both the console and a daily rotating file under `logs/`.

## Project Structure

```
PriceMonitor/
├── price_monitor.py   # Entry point: logging setup, product lists, scheduler
├── utils.py           # Shared utilities (HTTP fetch, Discord alerts, monitoring loop)
├── bestbuy/
│   └── monitor.py     # BestBuy CA integration
└── homedepot/
    └── monitor.py     # Home Depot CA integration
```

## Adding a New Retailer

1. Create a `<retailer>/` directory with a `monitor.py` file inside.
2. Define a `WEBHOOK_URL` constant at the top.
3. Implement the four standard functions — `monitor_products`, `check_price`, `fetch_product_data`, `send_alert` — following the pattern in an existing retailer module.
4. In `price_monitor.py`, import the new module, add a product list, and add a `schedule.every(...)` line inside `main()`.
