import json
import time
import re
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os

# Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATEGORIES = {
    "Mobiles": "https://priceoye.pk/mobiles",
    "Wireless Earbuds": "https://priceoye.pk/wireless-earbuds",
    "Smart Watches": "https://priceoye.pk/smart-watches"
}
OUTPUT_FILE = os.path.join(BASE_DIR, "priceoye_electronics.json")
PAGES_PER_CATEGORY = 2 # Keeping it conservative to avoid blocks

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Anti-detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
    })
    return driver

def extract_price(text):
    if not text: return 0.0
    # Clean up "Rs." and commas
    clean = re.sub(r'[^\d]', '', text)
    return float(clean) if clean else 0.0

def scrape_category(driver, category_name, base_url):
    all_products = []
    for page in range(1, PAGES_PER_CATEGORY + 1):
        url = f"{base_url}?page={page}"
        print(f"Scraping {category_name} - Page {page}: {url}")
        driver.get(url)
        
        try:
            # Wait for product cards
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.ga-dataset")))
        except Exception as e:
            print(f"Timeout waiting for cards on {url}")
            continue

        # Scroll to load images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        cards = driver.find_elements(By.CSS_SELECTOR, "a.ga-dataset")
        print(f"Found {len(cards)} cards")

        for card in cards:
            try:
                name = card.find_element(By.CSS_SELECTOR, ".p-title").text.strip()
                product_url = card.get_attribute("href")
                
                # Prices
                try:
                    # Sale Price
                    sale_price_el = card.find_elements(By.CSS_SELECTOR, ".price-box")
                    sale_price_text = sale_price_el[0].text if sale_price_el else ""
                    sale_price = extract_price(sale_price_text)
                    
                    orig_price = sale_price
                    discount = 0
                    
                    # Original Price
                    orig_price_el = card.find_elements(By.CSS_SELECTOR, ".price-diff-retail")
                    if orig_price_el:
                        # Sometimes original price has "Rs. 0" if not applicable, so we extract and check
                        ext_orig = extract_price(orig_price_el[0].text)
                        if ext_orig > 0:
                            orig_price = ext_orig
                    
                    # Discount Percentage
                    disc_el = card.find_elements(By.CSS_SELECTOR, ".price-diff-saving")
                    if disc_el:
                        disc_text = disc_el[0].text
                        disc_match = re.search(r'(\d+)%', disc_text)
                        if disc_match:
                            discount = int(disc_match.group(1))
                        
                    # Final correction: if we have a discount but orig_price == sale_price, calculate back
                    if discount > 0 and orig_price == sale_price:
                        orig_price = round(sale_price / (1 - (discount / 100)), 0)

                except Exception as pe:
                    print(f"Price parsing error: {pe}")
                    sale_price = 0.0
                    orig_price = 0.0
                    discount = 0

                # Image
                img_el = card.find_element(By.CSS_SELECTOR, "img.product-thumbnail")
                image_url = img_el.get_attribute("src") or img_el.get_attribute("data-src")

                all_products.append({
                    "name": name,
                    "category": category_name,
                    "sale_price": sale_price,
                    "original_price": orig_price,
                    "discount_percentage": discount,
                    "image_url": image_url,
                    "product_url": product_url,
                    "source": "PriceOye",
                    "timestamp": datetime.datetime.now().isoformat()
                })
            except Exception as e:
                # print(f"Error parsing card: {e}")
                continue
                
    return all_products

def main():
    driver = setup_driver()
    results = []
    try:
        for cat, url in CATEGORIES.items():
            cat_products = scrape_category(driver, cat, url)
            results.extend(cat_products)
            print(f"Total products in {cat}: {len(cat_products)}")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        
        print(f"\nSaved {len(results)} products to {OUTPUT_FILE}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
