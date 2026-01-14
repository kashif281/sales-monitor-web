import requests

def inspect():
    url = "https://www.daraz.pk/flash-sale/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        content = response.text
        print(f"Length of content: {len(content)}")
        
        # Look for likely data vars
        keywords = ["window.pageData", "flashSale", "sku", "price", "discount"]
        for kw in keywords:
            if kw in content:
                print(f"Found keyword: {kw}")
                # print snippet
                idx = content.find(kw)
                print(content[idx:idx+200])
        
        with open("daraz_raw.html", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
