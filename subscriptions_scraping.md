# PressReader Subscriptions Scraping Script

## Overview
This script automates the process of scraping subscription product information from PressReader URLs and uploading them to Google Merchant Center. It specifically targets subscription offers for newspapers and magazines, extracting structured data from web pages and creating product listings for e-commerce platforms.

## Features
- **Web Scraping**: Extracts schema.org JSON-LD data from PressReader URLs
- **Subscription Filtering**: Specifically targets subscription offers (not single issues)
- **Google Merchant Center Integration**: Uploads products via Google Content API
- **Data Feed Management**: Creates and manages product feeds
- **Multi-currency Support**: Configurable target currency (USD, EUR, GBP, etc.)
- **Publication Type Support**: Handles both Newspapers and Magazines

## Prerequisites

### Required Files
1. **Service Account Key**: Google Cloud service account JSON file
   - Path: `/content/drive/MyDrive/Colab Notebooks/Merchant Center API/service_account_key.json`
   - Must have Content API permissions

2. **CSV File**: Contains URLs to scrape (this will change depending where we store the CSVs)
   - Path: `/content/Newspapers-full.csv`
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
publication_type = "Newspaper" # "Newspaper" or "Magazine"

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
1. Makes HTTP request to the URL with 10-second timeout
2. Parses HTML with BeautifulSoup using UTF-8 encoding
3. Finds all `<script type="application/ld+json">` tags
4. Returns the first schema with `@type: "Product"`
5. Provides detailed logging of found schemas

### 2. `process_product_data(schema, target_currency)`
**Purpose**: Processes schema data to extract subscription product information

**Parameters**:
- `schema` (dict): Schema.org product data
- `target_currency` (str): Target currency code (e.g., "USD")

**Returns**:
- `dict` or `None`: Formatted product data for Google Merchant Center

**Filters Applied**:
- Currency must match target currency
- Offer type must be "Subscription" (explicitly targets subscriptions)
- Generates unique offer ID from URL structure with "-sub" suffix
- Extracts locale code from URL path

**Product Data Structure**:
```python
{
    "offerId": "locale-lastsegment-sub",
    "title": "Subscription Name",
    "description": "Product Description",
    "imageLink": "Image URL",
    "link": "Subscription URL",
    "contentLanguage": "en",
    "targetCountry": "US",
    "channel": "online",
    "availability": "in stock",
    "price": {"value": "19.99", "currency": "USD"},
    "customLabel0": "Newspaper - Subscription - EN"
}
```

### 3. `upload_product(product_data)`
**Purpose**: Uploads product data to Google Merchant Center

**Parameters**:
- `product_data` (dict): Formatted product data

**Process**:
- Uses Google Content API to insert product
- Handles API errors gracefully with detailed error logging

### 4. `create_data_source()`
**Purpose**: Creates a data feed in Google Merchant Center

**Process**:
- Checks for existing feeds with name "PressReader Feed 2"
- Creates new feed if not exists
- Configures feed for target country/language
- Sets up Shopping destination targeting

**Feed Configuration**:
```python
{
    "name": "PressReader Feed 2",
    "contentType": "products",
    "fileName": "Newspaper - Subscription - US.csv",
    "targets": [
        {
            "country": "US",
            "language": "en",
            "includedDestinations": ["Shopping"]
        }
    ]
}
```

### 5. `main(target_currency)`
**Purpose**: Main execution function

**Parameters**:
- `target_currency` (str): Currency code for product pricing

**Process**:
1. Reads CSV file with URLs
2. Creates data source feed
3. Iterates through each URL with progress tracking
4. Extracts and processes product data
5. Uploads valid subscription products to Merchant Center
6. Adds 1-second delay between requests

## Usage

### Basic Execution
```python
if __name__ == "__main__":
    main("USD")  # Upload subscription products with USD pricing
```

### Supported Currencies
- `"USD"` - US Dollar
- `"EUR"` - Euro
- `"GBP"` - British Pound
- Any valid ISO 4217 currency code

### Publication Types
- `"Newspaper"` - For newspaper subscriptions
- `"Magazine"` - For magazine subscriptions

## Error Handling

### Scraping Errors
- Network timeouts (10 seconds)
- Invalid JSON in schema data
- Missing schema.org data
- Non-Product schema types
- UTF-8 encoding issues

### API Errors
- Authentication failures
- Rate limiting
- Invalid product data
- Duplicate product IDs
- Feed creation failures

### Data Validation
- Only subscription offers are processed
- Currency must match target currency
- Missing required fields are handled gracefully
- Invalid offer types are skipped

## Logging and Monitoring

The script provides detailed step-by-step logging:
- **Step 1**: URL scraping initiation
- **Step 2**: Schema extraction and validation with JSON output
- **Step 3**: Product data processing with offer analysis
- **Step 4**: Upload initiation
- **Step 5**: Upload completion/error
- **Progress tracking**: Shows current URL number and total count

## Key Differences from Single Issue Script

### Subscription vs Single Issue
- **This script**: Targets `offerType: "Subscription"`
- **Single issue script**: Filters out subscriptions, targets single issues

### Offer ID Generation
- **This script**: Adds "-sub" suffix to offer IDs
- **Single issue script**: Uses different ID format

### Custom Labels
- **This script**: `"Newspaper - Subscription - EN"`
- **Single issue script**: `"Magazine - Single Issue - EN"`

## Limitations and Considerations

### API Quotas
- Google Merchant Center API has rate limits
- Monitor quota usage in Google Cloud Console
- 1-second delay between requests helps manage rate limits

### Data Quality
- Depends on quality of schema.org data on source websites
- Some URLs may not have structured data
- Price and availability may be outdated
- Only processes first subscription offer found

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
5. **No Subscriptions Found**: Verify URLs contain subscription offers

### Debug Mode
The script includes extensive logging. Check console output for:
- Schema extraction details
- Offer analysis results
- Upload success/failure messages

## Security Notes
- Service account credentials should be kept secure
- Never commit API keys to version control
- Use environment variables for sensitive data in production
- Consider using service account key rotation

## Future Enhancements
- Add support for multiple subscription types per product
- Implement retry logic for failed uploads
- Add data validation and cleaning
- Support for batch processing
- Integration with other e-commerce platforms
- Add support for different subscription durations (monthly, yearly, etc.)

## File Structure
```
merchent_center_api/
├── subscriptions_scraping.py    # Main script file
├── README.md                    # This documentation
├── service_account_key.json     # Google Cloud credentials (not in repo)
└── Newspapers-full.csv          # URL data file (not in repo)
```

## License
This project is for internal use. Please ensure compliance with Google's API terms of service and PressReader's terms of use. 