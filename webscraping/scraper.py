import requests
from bs4 import BeautifulSoup
from tkr_utils import setup_logging, logs_and_exceptions

logger = setup_logging(__file__)

@logs_and_exceptions(logger)
def scrape_webpage(url: str) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    else:
        logger.error("Failed to fetch webpage: %s", url)
        return ""
