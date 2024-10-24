import platform
import time
from datetime import datetime
from pathlib import Path

import requests
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


# Get the correct ChromeDriver path based on the operating system and architecture
def get_chromedriver_path():
    # Get the current OS and architecture
    current_os = platform.system().lower()
    architecture = platform.machine().lower()

    # Determine the appropriate ChromeDriver file based on OS and architecture
    if "windows" in current_os:
        if architecture == "amd64" or architecture == "x86_64":  # 64-bit Windows
            driver_name = "chromedriver_win64.exe"
        else:  # 32-bit Windows
            driver_name = "chromedriver_win32.exe"
    elif "darwin" in current_os:  # macOS
        if architecture == "arm64":  # Apple Silicon (ARM-based Macs)
            driver_name = "chromedriver_mac_arm64"
        else:  # Intel-based Macs
            driver_name = "chromedriver_mac_x64"
    elif "linux" in current_os:
        driver_name = "chromedriver_linux64"
    else:
        raise Exception(f"Unsupported operating system: {current_os} ({architecture})")

    # Build the full path to the ChromeDriver
    project_root = Path(__file__).parent
    driver_path = project_root / 'drivers' / 'chrome_130.0.6723.69' / driver_name

    # Check if the driver exists
    if not driver_path.exists():
        raise FileNotFoundError(f"ChromeDriver not found at {driver_path}")

    return driver_path

# Function to check the price of a product
def check_price(url, target_price, product_name, alerted):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Optional: run in headless mode

    # Specify the full path to the ChromeDriver executable
    webdriver_path = get_chromedriver_path()

    # Set up WebDriver service
    service = Service(str(webdriver_path))
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the webpage
    driver.get(url)

    # Let the page load completely
    time.sleep(5)

    try:
        # Wait for the element to be present in the DOM
        price_element = WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "#ID_VARIANTS_COMPONENT > div > div.variantOptionsBoxContainer_R2jnc > div.optionBox_3I57G.variantOptionTextWithPrice_1kbUz.isSelected_3g8j6 > p.price_3O7LI"))
        )

        # Get the text of the element which contains the price
        price_text = price_element.text
        # Remove any non-numeric characters (like '$' and ',')
        price_value = float(price_text.replace('$', '').replace(',', '').strip())

        # Get the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format the date and time

        print(f"[{current_time}] Current price for {product_name}: ${price_value}")

        # Check if the price is below the target price
        if price_value < target_price and not alerted:
            notify_discord(product_name, url, price_value)  # Call the notification function
            return True # Indicate that we alerted for this product

    except Exception as e:
        print(f"An error occurred for product '{product_name}': {e}")

    # Close the browser session
    driver.quit()
    return alerted # Return the current alerted status


# Notification via Discord Webhook
def notify_discord(product_name, url, price):
    webhook_url = 'https://discordapp.com/api/webhooks/1298699024924151899/5_GM4ZKIRgFc04fthbYR6YtrcHXT_N-NG1lZVJQwpgCIWRyD2rUR_xnqYKQMMivvfnvh'
    message = {
        "content": f"Price alert! The product '{product_name}' at {url} is now ${price:.2f}!"
    }
    requests.post(webhook_url, json=message)


# List of products to monitor with their target prices
products = [
    {
        'url': 'https://www.bestbuy.ca/en-ca/product/sony-75-4k-uhd-hdr-led-smart-google-tv-xr75x90l/17080864',
        'target_price': 2100,
        'product_name': 'Sony X90L',
        'alerted': False
    },
    {
        'url': 'https://www.bestbuy.ca/en-ca/product/sony-bravia-7-75-4k-uhd-hdr-mini-led-qled-smart-google-tv-k75xr70b-2024/17909536',
        'target_price': 2900,
        'product_name': 'Sony Bravia 7',
        'alerted': False
    },
    {
        'url': 'https://www.bestbuy.ca/en-ca/product/sony-bravia-9-75-4k-uhd-hdr-mini-led-qled-smart-google-tv-k75xr90b-2024/17909543',
        'target_price': 3000,
        'product_name': 'Sony Bravia 9',
        'alerted': False
    },
    {
        'url': 'https://www.bestbuy.ca/en-ca/product/lg-c4-77-4k-uhd-hdr-oled-evo-webos-smart-tv-oled77c4pua-2024/17921975',
        'target_price': 3000,
        'product_name': 'LG C4',
        'alerted': False
    },
    {
        'url': 'https://www.bestbuy.ca/en-ca/product/sony-bravia-8-77-4k-uhd-hdr-oled-smart-google-tv-k77xr80b-2024/17909539',
        'target_price': 3000,
        'product_name': 'Sony Bravia 8',
        'alerted': False
    },
    {
        'url': 'https://www.bestbuy.ca/en-ca/product/sony-bravia-xr-77-4k-uhd-hdr-oled-smart-google-tv-xr77a95l/17230341',
        'target_price': 3000,
        'product_name': 'Sony A95L',
        'alerted': False
    },
]

# Function to reset alerted status
def reset_alerted_status():
    for product in products:
        product['alerted'] = False
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Alerted status reset for all products.")

# Function to run the monitoring
def monitor_products():
    for product in products:
        product['alerted'] = check_price(product['url'], product['target_price'], product['product_name'], product['alerted'])


# Schedule the monitoring every hour
schedule.every().hour.at(':00').do(monitor_products)

# Schedule the reset of alerted status every week (e.g., every Monday at 00:00)
schedule.every().friday.at("00:00").do(reset_alerted_status)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
