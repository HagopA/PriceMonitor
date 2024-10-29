import logging
import os
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import requests
import schedule

# Set up the log directory
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

# Function to get the log filename based on the current date
def get_log_filename():
    today_date = datetime.now().strftime("%Y_%m_%d")
    return os.path.join(log_folder, f"price_monitor_{today_date}.log")

# Setup logging configuration
def setup_logging():

    # Initialize the TimedRotatingFileHandler with a custom filename
    log_file_path = get_log_filename()
    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
    file_handler.namer = lambda name: name.replace(".log", "") + "_" + datetime.now().strftime("%Y_%m_%d") + ".log"

    # Set up a StreamHandler to output to the console
    console_handler = logging.StreamHandler()

    # Set up a formatter without milliseconds in the log entries
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Configure the root logger with both handlers
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])

setup_logging()

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


# Function to monitor the list of products
def monitor_products():
    for product in products:
        product['alerted'] = check_price(product)
        time.sleep(1)  # Wait 1 seconds between each request

    # Add a blank line to the log file without metadata
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):  # Check if it's the file handler
            handler.stream.write("\n")  # Write a newline directly to the file
            handler.flush()  # Ensure it's written immediately

    print()

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


# Function to reset the alerted status of all products (run every other day)
def reset_alerted_status():
    for product in products:
        product['alerted'] = False
    logging.info("Alerted statuses reset.\n")


# List of products to monitor
products = [
    {'product_id': '17924069', 'product_name': 'LG QNED90T 75"', 'target_price': 2100, 'alerted': False},
    {'product_id': '17080864', 'product_name': 'Sony X90L 75"', 'target_price': 2100, 'alerted': False},
    {'product_id': '17909536', 'product_name': 'Sony Bravia 7 75"', 'target_price': 2900, 'alerted': False},
    {'product_id': '17909543', 'product_name': 'Sony Bravia 9 75"', 'target_price': 3000, 'alerted': False},
    {'product_id': '17924064', 'product_name': 'LG B4 77"', 'target_price': 2500, 'alerted': False},
    {'product_id': '17921975', 'product_name': 'LG C4 77"', 'target_price': 3000, 'alerted': False},
    {'product_id': '17909539', 'product_name': 'Sony Bravia 8 77"', 'target_price': 3000, 'alerted': False},
    {'product_id': '17230341', 'product_name': 'Sony A95L 77"', 'target_price': 3000, 'alerted': False},
    {'product_id': '17857419', 'product_name': 'Samsung Q70D 65"', 'target_price': 1300, 'alerted': False},
    {'product_id': '17857407', 'product_name': 'Samsung Q80D 65"', 'target_price': 1400, 'alerted': False},
    {'product_id': '15966921', 'product_name': 'Sony X85K 65"', 'target_price': 950, 'alerted': False},
    {'product_id': '17924073', 'product_name': 'LG QNED85T 65"', 'target_price': 1300, 'alerted': False},
    {'product_id': '17080860', 'product_name': 'Sony X90L 65"', 'target_price': 1300, 'alerted': False},
]

# Scheduling tasks
schedule.every(1).hours.at(':00').do(monitor_products)  # Run monitor_products() every hour
schedule.every(2).days.at("06:00").do(reset_alerted_status)  # Reset alerted status every other day at 6AM

# Main loop to run scheduled tasks
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
