from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import logging

from config import (
    ZEPTO_CATEGORIES,
    BLINKIT_CATEGORIES,
    JIOMART_CATEGORIES,
    LOCATION_CONFIG
)


class GroceryScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def __del__(self):
        self.driver.quit()

    def scrape_jiomart(self, category):
        products = []
        try:
            category_parts = category.split('/')
            main_category = category_parts[1]

            if main_category in JIOMART_CATEGORIES:
                category_id = JIOMART_CATEGORIES[main_category]
                url = f"https://www.jiomart.com/c/groceries/{
                    main_category}/{category_id}"
                logging.info(f"Scraping JioMart URL: {url}")

                self.driver.get(url)
                time.sleep(5)  # Initial wait for page load

                scroll_count = 0
                max_scrolls = 20  # Adjust this number as needed

                # Scroll until no more new products are loaded
                last_height = self.driver.execute_script(
                    "return document.body.scrollHeight")
                while scroll_count < max_scrolls:
                    # Scroll to bottom
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for new content to load

                    # Calculate new scroll height and compare with last scroll height
                    new_height = self.driver.execute_script(
                        "return document.body.scrollHeight")
                    if new_height == last_height:
                        # If heights are the same, no more new content
                        break
                    last_height = new_height
                    scroll_count += 1

                # Get all products after scrolling
                product_cards = self.driver.find_elements(
                    By.CLASS_NAME, 'plp-card-container')

                logging.info(f"Found {len(product_cards)} products on JioMart")

                for card in product_cards:
                    try:
                        name = card.find_element(
                            By.CLASS_NAME, 'plp-card-details-name').text.strip()
                        price = card.find_element(
                            By.CLASS_NAME, 'jm-heading-xxs').text.strip()
                        image = card.find_element(By.CLASS_NAME, 'plp-card-image').find_element(
                            By.TAG_NAME, 'img').get_attribute('src')

                        product = {
                            'name': name,
                            # Remove the rupee symbol
                            'price': price.replace('₹', ''),
                            'image': image,
                            'source': 'JioMart',
                            'category': main_category
                        }
                        products.append(product)
                    except Exception as e:
                        logging.error(
                            f"Error parsing JioMart product: {str(e)}")
                        continue

        except Exception as e:
            logging.error(f"Error scraping JioMart: {str(e)}")

        logging.info(f"Successfully scraped {
                     len(products)} products from JioMart")
        return products

    def scrape_blinkit(self, category):
        products = []
        try:
            main_category, sub_category = category.split('/')

            if main_category in BLINKIT_CATEGORIES:
                cid = BLINKIT_CATEGORIES[main_category]['cid']
                subcategory_id = BLINKIT_CATEGORIES[main_category]['subcategories'][sub_category]

                url = f"https://blinkit.com/cn/{
                    sub_category}/cid/{cid}/{subcategory_id}"
                logging.info(f"Scraping Blinkit URL: {url}")

                self.driver.get(url)
                time.sleep(5)

                # New scrolling logic - scroll in smaller increments
                last_product_count = 0
                no_new_products_count = 0
                max_attempts = 20

                while no_new_products_count < 3 and max_attempts > 0:
                    self.driver.execute_script("window.scrollBy(0, 800);")
                    time.sleep(2)

                    # Updated selector for product cards
                    current_products = self.driver.find_elements(
                        By.CSS_SELECTOR, '[data-test-id="plp-product"]')

                    if len(current_products) > last_product_count:
                        logging.info(
                            f"Found {len(current_products)} products so far...")
                        last_product_count = len(current_products)
                        no_new_products_count = 0
                    else:
                        no_new_products_count += 1

                    max_attempts -= 1

                # Updated selectors for product information
                product_cards = self.driver.find_elements(
                    By.CSS_SELECTOR, '[data-test-id="plp-product"]')
                logging.info(f"Found {len(product_cards)} products on Blinkit")

                for card in product_cards:
                    try:
                        name = card.find_element(
                            By.CLASS_NAME, "Product__UpdatedTitle-sc-11dk8zk-9").text.strip()
                        price = card.find_element(
                            By.CSS_SELECTOR, '[style*="color: rgb(31, 31, 31)"]').text.strip()
                        image = card.find_element(
                            By.TAG_NAME, "img").get_attribute("src")
                        quantity = card.find_element(
                            By.CLASS_NAME, "plp-product__quantity--box").text.strip()

                        product = {
                            'name': name,
                            'price': price.replace('₹', '').strip(),
                            'image': image,
                            'quantity': quantity,
                            'source': 'Blinkit',
                            'main_category': main_category,
                            'sub_category': sub_category
                        }
                        products.append(product)
                    except Exception as e:
                        logging.error(
                            f"Error parsing Blinkit product: {str(e)}")
                        continue

        except Exception as e:
            logging.error(f"Error scraping Blinkit: {str(e)}")

        logging.info(f"Successfully scraped {
                     len(products)} products from Blinkit")
        return products

    def scrape_zepto(self, category):
        products = []
        try:
            category_parts = category.split('/')
            main_category = category_parts[2]  # fruits-vegetables
            sub_category = category_parts[3]   # fresh-vegetables

            if main_category in ZEPTO_CATEGORIES:
                cid = ZEPTO_CATEGORIES[main_category]['cid']
                scid = ZEPTO_CATEGORIES[main_category]['subcategories'][sub_category]

                url = f"https://www.zeptonow.com{
                    category}/cid/{cid}/scid/{scid}"
                logging.info(f"Scraping Zepto URL: {url}")

                self.driver.get(url)
                time.sleep(10)

                # New scrolling logic - scroll in smaller increments
                last_product_count = 0
                no_new_products_count = 0
                max_attempts = 20

                while no_new_products_count < 3 and max_attempts > 0:
                    # Scroll in smaller increments (800 pixels each time)
                    self.driver.execute_script("window.scrollBy(0, 800);")
                    time.sleep(2)  # Wait for content to load

                    # Check current product count
                    current_products = self.driver.find_elements(
                        By.CSS_SELECTOR, '[data-testid="product-card"]')

                    if len(current_products) > last_product_count:
                        logging.info(
                            f"Found {len(current_products)} products so far...")
                        last_product_count = len(current_products)
                        no_new_products_count = 0
                    else:
                        no_new_products_count += 1

                    max_attempts -= 1

                # Rest of your code remains the same
                product_cards = []
                card_selectors = [
                    '[data-testid="product-card"]',
                    '.product-item',
                ]

                for selector in card_selectors:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, selector))
                        )
                        cards = self.driver.find_elements(
                            By.CSS_SELECTOR, selector)
                        if cards:
                            product_cards = cards
                            logging.info(
                                f"Found products with selector: {selector}")
                            break
                    except Exception:
                        continue

                if not product_cards:
                    logging.error(
                        "No product cards found with any known selectors")
                    with open('zepto_page.html', 'w', encoding='utf-8') as f:
                        f.write(self.driver.page_source)
                    return products

                logging.info(f"Found {len(product_cards)} products on Zepto")

                for card in product_cards:
                    try:
                        name = card.find_element(
                            By.CSS_SELECTOR, '[data-testid="product-card-name"]').text.strip()
                        price = card.find_element(
                            By.CSS_SELECTOR, '[data-testid="product-card-price"]').text.strip()
                        image = card.find_element(
                            By.CSS_SELECTOR, '[data-testid="product-card-image"]').get_attribute("src")
                        quantity = card.find_element(
                            By.CSS_SELECTOR, '[data-testid="product-card-quantity"]').text.strip()

                        product = {
                            'name': name,
                            'price': price.replace('₹', '').strip(),
                            'image': image,
                            'quantity': quantity,
                            'source': 'Zepto',
                            'main_category': main_category,
                            'sub_category': sub_category
                        }
                        products.append(product)
                    except Exception as e:
                        logging.error(f"Error parsing Zepto product: {str(e)}")
                        continue

        except Exception as e:
            logging.error(f"Error scraping Zepto: {str(e)}")

        logging.info(f"Successfully scraped {
                     len(products)} products from Zepto")
        return products

    def save_to_json(self, products, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=4)
            logging.info(f"Successfully saved {
                         len(products)} products to {filename}")
        except Exception as e:
            logging.error(f"Error saving to JSON: {str(e)}")
