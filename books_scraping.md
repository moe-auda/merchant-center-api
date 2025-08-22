# PressReader Books Scraping Script

## Overview
This script automates the process of scraping book product information from PressReader URLs and uploading them to Google Merchant Center. It extracts structured data from web pages and creates product listings for books, with support for regional content targeting and enhanced product metadata.

## Features
- **Web Scraping**: Extracts schema.org JSON-LD data from PressReader URLs
- **Regional Targeting**: Supports different regions (US/CA) with appropriate headers
- **Google Merchant Center Integration**: Uploads products via Google Content API
- **Enhanced Product Data**: Includes GTIN, brand, and detailed product information
- **Multi-region Support**: Configurable for different geographic markets
- **Book-specific Processing**: Optimized for book product data extraction

## Prerequisites

### Required Files
1. **Service Account Key**: Google Cloud service account JSON file (this will change depending where we strore the json file)
   - Path: `/content/drive/MyDrive/Colab Notebooks/Merchant Center API/service_account_key.json`
   - Must have Content API permissions

2. **CSV File**: Contains URLs to scrape (this will change depending where we store the CSVs)
   - Path: `/content/Book1.csv`
   - Must have a column named `"url"`

### Required Python Packages
```bash
pip install requests pandas beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Configuration

### Global Variables
```python
# Google Merchant Center Configuration
merchant_id = "5411908926"  # Our Merchant Center ID
SCOPES = ["https://www.googleapis.com/auth/content"]

# Target Market Configuration
target_country = "CA"        # Target country code
target_language = "en"       # Target language code
publication_type = "Book"    # Product type

# Web Scraping Configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Naverbot/1.0; +http://naver.com/bot)"
}

# Regional Configuration
US_IP = "104.131.0.1"  # Example US IP for regional targeting
```

## Core Functions

### 1. `extract_schema(url, region)`
**Purpose**: Scrapes a URL and extracts schema.org JSON-LD data with regional targeting

**Parameters**:
- `url` (str): The URL to scrape
- `region` (str): Target region ("US" or "CA")

**Returns**:
- `dict` or `None`: Product schema data if found, None otherwise

**Process**:
1. Sets region-specific headers (Accept-Language, X-Forwarded-For for US)
2. Makes HTTP request to the URL with 10-second timeout
3. Uses fresh session to avoid cookie persistence
4. Parses HTML with BeautifulSoup using UTF-8 encoding
5. Finds all `<script type="application/ld+json">` tags
6. Returns the first schema with `@type: "Product"`
7. Provides detailed logging of headers and response URLs

**Regional Headers**:
```python
# US Region
headers["Accept-Language"] = "en-US"
headers["X-Forwarded-For"] = US_IP

# CA Region  
headers["Accept-Language"] = "en-CA"
```

### 2. `process_product_data(schema)`
**Purpose**: Processes schema data to extract book product information

**Parameters**:
- `schema` (dict): Schema.org product data

**Returns**:
- `dict` or `None`: Formatted product data for Google Merchant Center

**Filters Applied**:
- Validates schema type is "Product"
- Skips products with zero price
- Generates unique offer ID from URL structure
- Extracts locale code from URL path

**Enhanced Product Data Structure**:
```python
{
    "offerId": "locale-lastsegment",
    "title": "Book Title",
    "description": "Book Description",
    "imageLink": "Image URL",
    "link": "Product URL",
    "contentLanguage": "en",
    "targetCountry": "CA",
    "channel": "online",
    "availability": "in stock",
    "price": {"value": "19.99", "currency": "USD"},
    "gtin": "9781234567890",  # ISBN-13
    "brand": "Publisher Name",
    "customLabel0": "Book - EN"
}
```

**Data Extraction**:
- **Title**: From `schema.name`
- **Description**: From `schema.description`
- **Image**: From `schema.image`
- **GTIN**: From `schema.gtin13` (ISBN-13)
- **Brand**: From `schema.brand.name`
- **Price**: From `offers.price`
- **Currency**: From `offers.priceCurrency`

### 3. `upload_product(product_data)`
**Purpose**: Uploads product data to Google Merchant Center

**Parameters**:
- `product_data` (dict): Formatted product data

**Process**:
- Uses Google Content API to insert product
- Handles API errors gracefully with detailed error logging

### 4. `main(region)`
**Purpose**: Main execution function

**Parameters**:
- `region` (str): Target region for scraping ("US" or "CA")

**Process**:
1. Reads CSV file with URLs
2. Iterates through each URL with progress tracking
3. Extracts and processes product data with regional targeting
4. Uploads valid book products to Merchant Center

## Usage

### Basic Execution
```python
if __name__ == "__main__":
    main("CA")  # Upload books with Canadian regional targeting
```

### Supported Regions
- `"US"` - United States (uses US IP and en-US headers)
- `"CA"` - Canada (uses Canadian headers)

### Regional Differences
| Region | Accept-Language | X-Forwarded-For | Use Case |
|--------|----------------|-----------------|----------|
| US | en-US | US IP | US market content |
| CA | en-CA | None | Canadian market content |

## Error Handling

### Scraping Errors
- Network timeouts (10 seconds)
- Invalid JSON in schema data
- Missing schema.org data
- Non-Product schema types
- UTF-8 encoding issues
- Regional header conflicts

### API Errors
- Authentication failures
- Rate limiting
- Invalid product data
- Duplicate product IDs
- Missing required fields

### Data Validation
- Zero-price products are skipped
- Invalid schema types are rejected
- Missing required fields are handled gracefully
- GTIN validation (ISBN-13 format)

## Logging and Monitoring

The script provides detailed step-by-step logging:
- **Step 1**: URL scraping initiation with region info
- **Step 2**: Schema extraction and validation with JSON output
- **Step 3**: Product data processing with price/currency analysis
- **Step 4**: Upload initiation
- **Step 5**: Upload completion/error
- **Progress tracking**: Shows current URL number and total count

**Additional Logging**:
- Headers used for each request
- Response URLs (for redirect tracking)
- Regional configuration details

## Key Features

### Regional Content Targeting
- **US Region**: Uses US IP and en-US language headers
- **CA Region**: Uses Canadian language headers
- **Session Management**: Fresh sessions prevent cookie conflicts

### Enhanced Product Metadata
- **GTIN Support**: Extracts ISBN-13 for book identification
- **Brand Information**: Captures publisher/author information
- **Rich Descriptions**: Full product descriptions
- **High-Quality Images**: Direct image links

### Book-Specific Processing
- **ISBN Validation**: Supports standard book identification
- **Publisher Data**: Extracts brand/publisher information
- **Content Type**: Specifically tagged as "Book" products

## Limitations and Considerations

### API Quotas
- Google Merchant Center API has rate limits
- Monitor quota usage in Google Cloud Console
- No built-in delays between requests

### Data Quality
- Depends on quality of schema.org data on source websites
- Some URLs may not have structured data
- Price and availability may be outdated
- GTIN may not be available for all books

### Regional Limitations
- IP-based regional targeting may not work reliably
- Some content may be geo-restricted
- Language headers may not affect all content

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
5. **Regional Content Issues**: Verify content availability in target region
6. **GTIN Missing**: Some books may not have ISBN-13 data

### Debug Mode
The script includes extensive logging. Check console output for:
- Regional header configuration
- Schema extraction details
- Product data processing results
- Upload success/failure messages

## Security Notes
- Service account credentials should be kept secure
- Never commit API keys to version control
- Use environment variables for sensitive data in production
- Consider using service account key rotation
- IP address usage should be reviewed for compliance

## Future Enhancements
- Add support for multiple regions per product
- Implement retry logic for failed uploads
- Add data validation and cleaning
- Support for batch processing
- Integration with other e-commerce platforms
- Add support for different book formats (eBook, audiobook, etc.)
- Implement proper proxy rotation for regional targeting

## File Structure
```
merchent_center_api/
├── books_scraping.py         # Main script file
├── BOOKS_README.md           # This documentation
├── service_account_key.json  # Google Cloud credentials (not in repo)
└── Book1.csv                 # URL data file (not in repo)
```

## License
This project is for internal use. Please ensure compliance with Google's API terms of service and PressReader's terms of use. 