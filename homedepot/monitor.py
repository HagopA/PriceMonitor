import logging
import time

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
        sale_price = offer.get('optimizedPrice', {}).get('displayPrice', {}).get('value')
        was_price = offer.get('optimizedPrice', {}).get('wasprice', {}).get('value')
        percent_saving = offer.get('optimizedPrice', {}).get('percentSaving')

        # Log the price and sale end date if available
        log_message = f"Regular price for {product['product_name']}: ${was_price if was_price is not None else sale_price}. Current sale price: ${sale_price}."

        logging.info(log_message)

        # Check if the salePrice is lower than or equal to the target price
        if sale_price <= product['target_price'] and not product['alerted']:
            send_alert(product['product_name'], sale_price, was_price if was_price is not None else sale_price, percent_saving)  # Notify via Discord
            return True  # Return alerted status
    return product['alerted']

# Function to fetch product details from BestBuy API
def fetch_product_data(product_id):
    url = f"https://www.homedepot.ca/api/productsvc/v1/products-localized-basic?products={product_id}&store=7159&lang=en"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.warning(f"Error fetching product {product_id}: {response.status_code}\n")
        return None

# Function to send an alert via Discord
def send_alert(product_name, sale_price, regular_price, percent_saving):
    webhook_url = 'https://discord.com/api/webhooks/1334619793025925203/Il8yPSV08Dm5x2-cYCk04xImoRdbt_8PWNOCzXlSz3N_5u1C_iCIKCPRX1Zvb6trVAUQ'
    savings = f"Saving {percent_saving}." if percent_saving is not None else ''
    message = {
        "content": f"Price alert! The '{product_name}' is now on sale for ${sale_price} from its original price of ${regular_price}. {savings}"
    }
    requests.post(webhook_url, json=message)
    logging.info(f"Alert! {product_name} is now on sale for ${sale_price} from its original price of ${regular_price}. {savings}\n")