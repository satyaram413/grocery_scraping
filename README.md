# Grocery Scraper

A Python-based web scraper for collecting product information from various Indian grocery delivery platforms.

## Features

- Scrapes product data from multiple grocery platforms:
  - Blinkit
  - Zepto 
  - JioMart
- Collects detailed product information:
  - Name
  - Price
  - Image URL
  - Quantity
  - Category information
- Saves data in JSON format
- Configurable category and location settings

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver

### Python Dependencies

```bash
pip install -r requirements.txt
```

## Project Structure

```
grocery_scrapers/
├── config.py          # Configuration settings and category mappings
├── scraper.py         # Main scraper implementation with Selenium
├── main.py            # Script entry point
├── requirements.txt   # Python package dependencies
└── grocery_products.json  # Output data file
```

## Running the Scraper

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd grocery_scrapers
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the scraper:
   ```bash
   python main.py
   ```

The scraped data will be saved to `grocery_products.json`.

## Output Format

```json
{
    "name": "Product Name",
    "price": "99",
    "image": "https://example.com/image.jpg",
    "quantity": "500g",
    "source": "Platform Name",
    "main_category": "Category",
    "sub_category": "Subcategory"
}
```

## Contributing

Feel free to open issues or submit pull requests for improvements.
