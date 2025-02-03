import logging
import time
from datetime import datetime

import requests


# Function to monitor the list of products
def monitor_products(products):
    for product in products:
        product['alerted'] = check_price(product)
        time.sleep(1)  # Wait 1 seconds between each request

    # Add a blank line to the log file without metadata
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):  # Check if it's the file handler
            handler.stream.write("\n")  # Write a newline directly to the file
            handler.flush()  # Ensure it's written immediately

    print()

# Function to check the price
def check_price(product):
    product_data = fetch_product_data(product['product_id'])

    if product_data:
        offer = product_data[0]  # Assuming the first offer is the relevant one
        regular_price = offer.get('regularPrice')
        sale_price = offer.get('salePrice')
        sale_end_date = offer.get('saleEndDate')

        # Log the price and sale end date if available
        log_message = f"Current regular price for {product['product_name']}: ${regular_price}. Current sale price: ${sale_price}."

        # If saleEndDate is available, convert it to a readable format
        if sale_end_date:
            sale_end_date = datetime.strptime(sale_end_date, "%Y-%m-%dT%H:%M:%SZ")
            sale_end_date_str = sale_end_date.strftime("%Y-%m-%d %H:%M:%S")
            log_message += f" Sale ends on: {sale_end_date_str}"
        else:
            sale_end_date_str = "No sale end date provided"
            log_message += f" {sale_end_date_str}"

        logging.info(log_message)

        # Check if the salePrice is lower than or equal to the target price
        if sale_price <= product['target_price'] and not product['alerted']:
            send_alert(product['product_name'], sale_price, regular_price, sale_end_date_str)  # Notify via Discord
            return True  # Return alerted status
    return product['alerted']

# Function to fetch product details from BestBuy API
def fetch_product_data(product_id):
    url = f"https://www.bestbuy.ca/api/offers/v1/products/{product_id}/offers"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200 or response.status_code == 304:
        return response.json()
    else:
        logging.warning(f"Error fetching product {product_id}: {response.status_code}\n")
        return None

# Function to send an alert via Discord
def send_alert(product_name, sale_price, regular_price, sale_end_date_str):
    savings_amount_percent = round((regular_price - sale_price) / regular_price * 100, 2)
    webhook_url = 'https://discordapp.com/api/webhooks/1298699024924151899/5_GM4ZKIRgFc04fthbYR6YtrcHXT_N-NG1lZVJQwpgCIWRyD2rUR_xnqYKQMMivvfnvh'
    message = {
        "content": f"Price alert! The '{product_name}' is now on sale for ${sale_price} from its original price of ${regular_price}. "
                   f"Saving {savings_amount_percent}%. Sale ends on: {sale_end_date_str}"
    }
    requests.post(webhook_url, json=message)
    logging.info(f"Alert! {product_name} is now on sale for ${sale_price} from its original price of ${regular_price}. "
                 f"Saving {savings_amount_percent}%. Sale ends on: {sale_end_date_str}\n")