import logging

import utils

WEBHOOK_URL = 'https://discord.com/api/webhooks/1334619793025925203/Il8yPSV08Dm5x2-cYCk04xImoRdbt_8PWNOCzXlSz3N_5u1C_iCIKCPRX1Zvb6trVAUQ'


# Function to monitor the list of products
def monitor_products(products):
    utils.monitor_products(products, check_price)


# Function to check the price
def check_price(product):
    product_data = fetch_product_data(product['product_id'])

    if product_data:
        offer = product_data[0]
        sale_price = offer.get('optimizedPrice', {}).get('displayPrice', {}).get('value')
        was_price = offer.get('optimizedPrice', {}).get('wasprice', {}).get('value')
        percent_saving = offer.get('optimizedPrice', {}).get('percentSaving')

        regular_price = was_price if was_price is not None else sale_price
        logging.info(f"Regular price for {product['product_name']}: ${regular_price}. Current sale price: ${sale_price}.")

        if sale_price <= product['target_price'] and not product['alerted']:
            send_alert(product['product_name'], sale_price, regular_price, percent_saving)
            return True

    return product['alerted']


# Function to fetch product details from the Home Depot CA API
def fetch_product_data(product_id):
    url = f"https://www.homedepot.ca/api/productsvc/v1/products-localized-basic?products={product_id}&store=7159&lang=en"
    return utils.fetch_json(url, product_id)


# Function to send an alert via Discord
def send_alert(product_name, sale_price, regular_price, percent_saving):
    savings = f"Saving {percent_saving}." if percent_saving is not None else ''
    message = f"Price alert! The '{product_name}' is now on sale for ${sale_price} from its original price of ${regular_price}. {savings}"
    log = f"Alert! {product_name} is now on sale for ${sale_price} from its original price of ${regular_price}. {savings}\n"
    utils.post_discord_alert(WEBHOOK_URL, message, log)
