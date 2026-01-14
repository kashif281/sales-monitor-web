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

# Configurations
BASE_URL = "https://www.daraz.pk/shop-electronics/"
OUTPUT_FILE = "daraz_electronics.json"
MIN_DISCOUNT = 25
PAGES_TO_SCRAPE = 3

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=375,812") # Mobile viewport
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")
    
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
    match = re.search(r'Rs\.\s?([\d,]+)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    return 0.0

def scrape_page(driver, page_num):
    # Fix pagination URL
    connector = "&" if "?" in BASE_URL else "?"
    url = f"{BASE_URL}{connector}page={page_num}"
    print(f"Scraping Page {page_num}: {url}")
    driver.get(url)
    time.sleep(5)  # Let it load
    
    # Scroll slowly to load images and dynamic content
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    for i in range(1, total_height, 400):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(0.1)
    
    # Wait for products using multiple possible selectors
    card_selectors = [
        ".search-product-item",
        ".product-jfy-item",
        ".jfy-product-card-wrapper",
        "[data-qa-locator='product-item']",
        ".unit-content"
    ]
    
    cards = []
    for selector in card_selectors:
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                print(f"Found {len(cards)} products using selector: {selector}")
                break
        except:
            continue
            
    if not cards:
        print(f"No products found on page {page_num}")
        return []

    products = []
    for card in cards:
        try:
            # Get text and HTML early for extraction
            text = card.text
            html = card.get_attribute("outerHTML")
            
            # Basic info
            name = ""
            product_url = ""
            
            # Try to find name and link
            name_sel = card.find_elements(By.CSS_SELECTOR, ".RfADt, .jfy-product-card-name, .title, .name")
            if name_sel:
                name = name_sel[0].text.strip()
            
            # Find product URL
            links = card.find_elements(By.CSS_SELECTOR, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "/products/" in href:
                    product_url = href
                    # If we don't have a name yet, try this link's title/text
                    if not name:
                        t = (link.get_attribute("title") or link.text).strip()
                        if len(t) > 10 and not t.startswith("http") and not re.search(r'\.(jpg|png|webp)', t, re.I):
                            name = t
                    if product_url and name: break
            
            if not name: 
                # Last resort: take the longest text block that's not a price
                text_blocks = [t.strip() for t in text.split('\n') if len(t.strip()) > 15]
                for b in text_blocks:
                    if "Rs." not in b and "-" not in b:
                        name = b
                        break

            if not name: continue
            if product_url.startswith("//"): product_url = "https:" + product_url
            
            # Sale Price
            sale_price = 0.0
            sale_price_els = card.find_elements(By.CSS_SELECTOR, ".ooOxS, .jfy-product-card-price, .price")
            if sale_price_els:
                sale_price = extract_price(sale_price_els[0].text)
            else:
                rs_matches = re.findall(r'Rs\.\s?([\d,]+)', text)
                if rs_matches: sale_price = float(rs_matches[0].replace(',', ''))
            
            if sale_price == 0.0: continue
            
            # Original Price & Discount
            orig_price = sale_price
            discount = 0
            
            # Remove coins section
            clean_text = text
            coins_els = card.find_elements(By.CSS_SELECTOR, ".WNoq3, .coins")
            for c in coins_els: clean_text = clean_text.replace(c.text, "")
            
            disc_match = re.search(r'-(\d+)%', clean_text)
            if disc_match:
                discount = int(disc_match.group(1))
            
            # Look for another price (original)
            all_prices = re.findall(r'Rs\.\s?([\d,]+)', clean_text)
            price_vals = [float(p.replace(',', '')) for p in all_prices]
            if len(price_vals) > 1:
                others = [p for p in price_vals if abs(p - sale_price) > 5]
                if others:
                    orig_price = max(others)
                    if orig_price > sale_price:
                        calc_disc = int(((orig_price - sale_price) / orig_price) * 100)
                        discount = max(discount, calc_disc)
            
            if discount > 0 and orig_price == sale_price:
                orig_price = round(sale_price / (1 - (discount / 100)), 2)
            
            # Filter by discount
            if discount < MIN_DISCOUNT:
                continue

            # Rating & Reviews
            rating = 0.0
            reviews = 0
            review_match = re.search(r'\((\d+)\)', clean_text)
            if review_match: reviews = int(review_match.group(1))
            
            rating_attr = card.get_attribute("data-rating")
            if rating_attr: rating = float(rating_attr)

            # Image
            img_el = card.find_elements(By.CSS_SELECTOR, "img")
            image_url = ""
            if img_el:
                image_url = img_el[0].get_attribute("src") or img_el[0].get_attribute("data-src")
            
            # Badges
            badges = []
            if "Free Shipping" in clean_text: badges.append("Free Shipping")
            if "COD" in clean_text: badges.append("COD")
            html_content = card.get_attribute("outerHTML")
            if "mall" in html_content.lower(): badges.append("Daraz Mall")
            
            products.append({
                "name": name,
                "brand": "Unknown",
                "sale_price": sale_price,
                "original_price": orig_price,
                "discount_percentage": discount,
                "image_url": image_url,
                "product_url": product_url,
                "rating": rating,
                "reviews": reviews,
                "badges": badges,
                "timestamp": datetime.datetime.now().isoformat()
            })
        except Exception as e:
            continue
            
    return products

def main():
    driver = setup_driver()
    all_products = []
    try:
        for p in range(1, PAGES_TO_SCRAPE + 1):
            page_products = scrape_page(driver, p)
            all_products.extend(page_products)
            print(f"Current total valid products: {len(all_products)}")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=4)
        if all_products:
            avg_discount = sum(p['discount_percentage'] for p in all_products) / len(all_products)
            print("\nSCRAPING SUMMARY")
            print(f"Total Products: {len(all_products)}")
            print(f"Average Discount: {avg_discount:.2f}%")
        else:
            print("No valid products matching criteria found across first 3 pages.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
