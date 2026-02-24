import logging
import time

import requests

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'application/json',
    'Connection': 'keep-alive'
}


def monitor_products(products, check_price_fn):
    for product in products:
        product['alerted'] = check_price_fn(product)
        time.sleep(1)

    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.stream.write("\n")
            handler.flush()

    logging.info("")


def fetch_json(url, product_id, valid_status_codes=(200,)):
    response = requests.get(url, headers=BROWSER_HEADERS)
    if response.status_code in valid_status_codes:
        return response.json()

    logging.warning(f"Error fetching product {product_id}: {response.status_code}\n")
    return None


def post_discord_alert(webhook_url, message_content, log_message):
    requests.post(webhook_url, json={"content": message_content})
    logging.info(log_message)
