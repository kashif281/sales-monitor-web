import csv
import random
import os

# Constants
CLOTHING_BRANDS = [
    "Khaadi", "Gul Ahmed", "J.", "Sapphire", "Alkaram Studio",
    "Nishat Linen", "Maria.B", "Outfitters", "Bonanza Satrangi", "Ethnic",
    "Limelight", "Sana Safinaz", "BeechTree", "Cross Stitch", "Generation",
    "Zellbury", "So Kamal", "Warda", "Saya", "Rang Ja"
]

SHOE_BRANDS = [
    "Bata", "Servis", "Stylo", "Borjan", "Unze London",
    "Ndure", "Insignia", "Mociani", "Hush Puppies", "Metro Shoes",
    "ECS", "WalkEaze", "Starlet", "Logo", "Sputnik",
    "Regal Shoes", "Footlib", "Urban Sole", "Crocs Pakistan", "1st Step"
]

OUTPUT_FILE = ".tmp/pakistan_retail_sales_seed.csv"

def generate_data():
    data = []

    # Process Clothing Brands
    for brand in CLOTHING_BRANDS:
        discount = random.randint(0, 70)
        data.append({
            "Brand Name": brand,
            "Category": "Clothing",
            "Discount Percentage": f"{discount}%",
            "Discount Value": discount # Helper for sorting
        })

    # Process Shoe Brands
    for brand in SHOE_BRANDS:
        discount = random.randint(0, 70)
        data.append({
            "Brand Name": brand,
            "Category": "Shoes",
            "Discount Percentage": f"{discount}%",
            "Discount Value": discount # Helper for sorting
        })

    # Sort by Discount Value descending
    data.sort(key=lambda x: x["Discount Value"], reverse=True)

    # Remove helper key
    for item in data:
        del item["Discount Value"]

    return data

def write_csv(data):
    # Ensure .tmp directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Brand Name", "Category", "Discount Percentage"])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Successfully generated seed data at {OUTPUT_FILE}")

if __name__ == "__main__":
    sales_data = generate_data()
    write_csv(sales_data)
