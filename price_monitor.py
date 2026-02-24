import logging
import os
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import schedule

import bestbuy.monitor
import homedepot.monitor

LOG_FOLDER = "logs"


def get_log_filename():
    today_date = datetime.now().strftime("%Y_%m_%d")
    return os.path.join(LOG_FOLDER, f"price_monitor_{today_date}.log")


def setup_logging():
    log_file_path = get_log_filename()
    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
    file_handler.namer = lambda name: name.replace(".log", "") + "_" + datetime.now().strftime("%Y_%m_%d") + ".log"

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


def reset_alerted_status(products):
    for product in products:
        product['alerted'] = False
    logging.info("Alerted statuses reset.\n")


def main():
    os.makedirs(LOG_FOLDER, exist_ok=True)
    setup_logging()

    bestbuy_products = [
        # {'product_id': '17909550', 'product_name': 'Hisense U78N 55"', 'target_price': 780, 'alerted': False},
        # {'product_id': '17924067', 'product_name': 'LG B4 48"', 'target_price': 880, 'alerted': False},
        # {'product_id': '17921978', 'product_name': 'LG C4 48"', 'target_price': 1000, 'alerted': False},
        # {'product_id': '17729478', 'product_name': 'Samsung QN90D 50"', 'target_price': 1000, 'alerted': False},
        # {'product_id': '17857408', 'product_name': 'Samsung Q80D 50"', 'target_price': 1000, 'alerted': False},
        # {'product_id': '17903775', 'product_name': 'Samsung S90D 48"', 'target_price': 1000, 'alerted': False},
        # {'product_id': '18965640', 'product_name': 'ASUS ROG Strix 27" XG27ACG', 'target_price': 340, 'alerted': False},
        {'product_id': '16705056', 'product_name': 'Cybex Gazelle S 2 Second Seat', 'target_price': 300, 'alerted': False},
        # {'product_id': '17909539', 'product_name': 'Sony Bravia 8 77"', 'target_price': 3000, 'alerted': False},
        # {'product_id': '17230341', 'product_name': 'Sony A95L 77"', 'target_price': 3000, 'alerted': False},
        # {'product_id': '17857419', 'product_name': 'Samsung Q70D 65"', 'target_price': 1300, 'alerted': False},
        # {'product_id': '17857407', 'product_name': 'Samsung Q80D 65"', 'target_price': 1400, 'alerted': False},
        # {'product_id': '15966921', 'product_name': 'Sony X85K 65"', 'target_price': 950, 'alerted': False},
        # {'product_id': '17924073', 'product_name': 'LG QNED85T 65"', 'target_price': 1300, 'alerted': False},
        # {'product_id': '17080860', 'product_name': 'Sony X90L 65"', 'target_price': 1300, 'alerted': False},
    ]

    homedepot_products = [
        {'product_id': '1001006914', 'product_name': 'Stelpro 1000W Baseboard Heater', 'target_price': 70, 'alerted': False},
    ]

    schedule.every(1).hours.at(':00').do(bestbuy.monitor.monitor_products, bestbuy_products)
    # schedule.every(1).hours.at(':00').do(homedepot.monitor.monitor_products, homedepot_products)
    schedule.every(2).days.at("06:00").do(reset_alerted_status, bestbuy_products)
    # schedule.every(2).days.at("06:00").do(reset_alerted_status, homedepot_products)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
