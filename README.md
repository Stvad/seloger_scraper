# seloger_scraper
Parser for SeLoger.com apartments information

## Usage:

**seloger_scraper.py [-h] [-o OUTPUT] [-p PAGES] [-b APARTMENT_BASE_URL] URLs [URLs ...]**

Positional arguments:

  **URLs**: List of URLs with all desired parameters from SeLoger.com (So you go to Seloger.com, enter search query, go for the second page of the result, copy the URL without 2 at the end and post it here)

Optional arguments:

  **-h, --help**            show help message and exit
  
  **-o OUTPUT, --output OUTPUT**  output file path
  
  **-p PAGES, --pages PAGES**  number of pages to go through for each base URL. 
  
  **-b APARTMENT_BASE_URL, --apartment_base_url APARTMENT_BASE_URL** Base URL for constracting apartment URL. Default value should work fine.
