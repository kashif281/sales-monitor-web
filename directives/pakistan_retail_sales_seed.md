# Directive: Generate Pakistan Retail Sales Seed Data

## Goal
Create a structured seed file containing 20 famous clothing brands and 20 famous shoe brands in Pakistan with placeholder discount values, sorted by highest discount.

## Inputs
- List of 20 Famous Clothing Brands (Hardcoded in script for Phase 1)
- List of 20 Famous Shoe Brands (Hardcoded in script for Phase 1)

## Tools / Scripts
- `execution/generate_seed_data.py`

## Process
1.  **Define Brands**: The script will contain lists of brand names.
2.  **Generate Data**:
    - Assign random discount percentages (0-70%) to each brand.
    - Tag each with its Category (Clothing or Shoes).
3.  **Sort**: Sort the combined list by Discount Percentage in descending order.
4.  **Output**: Write the result to `.tmp/pakistan_retail_sales_seed.csv`.

## Output
- File: `.tmp/pakistan_retail_sales_seed.csv`
- Format: CSV
- Columns: `Brand Name`, `Category`, `Discount Percentage`

## Edge Cases
- Ensure no duplicate brand names if possible (though manual list should prevent this).
- Ensure discounts are integers between 0 and 70.