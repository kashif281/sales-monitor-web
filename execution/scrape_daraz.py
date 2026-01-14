import json
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

# Configuration
# URL provided by user
TARGET_URL = "https://pages.daraz.pk/wow/gcp/route/daraz/pk/upr/router?hybrid=1&data_prefetch=true&prefetch_replace=1&at_iframe=1&wh_pid=%2Flazada%2Fchannel%2Fpk%2Fflashsale%2F7cdarZ6wBa&hide_h5_title=true&lzd_navbar_hidden=true&disable_pull_refresh=true&skuIds=655652080%2C924783262%2C119034689%2C924421704%2C271814546%2C272976334%2C655652081&spm=a2a0e.tm80335142.FlashSale.d_shopMore"

OUTPUT_FILE = "daraz_flash_sales.json"
MIN_DISCOUNT = 40

def setup_driver():
    options = Options()
    # options.add_argument("--headless") 
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=375,812") # Mobile viewport
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")
    
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

def extract_from_mobile_card(card):
    try:
        html = card.get_attribute('outerHTML')
        
        # 1. IDs and URL
        item_id = card.get_attribute("itemid")
        sku_id = card.get_attribute("skuid")
        
        product_url = ""
        if item_id and sku_id:
            product_url = f"https://www.daraz.pk/products/-i{item_id}-s{sku_id}.html"
        elif item_id:
            product_url = f"https://www.daraz.pk/products/-i{item_id}.html"
        else:
            # Check for anchor tag
            try:
                a_tag = card.find_element(By.TAG_NAME, "a")
                product_url = a_tag.get_attribute("href")
            except:
                product_url = ""

        # 2. Image
        img_url = ""
        try:
            img = card.find_element(By.CSS_SELECTOR, ".picture-wrapper img")
            img_url = img.get_attribute("src")
        except:
            # Fallback
            try:
                img = card.find_element(By.TAG_NAME, "img")
                img_url = img.get_attribute("src")
            except: pass
            
        if not img_url:
             # Check trackinfo which often has image or other metadata
             pass

        # 3. Prices and Discount
        # Prefer specific classes from analysis
        try:
            # Sale Price
            s_price_el = card.find_element(By.CSS_SELECTOR, ".i-product-discount-price-text")
            price = float(s_price_el.text.replace(',', '').strip())
        except:
            # Regex fallback
            hits = re.findall(r'Rs\.?\s?([\d,]+)', card.text)
            price = float(hits[0].replace(',', '')) if hits else 0.0

        try:
             # Original Price (often in .base-default-text)
             # Note: debug html showed <div class="... base-default-text default-title">Rs.2,799</div>
             o_text = card.find_element(By.CSS_SELECTOR, ".base-default-text").text
             orig_price = float(re.search(r'[\d,]+', o_text).group().replace(',', ''))
        except:
             orig_price = price

        try:
            # Discount
            d_text = card.find_element(By.CSS_SELECTOR, ".item-discount").text
            discount = int(re.search(r'\d+', d_text).group())
        except:
            if orig_price > price:
                discount = int(((orig_price - price) / orig_price) * 100)
            else:
                discount = 0

        if discount < MIN_DISCOUNT:
            return None
        
        # 4. Name
        # Since name is missing in this view, we use ID or "Flash Sale Item"
        name = f"Flash Sale Product {item_id}" if item_id else "Flash Sale Item"


        return {
            "name": name,
            "flash_sale_price": price,
            "original_price": orig_price,
            "discount_percentage": discount,
            "product_url": product_url or TARGET_URL,
            "image_url": img_url,
            "item_id": item_id,
            "sku_id": sku_id,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        # print(f"Error: {e}")
        return None

def scrape():
    driver = setup_driver()
    products = []
    
    try:
        print(f"Navigating to {TARGET_URL[:50]}...")
        driver.get(TARGET_URL)
        time.sleep(10) # Heavy wait
        
        # Scroll a bit
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)

        # Primary mobile classes: .top-module-fashion-item or .flash-unit
        potential_cards = driver.find_elements(By.CSS_SELECTOR, ".top-module-fashion-item, .flash-unit")
        
        if not potential_cards:
             potential_cards = driver.find_elements(By.XPATH, "//*[contains(text(), 'Rs.')]/ancestor::div[contains(@class, 'unit') or contains(@class, 'item') or contains(@class, 'card')][1]")

        print(f"Found {len(potential_cards)} potential cards.")

        for card in potential_cards:
            data = extract_from_mobile_card(card)
            if data:
                products.append(data)
                
        print(f"Extracted {len(products)} valid products.")
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(products, f, indent=4)
            
    except Exception as e:
        print(f"Fatal Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape()
