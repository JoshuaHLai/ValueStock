#! python3
# Web Scraper for Yahoo Finance

import os.path
import sys

from lxml import html
import requests
import urllib3

from collections import OrderedDict
import csv

import numpy as np
import pandas as pd

from datetime import date

# Suppress Insecure Request Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_headers():
    return {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
            "cache-control": "max-age=0",
            "pragma": "no-cache",
            "referrer": "https://google.com",
            "dnt": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}

'''
Parse Summary Table on Main Webpage
Summary Table Uses Key-Value Relationship
'''
def parse_summary(ticker):

    url = "https://finance.yahoo.com/quote/%s?p=%s" % (ticker, ticker)
    response = requests.get(url, verify=False, headers=get_headers(), timeout=30)
    
    print("Parsing Summary Data for %s" % (ticker))
    parser = html.fromstring(response.text)
    summary_table = parser.xpath('//div[contains(@data-test,"summary-table")]//tr')

    relevant_keys = ['Previous Close', 'Volume', 'Market Cap', 'PE Ratio (TTM)', 'EPS (TTM)']
    summary_data = OrderedDict()

    try:
        for table_data in summary_table:
            raw_table_key = table_data.xpath('.//td[1]//text()')
            raw_table_value = table_data.xpath('.//td[2]//text()')
            table_key = ''.join(raw_table_key).strip()

            if table_key in relevant_keys:
                table_value = ''.join(raw_table_value).strip()
                summary_data.update({table_key: table_value})

        return summary_data
    except ValueError:
        print("Failed to parse json response")
        return {"Error": "Failed to parse json response"}
    except:
        return {"Error": "Unhandled Error"}

'''
Parse Financial Data from Balance Sheet
Table Uses a 2-Dimensional Array Structure
'''
def parse_balance_sheet(ticker):

    url = "https://finance.yahoo.com/quote/%s/balance-sheet?p=%s" % (ticker, ticker)
    response = requests.get(url, verify=False, headers=get_headers(), timeout=30)

    print("Parsing Balance Sheet Data for %s" % (ticker))
    parser = html.fromstring(response.content)
    balance_sheet = parser.xpath("//div[contains(@class, 'D(tbr)')]")

    # Check that data exists
    assert len(balance_sheet) > 0

    balance_sheet_data = OrderedDict()

    full_data = []

    for table_data in balance_sheet:
        extracted_data = []

        data = table_data.xpath("./div")
        
        for element in data:

            try:    
                (text,) = element.xpath('.//span/text()[1]')
            except ValueError:
                (text,) = ("N/A",)

            extracted_data.append(text)
            if len(extracted_data) == 2:
                break

        full_data.append(extracted_data)

    for item in full_data:
        if item[0] == "Breakdown":
            key = "Financial Report Date"
        else:
            key = str(item[0])

        value = str(item[1])

        balance_sheet_data.update({key: value}) 

    return balance_sheet_data

'''
Calculate Book Value and Other Statistics
'''
def calculate(ticker, summary, balance_sheet):

    print("Calculating Statistics for %s" % (ticker))

    book_value = (convert(balance_sheet["Total Assets"]) - convert(balance_sheet["Total Liabilities Net Minority Interest"])) * 1000
    book_value_share = book_value / convert(summary["Volume"])

    price_to_asset = convert(summary["Previous Close"]) / book_value_share 

    asset_to_liability = convert(balance_sheet["Total Assets"]) / convert(balance_sheet["Total Liabilities Net Minority Interest"]) 

    calculations_summary = OrderedDict({"Book Value": book_value, "Book Value per Share": book_value_share, "Price to Book Value Ratio": price_to_asset, "Asset to Liabilities": asset_to_liability})

    return calculations_summary

'''
Helper Function #1
Merge All Data and Prepare for Export
'''
def merge_dict(dict1, dict2):
    result = {**dict1, **dict2}
    return result

'''
Helper Function #2
Strip Commas from Value and Convert to Float
'''
def convert(value):
    return float(value.replace(',',''))

'''
Core Process
Call Functions to Scrape/Merge Data and Export
'''
def process(ticker):
    # Extract and Save Today's Date
    today = date.today()
    convert = today.strftime("%m/%d/%y")
    result = {"Date Processed": convert}
    
    summary = parse_summary(ticker)

    balance_sheet = parse_balance_sheet(ticker)

    calculations = calculate(ticker, summary, balance_sheet)

    processed_dicts = [summary, balance_sheet, calculations]

    # Merge Dictionaries and Prepare for Export
    for item in processed_dicts:
        result = merge_dict(result, item)

    df = pd.DataFrame(result, index=[0])

    # Exporting DataFrame to CSV File
    file_out = "Data/%s.csv" % (ticker)
    print("Exporting to %s.csv" % (ticker))
    if os.path.exists(file_out) == True:
        with open(file_out, 'a') as f:
            df.to_csv(f, header = False, index = False, line_terminator = '\n')
    else:
        df.to_csv(file_out, index = False, line_terminator = '\n')

def main(ticker):

    if len(ticker) > 1:
        for item in ticker:
            print("Fetching data for %s" % (item))
            process(item)
    else:
        print("Fetching data for %s" % (ticker[0]))
        process(ticker[0])

if __name__ == "__main__":

    # Grab Arguments
    arg_len = len(sys.argv)
    ticker = sys.argv[1: arg_len]

    main(ticker)