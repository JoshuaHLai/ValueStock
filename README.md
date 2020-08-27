# ValueStock
### Pipeline to Scrape Stock Data and Feed to Tableu for Value Investing

Welcome to ValueStock, a basic pipeline to extract financial and stock information for public companies in order to determine whether or not a company's stock is undervalued based on principles put forth by the book "The Intelligent Investor" by Benjamin Graham. This repository holds all of the code necessary in order for the pipeline to work.

## Code
As of now, only a small part of the pipeline has been developed. Over time, there will be more files included to improve the overall process.

### scraper.py
- Python file to scrape web date from Yahoo! Finance based on inputted ticker symbol(s)
- Output data and statistics to a .csv file

## Future Work
There are features that still need to be implemented to improve the overall package
1. Develop batch/shell script in order to automate scraping at end-of-day and pipe output to Tableau

Note: name is tenative and is subject to change
