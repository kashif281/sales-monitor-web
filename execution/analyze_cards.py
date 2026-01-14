import re

with open("electronics_search_debug.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find cards with discounts
cards = re.findall(r'<div class="Bm3ON".*?</div></div></div></div></div>', content, re.DOTALL)

print(f"Total cards found: {len(cards)}")

for i, card in enumerate(cards):
    price_wrapper = re.search(r'<div[^>]*class="[^"]*aBrP0[^"]*"[^>]*>(.*?)</div>', card, re.DOTALL)
    if price_wrapper:
        inner = price_wrapper.group(1)
        if "-" in inner or "Rs." in inner[inner.find("Rs.")+3:]:
            print(f"\n--- Card {i} ---")
            print(f"Wrapper Inner HTML: {inner}")
            print(f"Wrapper Text: {re.sub('<[^>]*>', ' ', inner).strip()}")
