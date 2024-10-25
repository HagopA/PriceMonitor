import time
from datetime import datetime

import requests
import schedule


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
        print(f"Error fetching product {product_id}: {response.status_code}")
        return None


# Function to check the price
def check_price(product):
    product_data = fetch_product_data(product['product_id'])

    if product_data:
        offer = product_data[0]  # Assuming the first offer is the relevant one
        regular_price = offer.get('regularPrice')
        sale_price = offer.get('salePrice')
        sale_end_date = offer.get('saleEndDate')

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log the price and sale end date if available
        log_message = f"[{current_time}] Current regular price for {product['product_name']}: ${regular_price}. Current sale price: ${sale_price}."

        # If saleEndDate is available, convert it to a readable format
        if sale_end_date:
            sale_end_date = datetime.strptime(sale_end_date, "%Y-%m-%dT%H:%M:%SZ")
            sale_end_date_str = sale_end_date.strftime("%Y-%m-%d %H:%M:%S")
            log_message += f" Sale ends on: {sale_end_date_str}"
        else:
            sale_end_date_str = "No sale end date provided"
            log_message += f" {sale_end_date_str}"

        print(log_message)

        # Check if the salePrice is lower than or equal to the target price
        if sale_price <= product['target_price'] and not product['alerted']:
            send_alert(product['product_name'], sale_price, sale_end_date_str)  # Notify via Discord
            return True  # Return alerted status
    return product['alerted']


# Function to monitor the list of products
def monitor_products():
    for product in products:
        product['alerted'] = check_price(product)
        time.sleep(3)  # Wait 3 seconds between each request
    print()


# Function to send an alert via Discord
def send_alert(product_name, price, sale_end_date_str):
    webhook_url = 'https://discordapp.com/api/webhooks/1298699024924151899/5_GM4ZKIRgFc04fthbYR6YtrcHXT_N-NG1lZVJQwpgCIWRyD2rUR_xnqYKQMMivvfnvh'
    message = {
        "content": f"Price alert! The '{product_name}' is now on sale for ${price}. Sale ends on: {sale_end_date_str}"
    }
    requests.post(webhook_url, json=message)


# Function to reset the alerted status of all products (run every other day)
def reset_alerted_status():
    for product in products:
        product['alerted'] = False
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Alerted statuses reset.")


# List of products to monitor
products = [
    {'product_id': '17924069', 'product_name': 'LG QNED90T', 'target_price': 2100, 'alerted': False},
    {'product_id': '17080864', 'product_name': 'Sony X90L', 'target_price': 2100, 'alerted': False},
    {'product_id': '17909536', 'product_name': 'Sony Bravia 7', 'target_price': 2900, 'alerted': False},
    {'product_id': '17909543', 'product_name': 'Sony Bravia 9', 'target_price': 3000, 'alerted': False},
    {'product_id': '17924064', 'product_name': 'LG B4', 'target_price': 2500, 'alerted': False},
    {'product_id': '17921975', 'product_name': 'LG C4', 'target_price': 3000, 'alerted': False},
    {'product_id': '17909539', 'product_name': 'Sony Bravia 8', 'target_price': 3000, 'alerted': False},
    {'product_id': '17230341', 'product_name': 'Sony A95L', 'target_price': 3000, 'alerted': False},
]

# Scheduling tasks
schedule.every(1).hours.at(':00').do(monitor_products)  # Run monitor_products() every hour
schedule.every(2).days.at("06:00").do(reset_alerted_status)  # Reset alerted status every other day at 6AM

# Main loop to run scheduled tasks
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
