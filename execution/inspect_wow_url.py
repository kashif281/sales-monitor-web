import requests
import json
from urllib.parse import unquote

def inspect_new_url():
    url = "https://pages.daraz.pk/wow/gcp/route/daraz/pk/upr/router?hybrid=1&data_prefetch=true&prefetch_replace=1&at_iframe=1&wh_pid=%2Flazada%2Fchannel%2Fpk%2Fflashsale%2F7cdarZ6wBa&hide_h5_title=true&lzd_navbar_hidden=true&disable_pull_refresh=true&skuIds=655652080%2C924783262%2C119034689%2C924421704%2C271814546%2C272976334%2C655652081&spm=a2a0e.tm80335142.FlashSale.d_shopMore"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "https://www.daraz.pk/"
    }
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content = response.text
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(content)}")
        
        # Check if it's JSON
        try:
            data = response.json()
            print("Response is JSON!")
            print(json.dumps(data, indent=2)[:500])
        except:
            print("Response is NOT JSON. Checking first 500 chars:")
            print(content[:500])
            
        # Save to file for further inspection
        with open("daraz_wow_page.html", "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_new_url()
