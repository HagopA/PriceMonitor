import logging
from datetime import datetime

import utils

WEBHOOK_URL = 'https://discordapp.com/api/webhooks/1298699024924151899/5_GM4ZKIRgFc04fthbYR6YtrcHXT_N-NG1lZVJQwpgCIWRyD2rUR_xnqYKQMMivvfnvh'


# Function to monitor the list of products
def monitor_products(products):
    utils.monitor_products(products, check_price)


# Function to check the price
def check_price(product):
    product_data = fetch_product_data(product['product_id'])

    if product_data:
        offer = product_data[0]
        regular_price = offer.get('regularPrice')
        sale_price = offer.get('salePrice')
        sale_end_date_raw = offer.get('saleEndDate')

        log_message = f"Current regular price for {product['product_name']}: ${regular_price}. Current sale price: ${sale_price}."

        if sale_end_date_raw:
            sale_end_date_str = datetime.strptime(sale_end_date_raw, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
            log_message += f" Sale ends on: {sale_end_date_str}"
        else:
            sale_end_date_str = "No sale end date provided"
            log_message += f" {sale_end_date_str}"

        logging.info(log_message)

        if sale_price <= product['target_price'] and not product['alerted']:
            send_alert(product['product_name'], sale_price, regular_price, sale_end_date_str)
            return True

    return product['alerted']


# Function to fetch product details from the BestBuy CA API
def fetch_product_data(product_id):
    url = f"https://www.bestbuy.ca/api/offers/v1/products/{product_id}/offers"
    return utils.fetch_json(url, product_id, valid_status_codes=(200, 304))


# Function to send an alert via Discord
def send_alert(product_name, sale_price, regular_price, sale_end_date_str):
    savings_amount_percent = round((regular_price - sale_price) / regular_price * 100, 2)
    message = (
        f"Price alert! The '{product_name}' is now on sale for ${sale_price} "
        f"from its original price of ${regular_price}. "
        f"Saving {savings_amount_percent}%. Sale ends on: {sale_end_date_str}"
    )
    log = (
        f"Alert! {product_name} is now on sale for ${sale_price} from its original price of ${regular_price}. "
        f"Saving {savings_amount_percent}%. Sale ends on: {sale_end_date_str}\n"
    )
    utils.post_discord_alert(WEBHOOK_URL, message, log)
