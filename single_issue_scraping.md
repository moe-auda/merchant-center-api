# Merchant Center API - Single Issue Product Upload Script

## Overview
This script automates the process of scraping product information from PressReader URLs and uploading single-issue magazine/newspaper products to Google Merchant Center. It extracts structured data from web pages and creates product listings for e-commerce platforms.

## Features
- **Web Scraping**: Extracts schema.org JSON-LD data from PressReader URLs
- **Product Processing**: Filters for single-issue offers in specified currency
- **Google Merchant Center Integration**: Uploads products via Google Content API
- **Data Feed Management**: Creates and manages product feeds
- **Multi-currency Support**: Configurable target currency (USD, EUR, GBP, etc.)

## Prerequisites

### Required Files
1. **Service Account Key**: Google Cloud service account JSON file
   - Path: `/content/drive/MyDrive/Colab Notebooks/Merchant Center API/service_account_key.json` (this will change depending where we strore the json file)
   - Must have Content API permissions

2. **CSV File**: Contains URLs to scrape (this will change depending where we store the CSVs)
   - Path: `/content/Magazines-full.csv`
   - Must have a column named `"url"`

### Required Python Packages
```bash
pip install requests pandas beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Configuration

### Global Variables
```python
# Google Merchant Center Configuration
merchant_id = "5411908926"  # Your Merchant Center ID
SCOPES = ["https://www.googleapis.com/auth/content"]

# Target Market Configuration (this varaiable will change depending on which country/language we want)
target_country = "US"        # Target country code
target_language = "en"       # Target language code
publication_type = "Magazine" # "Magazine" or "Newspaper"

# Web Scraping Configuration
HEADERS = {
    "User-Agent": "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)"
}
```

## Core Functions

### 1. `extract_schema(url)`
**Purpose**: Scrapes a URL and extracts schema.org JSON-LD data

**Parameters**:
- `url` (str): The URL to scrape

**Returns**:
- `dict` or `None`: Product schema data if found, None otherwise

**Process**:
1. Makes HTTP request to the URL
2. Parses HTML with BeautifulSoup
3. Finds all `<script type="application/ld+json">` tags
4. Returns the first schema with `@type: "Product"`

### 2. `process_product_data(schema, target_currency)`
**Purpose**: Processes schema data to extract product information

**Parameters**:
- `schema` (dict): Schema.org product data
- `target_currency` (str): Target currency code (e.g., "USD")

**Returns**:
- `dict` or `None`: Formatted product data for Google Merchant Center

**Filters Applied**:
- Currency must match target currency
- Offer type must not be "Subscription"
- Price must not be zero
- Generates unique offer ID from URL structure

**Product Data Structure**:
```python
{
    "offerId": "unique-identifier",
    "title": "Product Name",
    "description": "Product Description",
    "imageLink": "Image URL",
    "link": "Product URL",
    "contentLanguage": "en",
    "targetCountry": "US",
    "channel": "online",
    "availability": "in stock",
    "price": {"value": "9.99", "currency": "USD"},
    "customLabel0": "Magazine - Single Issue - EN"
}
```

### 3. `upload_product(product_data)`
**Purpose**: Uploads product data to Google Merchant Center

**Parameters**:
- `product_data` (dict): Formatted product data

**Process**:
- Uses Google Content API to insert product
- Handles API errors gracefully

### 4. `create_data_source()`
**Purpose**: Creates a data feed in Google Merchant Center

**Process**:
- Checks for existing feeds with same name
- Creates new feed if not exists
- Configures feed for target country/language

### 5. `main(target_currency)`
**Purpose**: Main execution function

**Parameters**:
- `target_currency` (str): Currency code for product pricing

**Process**:
1. Reads CSV file with URLs
2. Creates data source feed
3. Iterates through each URL
4. Extracts and processes product data
5. Uploads valid products to Merchant Center

## Usage

### Basic Execution
```python
if __name__ == "__main__":
    main("USD")  # Upload products with USD pricing
```

### Supported Currencies
- `"USD"` - US Dollar
- `"EUR"` - Euro
- `"GBP"` - British Pound
- Any valid ISO 4217 currency code

## Error Handling

### Scraping Errors
- Network timeouts (10 seconds)
- Invalid JSON in schema data
- Missing schema.org data
- Non-Product schema types

### API Errors
- Authentication failures
- Rate limiting
- Invalid product data
- Duplicate product IDs

### Data Validation
- Zero-price products are skipped
- Subscription offers are filtered out
- Missing required fields are handled gracefully

## Logging and Monitoring

The script provides detailed step-by-step logging:
- **Step 1**: URL scraping initiation
- **Step 2**: Schema extraction and validation
- **Step 3**: Product data processing
- **Step 4**: Upload initiation
- **Step 5**: Upload completion/error

## Limitations and Considerations

### API Quotas
- Google Merchant Center API has rate limits
- Monitor quota usage in Google Cloud Console

### Data Quality
- Depends on quality of schema.org data on source websites
- Some URLs may not have structured data
- Price and availability may be outdated

### Scalability
- Processes URLs sequentially
- Consider batching for large datasets
- Add delays between requests to avoid rate limiting

## Troubleshooting

### Common Issues
1. **File Not Found**: Check file paths for service account and CSV
2. **Authentication Error**: Verify service account permissions
3. **Column Error**: Ensure CSV has "url" column
4. **API Quota Exceeded**: Wait and retry, or increase quota limits

### Debug Mode
Enable detailed logging by uncommenting debug print statements in the code.

## Security Notes
- Service account credentials should be kept secure
- Never commit API keys to version control
- Use environment variables for sensitive data in production

## Future Enhancements
- Add support for multiple currencies per product
- Implement retry logic for failed uploads
- Add data validation and cleaning
- Support for batch processing
- Integration with other e-commerce platforms

## File Structure
```
merchent_center_api/
├── Single issue script.py    # Main script file
├── README.md                 # This documentation
├── service_account_key.json  # Google Cloud credentials (not in repo)
└── Magazines-full.csv        # URL data file (not in repo)
```

## License
This project is for internal use. Please ensure compliance with Google's API terms of service and PressReader's terms of use. 