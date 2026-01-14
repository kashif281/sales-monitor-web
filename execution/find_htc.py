import re
with open("electronics_search_debug.html", "r", encoding="utf-8") as f:
    content = f.read()

# Split by card start
cards = content.split('<div class="Bm3ON"')
for i, card in enumerate(cards):
    if "HTC-1" in card:
        print(f"\n--- Card {i} contains HTC-1 ---")
        # Price
        price_ctx = re.search(r'<div[^>]*class="[^"]*aBrP0[^"]*"[^>]*>.*?</div>', card, re.DOTALL)
        if price_ctx:
            print(f"Price HTML: {price_ctx.group(0)}")
        # Check for discount badge string
        if "<span>-" in card:
            badge = re.search(r'<span>-\d+%.*?</span>', card)
            if badge: print(f"Badge: {badge.group(0)}")
        # Print first 200 chars of card to see if it's the right one
        print(f"Card start snippet: {card[:200]}")
