import logging
from typing import Optional

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
from requests import Response, HTTPError

from utils import retry


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


@retry(retries=3, retry_sleep_sec=5)
def fetch(url: str) -> Response:
    """
    Fetches a URL, streams the response. Raises exception if the status code is invalid.

    :param url: The URL to fetch
    :return: The response if valid, otherwise raises exception
    """
    user_agent = UserAgent()
    headers = {"User-Agent": user_agent.random}
    res = requests.get(url, stream=True, headers=headers)
    res.raise_for_status()
    return res


def halifax_business_planning_development_applications(url: str):

    try:
        res: Response = fetch(url)
        if not res.ok:
            raise HTTPError(f"Invalid Response code for {url}: {res.status_code}")
        
        soup = BeautifulSoup(res.content, "html.parser")

        # Container div holding the relevant info
        content_div = soup.find("div", class_="view-content")

        rows = content_div.find_all("div", class_="views-row")



        


    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")


def main(url_function_map):
    for url in url_function_map:
        url_function_map[url](url)


if __name__ == "__main__":
    url_function_map = {
        "https://www.halifax.ca/business/planning-development/applications": halifax_business_planning_development_applications
    }
    main(url_function_map)
