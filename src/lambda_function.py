import json
from YelpScrape import YelpScraper

def lambda_handler(event, context):
    scraped = YelpScraper(event.uri)
    return {
        "statusCode": 200,
        "body": scraped
    }
