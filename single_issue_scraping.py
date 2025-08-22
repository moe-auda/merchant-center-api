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

# Your Merchant Center ID
merchant_id = "5411908926"

# Headers for scraping
HEADERS = {
    "User-Agent": "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)"
}

# Configuration for different regions and their CSV files
REGION_CONFIGS = {
    # Magazines
    "Magazines-US": {
        "csv_file": "csvs/Magazines-full.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Magazine"
    },
    "Magazines-DE": {
        "csv_file": "csvs/Magazines-de.csv",
        "target_country": "DE",
        "target_language": "de",
        "publication_type": "Magazine"
    },
    "Magazines-IT": {
        "csv_file": "csvs/Magazines-it.csv",
        "target_country": "IT",
        "target_language": "it",
        "publication_type": "Magazine"
    },
    "Magazines-FR": {
        "csv_file": "csvs/Magazines-fr.csv",
        "target_country": "FR",
        "target_language": "fr",
        "publication_type": "Magazine"
    },
    "Magazines-ES": {
        "csv_file": "csvs/Magazines-es.csv",
        "target_country": "ES",
        "target_language": "es",
        "publication_type": "Magazine"
    },
    "Magazines-BR": {
        "csv_file": "csvs/Magazines-pt-br.csv",
        "target_country": "BR",
        "target_language": "pt",
        "publication_type": "Magazine"
    },
    "Magazines-TR": {
        "csv_file": "csvs/Magazines-tr.csv",
        "target_country": "TR",
        "target_language": "tr",
        "publication_type": "Magazine"
    },
    "Magazines-RU": {
        "csv_file": "csvs/Magazines-ru.csv",
        "target_country": "RU",
        "target_language": "ru",
        "publication_type": "Magazine"
    },
    "Magazines-JP": {
        "csv_file": "csvs/Magazines-ja.csv",
        "target_country": "JP",
        "target_language": "ja",
        "publication_type": "Magazine"
    },
    # Newspapers
    "Newspapers-US": {
        "csv_file": "csvs/Newspapers-full.csv",
        "target_country": "US",
        "target_language": "en",
        "publication_type": "Newspaper"
    },
    "Newspapers-DE": {
        "csv_file": "csvs/Newspapers-de.csv",
        "target_country": "DE",
        "target_language": "de",
        "publication_type": "Newspaper"
    },
    "Newspapers-IT": {
        "csv_file": "csvs/Newspapers-it.csv",
        "target_country": "IT",
        "target_language": "it",
        "publication_type": "Newspaper"
    },
    "Newspapers-FR": {
        "csv_file": "csvs/Newspapers-fr.csv",
        "target_country": "FR",
        "target_language": "fr",
        "publication_type": "Newspaper"
    },
    "Newspapers-ES": {
        "csv_file": "csvs/Newspapers-es.csv",
        "target_country": "ES",
        "target_language": "es",
        "publication_type": "Newspaper"
    },
    "Newspapers-BR": {
        "csv_file": "csvs/Newspapers-pt-br.csv",  
        "target_country": "BR",
        "target_language": "pt",
        "publication_type": "Newspaper"
    },
    "Newspapers-TR": {
        "csv_file": "csvs/Newspapers-tr.csv",
        "target_country": "TR",
        "target_language": "tr",
        "publication_type": "Newspaper"
    },
    "Newspapers-RU": {
        "csv_file": "csvs/Newspapers-ru.csv",
        "target_country": "RU",
        "target_language": "ru",
        "publication_type": "Newspaper"
    },
    "Newspapers-JP": {
        "csv_file": "csvs/Newspapers-ja.csv",
        "target_country": "JP",
        "target_language": "ja",
        "publication_type": "Newspaper"
    }
}

# Extract schema.org JSON-LD, selecting only Product type
def extract_schema(url):
    print(f"Step 1: Scraping URL: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
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
        print("Step 2: No Product schema found among scripts")
        return None
    except Exception as e:
        print(f"Step 2: Could not scrape {url}: {e}")
        return None

# Process schema to get product data (first single-issue offer in target currency)
def process_product_data(schema, target_currency, target_country, target_language, publication_type):
    if not schema:
        print("Step 3: No schema provided")
        return None
    print(f"Step 3: Processing schema: {json.dumps(schema, indent=2, ensure_ascii=False)}")

    if schema.get("@type") != "Product":
        print(f"Step 3: Invalid type: {schema.get('@type')}")
        return None

    offers = schema.get("offers", [])
    if isinstance(offers, dict):
        offers = [offers]
    print(f"Step 3: Offers: {offers}")

    # Pick the first single-issue offer in the target currency
    for offer in offers:
        offer_name = offer.get("name", "")
        offer_currency = offer.get("priceCurrency", "")
        offer_type = offer.get("offerType", "")  # Check for subscription
        print(f"Step 3: Checking offer - Name: {offer_name}, Currency: {offer_currency}, Type: {offer_type}")
        if offer_currency == target_currency and offer_type != "Subscription":
            price = offer.get("price")
            # Skip if price is zero
            if str(price) in ["0", "0.0", "0.00"]:
                print(f"Step 3: Skipping product '{offer_name}' - Price is zero")
                return None
            # Proceed with non-zero price
            url_parts = offer.get("url", "").split("/")
            last_segment = url_parts[-1]  # e.g., "the-boston-globe"
            locale_code = ""
            content_types = ["newspapers", "magazines"]
            for i, part in enumerate(url_parts):
                if "pressreader.com" in url_parts[i-1] and part not in content_types and i+1 < len(url_parts) and url_parts[i+1] in content_types:
                    locale_code = part
                    break
            offer_id = f"{locale_code}-{last_segment}" if locale_code else last_segment
            product_data = {
                "offerId": offer_id,
                "title": offer_name,
                "description": schema.get("description", ""),
                "imageLink": schema.get("image", "https://via.placeholder.com/150"),
                "link": offer.get("url"),
                "contentLanguage": target_language,
                "targetCountry": target_country,
                "channel": "online",
                "availability": "in stock",
                "price": {"value": str(price), "currency": offer_currency},
                "customLabel0": f"{publication_type} - Single Issue - {target_language.upper()}"
            }
            print(f"Step 3: Processed product data - Title: {product_data['title']}, Custom Label: {product_data['customLabel0']}")
            return product_data
    print(f"Step 3: No {target_currency} single-issue offer found")
    return None

# Upload product to Google Merchant Center
def upload_product(product_data):
    print(f"Step 4: Starting upload for {product_data['title']}")
    try:
        service.products().insert(merchantId=merchant_id, body=product_data).execute()
        print(f"Step 5: Successfully uploaded: {product_data['title']}")
    except Exception as e:
        print(f"Step 5: Failed to upload {product_data['title']}: {e}")

# Create a feed for the target country
def create_data_source(target_country, target_language, publication_type):
    feed_name = f"PressReader Feed - {target_country}"
    print(f"Creating feed for {target_country}...")
    try:
        existing_feeds = service.datafeeds().list(merchantId=merchant_id).execute()
        if any(feed["name"] == feed_name for feed in existing_feeds.get("resources", [])):
            print(f"Feed '{feed_name}' already exists")
            return

        service.datafeeds().insert(
            merchantId=merchant_id,
            body={
                "name": feed_name,
                "contentType": "products",
                "fileName": f"{publication_type} - Single Issue - {target_country}.csv",
                "targets": [
                    {"country": target_country, "language": target_language, "includedDestinations": ["Shopping"]}
                ]
            }
        ).execute()
        print(f"Created feed: {feed_name} targeting {target_country}")
    except Exception as e:
        print(f"Failed to create feed: {e}")

# Process a single region
def process_region(region_code, config, target_currency):
    print(f"\n{'='*60}")
    print(f"Processing Region: {region_code}")
    print(f"CSV File: {config['csv_file']}")
    print(f"Target Country: {config['target_country']}")
    print(f"Target Language: {config['target_language']}")
    print(f"Publication Type: {config['publication_type']}")
    print(f"{'='*60}")
    
    try:
        df = pd.read_csv(config['csv_file'])
        create_data_source(config['target_country'], config['target_language'], config['publication_type'])

        print(f"\nStarting URL processing for {region_code} with target currency: {target_currency}...\n")
        for i, url in enumerate(df["url"], 1):
            print(f"--- Processing URL {i} of {len(df['url'])} for {region_code} ---")
            schema = extract_schema(url)
            product_data = process_product_data(schema, target_currency, config['target_country'], config['target_language'], config['publication_type'])
            if product_data:
                upload_product(product_data)
            print(f"--- Finished URL {i} for {region_code} ---\n")
            
    except FileNotFoundError:
        print(f"Warning: CSV file {config['csv_file']} not found. Skipping region {region_code}.")
    except Exception as e:
        print(f"Error processing region {region_code}: {e}")

# Main function with required currency parameter
def main(target_currency):
    print(f"Starting multi-region processing with currency: {target_currency}")
    print(f"Processing {len(REGION_CONFIGS)} regions...")
    
    for region_code, config in REGION_CONFIGS.items():
        process_region(region_code, config, target_currency)

if __name__ == "__main__":
    # Specify your desired currency here (required)
    main("USD")  # Must provide a currency, e.g., "EUR", "GBP", "USD"