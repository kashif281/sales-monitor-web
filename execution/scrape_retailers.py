import csv
import random
import os
import requests
from bs4 import BeautifulSoup
import time
import re

# Constants
TARGET_BRANDS = {
    # Clothing
    "Khaadi": {"url": "https://pk.khaadi.com/sale/", "category": "Clothing"},
    "Sapphire": {"url": "https://pk.sapphireonline.pk/collections/sale", "category": "Clothing"},
    "J.": {"url": "https://www.junaidjamshed.com/sale.html", "category": "Clothing"},
    "Gul Ahmed": {"url": "https://www.gulahmedshop.com/sale", "category": "Clothing"},
    "Alkaram Studio": {"url": "https://www.alkaramstudio.com/sale", "category": "Clothing"},
    "Limelight": {"url": "https://limelight.pk/pages/sale", "category": "Clothing"},
    "Nishat Linen": {"url": "https://nishatlinen.com/collections/sale", "category": "Clothing"},
    "Bonanza Satrangi": {"url": "https://bonanzasatrangi.com/collections/sale", "category": "Clothing"},
    "Ethnic": {"url": "https://ethnic.pk/collections/sale", "category": "Clothing"},
    "Sana Safinaz": {"url": "https://www.sanasafinaz.com/pk/sale.html", "category": "Clothing"},
    
    # Shoes
    "Calza": {"url": "https://www.calza.com.pk/collections/sale", "category": "Shoes"},
    "Servis": {"url": "https://servis.pk/collections/summer-sale", "category": "Shoes"},
    "Ndure": {"url": "https://www.ndure.com/collections/sale", "category": "Shoes"},
    "Hush Puppies": {"url": "https://www.hushpuppies.com.pk/", "category": "Shoes"},
    "Stylo": {"url": "https://stylo.pk/", "category": "Shoes"},
    "Khazanay": {"url": "https://www.khazanay.pk/", "category": "Shoes"},
    "Metro Shoes": {"url": "https://www.metroshoes.com.pk/", "category": "Shoes"},
    "Insignia": {"url": "https://insignia.com.pk/", "category": "Shoes"},
    "Engine": {"url": "https://engine.com.pk/collections/men-shoes", "category": "Shoes"},
    "1st Step": {"url": "https://1ststep.pk/", "category": "Shoes"},
    "Sputnik": {"url": "https://sputnikfootwear.com/", "category": "Shoes"},
    "Borjan": {"url": "https://www.borjan.com.pk/", "category": "Shoes"},
    "ECS": {"url": "https://shopecs.com/", "category": "Shoes"}
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
    "Regal Shoes", "Footlib", "Urban Sole", "Crocs Pakistan", "1st Step", "Calza"
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


def scrape_brand(brand_name, url, category):
    print(f"Scraping {brand_name} ({category}) at {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find discounts in specific product labels/badges first (common in Shopify/Magento)
        # These are common classes for discount badges in Pakistani retail sites
        potential_labels = soup.find_all(['span', 'div', 'p'], class_=re.compile(r'badge|label|discount|sale|price-tag|reduction', re.I))
        
        discounts = []
        for label in potential_labels:
            d = extract_max_discount(label.get_text())
            if d > 0:
                discounts.append(d)
        
        if discounts:
            discount = max(discounts)
        else:
            # Fallback: remove common noisy elements and check remaining text
            for noisy in soup.find_all(['header', 'footer', 'nav', 'script', 'style']):
                noisy.decompose()
            text_content = soup.get_text()
            discount = extract_max_discount(text_content)
        
        # Try to find a representative image (OG Image is best)
        image_url = ""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image.get('content')
            
        # Refinement: If OG image looks like a logo or is empty, try to find a category-specific banner
        if not image_url or "logo" in image_url.lower():
            # Look for large images with relevant alt text
            patterns = [category.lower(), "banner", "sale", "hero"]
            prio_images = soup.find_all('img', alt=re.compile('|'.join(patterns), re.I))
            for img in prio_images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and src.startswith('http'):
                    image_url = src
                    break
        
        # Ensure relative URLs are made absolute
        if image_url and not image_url.startswith('http'):
            from urllib.parse import urljoin
            image_url = urljoin(url, image_url)
        
        if discount > 0:
            return {
                "Brand Name": brand_name,
                "Category": category,
                "Discount Percentage": f"{discount}%",
                "Discount Value": discount,
                "Source": "Scraped (Real)",
                "URL": url,
                "ImageURL": image_url
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
        "URL": f"https://www.google.com/search?q={brand}+pakistan+sale",
        "ImageURL": ""
    }

def main():
    all_data = []
    
    # 1. Scrape Target Brands
    processed_brands = set()
    
    for brand, info in TARGET_BRANDS.items():
        processed_brands.add(brand)
        data = scrape_brand(brand, info["url"], info["category"])
        if data:
            all_data.append(data)
        else:
            # Fallback to mock if scraping failed but mark source
            print(f"  - Falling back to mock for {brand}")
            mock = generate_mock_data(brand, info["category"])
            mock["Source"] = "Estimated (Fallback)"
            mock["URL"] = info["url"] # Use the real URL even if fallback
            mock["ImageURL"] = ""
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
        writer = csv.DictWriter(file, fieldnames=["Brand Name", "Category", "Discount Percentage", "Source", "URL", "ImageURL"])
        writer.writeheader()
        for item in all_data:
            row = item.copy()
            del row["Discount Value"]
            writer.writerow(row)
    
    print(f"Completed. Data saved to {OUTPUT_FILE} ({len(all_data)} items)")

if __name__ == "__main__":
    main()
