import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Search URL is often more reliable for catalog scraping
TARGET_URL = "https://www.daraz.pk/catalog/?q=electronics"
DEBUG_FILE = "electronics_search_debug.html"

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    
    # Modern Desktop UA
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Randomize window size slightly
    options.add_argument(f"--window-size={random.randint(1200, 1920)},{random.randint(800, 1080)}")
    
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

def inspect_page():
    driver = setup_driver()
    try:
        print(f"Navigating to {TARGET_URL}...")
        driver.get(TARGET_URL)
        
        # Random sleep to mimic human
        time.sleep(random.uniform(10, 15)) 
        
        print(f"Page Title: {driver.title}")
        
        # Human-like scrolling
        for i in range(3):
            scroll_dist = random.randint(300, 700)
            driver.execute_script(f"window.scrollBy(0, {scroll_dist});")
            print(f"Scrolled {scroll_dist}px...")
            time.sleep(random.uniform(2, 4))

        print("Dumping HTML...")
        with open(DEBUG_FILE, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        # Check if products exist
        items = driver.find_elements(By.CSS_SELECTOR, "[data-qa-locator='product-item'], .gridItem, .box--2I2a")
        print(f"Found {len(items)} items by selector.")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_page()
