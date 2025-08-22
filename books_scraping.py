import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Merchant Center API Setup
SERVICE_ACCOUNT_FILE = "service_account_key.json"
SCOPES = ["https://www.googleapis.com/auth/content"]
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build("content", "v2.1", credentials=credentials)

merchant_id = "5411908926"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Naverbot/1.0; +http://naver.com/bot)"}

# Configuration for different regions and their settings
REGION_CONFIGS = {
    "Book1": {
        "csv_file": "csvs/Book1.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book2": {
        "csv_file": "csvs/Book2.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book3": {
        "csv_file": "csvs/Book3.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book4": {
        "csv_file": "csvs/Book4.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book5": {
        "csv_file": "csvs/Book5.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book6": {
        "csv_file": "csvs/Book6.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book7": {
        "csv_file": "csvs/Book7.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    },
    "Book8": {
        "csv_file": "csvs/Book8.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Book",
        "region": "US"
    }
}

# US IP for explicit US region requests
US_IP = "104.131.0.1"  # Example US IP (e.g., New York)

def extract_schema(url, region):
    print(f"Step 1: Scraping URL: {url} from region: {region}")
    try:
        # Set headers
        headers = HEADERS.copy()
        headers["Accept-Language"] = "en-US" if region == "US" else "en-CA"
        if region == "US":
            headers["X-Forwarded-For"] = US_IP  # Only set US IP for explicit US region
        print(f"Headers: {headers}")  # Log headers for debugging
        session = requests.Session()  # Use fresh session to avoid cookie persistence
        response = session.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        print(f"Response URL: {response.url}")  # Log response URL
        soup = BeautifulSoup(response.text, "html.parser", from_encoding="utf-8")
        script_tags = soup.find_all("script", type="application/ld+json")
        if not script_tags:
            print("Step 2: No JSON-LD scripts found")
            return None

        for i, script in enumerate(script_tags, 1):
            try:
                script_text = script.string.encode().decode('utf-8')
                data = json.loads(script_text)
                print(f"Step 2: Found schema {i}: {json.dumps(data, indent=2, ensure_ascii=False)}")
                if data.get("@type") == "Product":
                    print(f"Step 2: Selected Product schema {i}")
                    return data
            except json.JSONDecodeError:
                print(f"Step 2: Schema {i} is invalid JSON")
        print("Step 2: No Product schema found")
        return None
    except Exception as e:
        print(f"Step 2: Could not scrape {url} from {region}: {e}")
        return None

def process_product_data(schema, target_country, target_language, publication_type):
    if not schema:
        print("Step 3: No schema provided")
        return None
    print(f"Step 3: Processing schema: {json.dumps(schema, indent=2, ensure_ascii=False)}")

    if schema.get("@type") != "Product":
        print(f"Step 3: Invalid type: {schema.get('@type')}, expected Product")
        return None

    offers = schema.get("offers", {})
    if not isinstance(offers, dict):
        print("Step 3: Invalid offers format for Product schema")
        return None

    offer = offers
    title = schema.get("name", "")
    description = schema.get("description", "No description available")
    image_link = schema.get("image", "https://via.placeholder.com/150")
    gtin = schema.get("gtin13", "")
    brand = schema.get("brand", {}).get("name", "")
    url = offer.get("url", "")

    offer_currency = offer.get("priceCurrency", "")
    price = offer.get("price")
    print(f"Step 3: Processing offer - Name: {title}, Currency: {offer_currency}, Price: {price}")

    if str(price) in ["0", "0.0", "0.00"]:
        print(f"Step 3: Skipping product '{title}' - Price is zero")
        return None

    url_parts = url.split("/")
    last_segment = url_parts[-1]
    locale_code = ""
    content_types = ["books"]
    for i, part in enumerate(url_parts):
        if "pressreader.com" in url_parts[i-1] and part not in content_types and i+1 < len(url_parts) and url_parts[i+1] in content_types:
            locale_code = part
            break
    offer_id = f"{locale_code}-{last_segment}" if locale_code else last_segment
    product_data = {
        "offerId": offer_id,
        "title": title,
        "description": description,
        "imageLink": image_link,
        "link": url,
        "contentLanguage": target_language,
        "targetCountry": target_country,
        "channel": "online",
        "availability": "in stock",
        "price": {"value": str(price), "currency": offer_currency},
        "gtin": gtin,
        "brand": brand,
        "customLabel0": f"{publication_type} - {target_language.upper()}"
    }
    print(f"Step 3: Processed product data - Title: {product_data['title']}, Currency: {offer_currency}")
    return product_data

def upload_product(product_data):
    print(f"Step 4: Starting upload for {product_data['title']}")
    try:
        service.products().insert(merchantId=merchant_id, body=product_data).execute()
        print(f"Step 5: Successfully uploaded: {product_data['title']}")
    except Exception as e:
        print(f"Step 5: Failed to upload {product_data['title']}: {e}")

# Process a single region
def process_region(region_code, config):
    print(f"\n{'='*60}")
    print(f"Processing Region: {region_code}")
    print(f"CSV File: {config['csv_file']}")
    print(f"Target Country: {config['target_country']}")
    print(f"Target Language: {config['target_language']}")
    print(f"Publication Type: {config['publication_type']}")
    print(f"Region: {config['region']}")
    print(f"{'='*60}")
    
    try:
        df = pd.read_csv(config['csv_file'])

        print(f"\nStarting URL processing from region: {config['region']}...\n")
        for i, url in enumerate(df["url"], 1):
            print(f"--- Processing URL {i} of {len(df['url'])} for {region_code} ---")
            schema = extract_schema(url, config['region'])
            product_data = process_product_data(schema, config['target_country'], config['target_language'], config['publication_type'])
            if product_data:
                upload_product(product_data)
            print(f"--- Finished URL {i} for {region_code} ---\n")
            
    except FileNotFoundError:
        print(f"Warning: CSV file {config['csv_file']} not found. Skipping region {region_code}.")
    except Exception as e:
        print(f"Error processing region {region_code}: {e}")

def main():
    print(f"Starting multi-region processing for books")
    print(f"Processing {len(REGION_CONFIGS)} regions...")
    
    for region_code, config in REGION_CONFIGS.items():
        process_region(region_code, config)

if __name__ == "__main__":
    main()  # Books script doesn't need currency parameter