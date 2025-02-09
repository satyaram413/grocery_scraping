from scraper import GroceryScraper
from config import JIOMART_CATEGORIES, BLINKIT_CATEGORIES, ZEPTO_CATEGORIES
import logging
import time
import random


def scrape_platform(scraper, platform, all_products):
    try:
        if platform == 'zepto':
            for main_category, data in ZEPTO_CATEGORIES.items():
                for sub_category in data['subcategories'].keys():
                    category_path = f'/cn/{main_category}/{sub_category}'
                    logging.info(f"Scraping Zepto - {category_path}")
                    products = scraper.scrape_zepto(category_path)
                    all_products.extend(products)
                    time.sleep(random.uniform(2, 5))

        elif platform == 'blinkit':
            for main_category, data in BLINKIT_CATEGORIES.items():
                for sub_category in data['subcategories'].keys():
                    category_path = f'{main_category}/{sub_category}'
                    logging.info(f"Scraping Blinkit main.py - {category_path}")
                    products = scraper.scrape_blinkit(category_path)
                    all_products.extend(products)
                    time.sleep(random.uniform(2, 5))

        elif platform == 'jiomart':
            for main_category in JIOMART_CATEGORIES.keys():
                category_path = f'groceries/{main_category}'
                logging.info(f"Scraping JioMart - {category_path}")
                products = scraper.scrape_jiomart(category_path)
                all_products.extend(products)
                time.sleep(random.uniform(2, 5))

    except Exception as e:
        logging.error(f"Error scraping {platform}: {str(e)}")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    scraper = GroceryScraper()
    all_products = []

    # Scrape each platform
    platforms = ['zepto', 'blinkit', 'jiomart']
    for platform in platforms:
        scrape_platform(scraper, platform, all_products)

    # Save results
    logging.info(f"Total products collected: {len(all_products)}")
    if all_products:
        scraper.save_to_json(
            all_products, 'grocery_products.json')
        logging.info("Scraping completed successfully!")
    else:
        logging.error("No products were scraped!")


if __name__ == '__main__':
    main()
