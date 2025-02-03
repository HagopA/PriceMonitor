import logging
import os
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import schedule

import bestbuy.monitor
import homedepot.monitor

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

# Function to reset the alerted status of all products (run every other day)
def reset_alerted_status(products):
    for product in products:
        product['alerted'] = False
    logging.info("Alerted statuses reset.\n")

bestbuy_products = [
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

homedepot_products = [
    {'product_id': '1001006914', 'product_name': 'Stelpro 1000W Baseboard Heater', 'target_price': 70, 'alerted': False},
]

# Scheduling tasks
# schedule.every(1).hours.at(':00').do(bestbuy.monitor.monitor_products, bestbuy_products)  # Run monitor_products() every hour
schedule.every(1).hours.at(':00').do(homedepot.monitor.monitor_products, homedepot_products)
schedule.every(2).days.at("06:00").do(reset_alerted_status, homedepot_products)  # Reset alerted status every other day at 6AM

# Main loop to run scheduled tasks
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
