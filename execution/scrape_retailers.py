import csv
import random
import os
import requests
from bs4 import BeautifulSoup
import time
import re

# Constants
TARGET_BRANDS = {
    "Khaadi": "https://pk.khaadi.com/sale/",
    "Sapphire": "https://pk.sapphireonline.pk/collections/sale",
    "J.": "https://www.junaidjamshed.com/sale.html",
    "Gul Ahmed": "https://www.gulahmedshop.com/sale",
    "Alkaram Studio": "https://www.alkaramstudio.com/sale",
    "Limelight": "https://limelight.pk/pages/sale",
    "Nishat Linen": "https://nishatlinen.com/collections/sale",
    "Bonanza Satrangi": "https://bonanzasatrangi.com/collections/sale",
    "Ethnic": "https://ethnic.pk/collections/sale",
    "Sana Safinaz": "https://www.sanasafinaz.com/pk/sale.html"
}

# Remaining brands to mock
ALL_CLOTHING = [
    "Khaadi", "Gul Ahmed", "J.", "Sapphire", "Alkaram Studio",
    "Nishat Linen", "Maria.B", "Outfitters", "Bonanza Satrangi", "Ethnic",
    "Limelight", "Sana Safinaz", "BeechTree", "Cross Stitch", "Generation",
    "Zellbury", "So Kamal", "Warda", "Saya", "Rang Ja"
]

ALL_SHOES = [
    "Bata", "Servis", "Stylo", "Borjan", "Unze London",
    "Ndure", "Insignia", "Mociani", "Hush Puppies", "Metro Shoes",
    "ECS", "WalkEaze", "Starlet", "Logo", "Sputnik",
    "Regal Shoes", "Footlib", "Urban Sole", "Crocs Pakistan", "1st Step"
]

OUTPUT_FILE = ".tmp/live_retail_sales.csv"

def extract_max_discount(text):
    """
    Finds the highest integer X in strings like "X% OFF", "Flat X%", "Up to X%".
    """
    if not text:
        return 0
    
    # Look for [number]% pattern
    matches = re.findall(r'(\d{1,2})%', text)
    if not matches:
        return 0
    
    # Convert to ints and find max
    values = [int(m) for m in matches]
    return max(values) if values else 0


def scrape_brand(brand_name, url):
    print(f"Scraping {brand_name} at {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()
        
        # Heuristic: Find max discount mentioned on page
        discount = extract_max_discount(text_content)
        
        if discount > 0:
            return {
                "Brand Name": brand_name,
                "Category": "Clothing", # Assuming targets are mainly clothing
                "Discount Percentage": f"{discount}%",
                "Discount Value": discount,
                "Source": "Scraped (Real)",
                "URL": url
            }
        else:
            print(f"  - No discount pattern found for {brand_name}")
            return None

    except Exception as e:
        print(f"  - Failed to scrape {brand_name}: {e}")
        return None


def generate_mock_data(brand, category):
    discount = random.randint(10, 70)
    # Default URL to Google Search for the brand if no specific URL known
    return {
        "Brand Name": brand,
        "Category": category,
        "Discount Percentage": f"{discount}%",
        "Discount Value": discount,
        "Source": "Estimated",
        "URL": f"https://www.google.com/search?q={brand}+pakistan+sale"
    }

def main():
    all_data = []
    
    # 1. Scrape Target Brands
    processed_brands = set()
    
    for brand, url in TARGET_BRANDS.items():
        processed_brands.add(brand)
        data = scrape_brand(brand, url)
        if data:
            all_data.append(data)
        else:
            # Fallback to mock if scraping failed but mark source
            print(f"  - Falling back to mock for {brand}")
            mock = generate_mock_data(brand, "Clothing")
            mock["Source"] = "Estimated (Fallback)"
            mock["URL"] = url # Use the real URL even if fallback
            all_data.append(mock)

    # 2. Add Remaining Clothing Brands
    for brand in ALL_CLOTHING:
        if brand not in processed_brands:
            all_data.append(generate_mock_data(brand, "Clothing"))

    # 3. Add Shoe Brands (All mock for now as none in Target list)
    for brand in ALL_SHOES:
        if brand not in processed_brands:
            all_data.append(generate_mock_data(brand, "Shoes"))

    # 4. Sort: Prioritize "Real" source, then by Discount Value
    all_data.sort(key=lambda x: (
        0 if "Real" in x["Source"] else 1, 
        -x["Discount Value"]
    ))

    # 5. Write
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Brand Name", "Category", "Discount Percentage", "Source", "URL"])
        writer.writeheader()
        for item in all_data:
            row = item.copy()
            del row["Discount Value"]
            writer.writerow(row)
    
    print(f"Completed. Data saved to {OUTPUT_FILE} ({len(all_data)} items)")

if __name__ == "__main__":
    main()
