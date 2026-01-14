from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def debug_mobile():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=375,812")
    options.add_argument("--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        url = "https://www.daraz.pk/shop-electronics/"
        print(f"Navigating to {url}")
        driver.get(url)
        time.sleep(10)
        
        with open("mobile_category_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Dumped mobile_category_debug.html")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_mobile()
