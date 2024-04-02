import logging
import random
import re
import time

from datetime import datetime
from itertools import cycle
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse, unquote


import requests
from airflow.exceptions import AirflowBadRequest
from bs4 import BeautifulSoup, Tag
from fake_useragent import UserAgent


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


PROXIES_API = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&country=ca&proxy_format=protocolipport&format=text&timeout=20000"


class Scraper:
    def __init__(self):
        self.proxies = self.fetch_proxies()
        self.proxy_pool = cycle(self.proxies) if self.proxies else None
        self.functions = []

    def fetch_proxies(self) -> list:
        """Fetch list of proxies from ProxyScrape and return as list of dicts."""
        try:
            res = self.fetch(PROXIES_API)
            proxy_string = res.content.decode("utf-8")
            proxy_list = proxy_string.strip().split("\r\n")
            proxies = [{"http": proxy, "https": proxy} for proxy in proxy_list]
            return proxies

        except Exception as e:
            raise AirflowBadRequest(f"Failed to fetch proxies: {e}")

    def fetch(
        self,
        url: str,
        method: str = "GET",
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_proxy: bool = False,
        allow_redirects: bool = False,
        stream: bool = False,
        retries: int = 3,
        retry_sleep_sec: int = 5,
        timeout: int = 10,
    ) -> Optional[requests.Response]:
        """Fetches URL with desired options"""

        if use_proxy and not self.proxies:
            raise ValueError(
                f"'use_proxy' set to {use_proxy} but no proxies available.")

        # Default headers with randomized User-Agent
        user_agent = UserAgent()
        default_headers = {
            "user-agent": user_agent.random,
        }

        # If custom headers are provided, update default headers with them
        if headers:
            default_headers.update(headers)

        for attempt in range(retries):
            proxy = next(self.proxy_pool, None) if use_proxy else None

            try:

                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        proxies=proxy,
                        timeout=timeout,
                        allow_redirects=allow_redirects,
                        stream=stream,
                        headers=default_headers,
                    )
                elif method.upper() == "POST":
                    response = requests.post(
                        url,
                        json=json_data,
                        proxies=proxy,
                        timeout=timeout,
                        allow_redirects=allow_redirects,
                        stream=stream,
                        headers=default_headers,
                    )
                else:
                    logging.error(f"Unsupported method: {method}")
                    return None

                response.raise_for_status()
                logging.info(f"Successfully fetched URL: {url}")
                return response

            except requests.RequestException as e:
                logging.error(f"Request failed for URL: {url}. Error: {e}")
                logging.error(f"Trying attempt {attempt+1} of {retries}")
                time.sleep(retry_sleep_sec)

        raise requests.ConnectionError(f"Exceeded max retry num: {retries} failed")

    def get_text_from_element(
        self,
        soup: Union[BeautifulSoup, Tag],
        tag: str,
        attributes: Dict[str, str] = None,
        class_name: Optional[str] = None,
        strip: bool = True,
    ) -> Optional[str]:
        """Utility method to extract text from a specific tag"""
        element = soup.find(tag, attrs=attributes, class_=class_name)
        return element.get_text(strip=strip) if element else None

    def get_attribute_from_element(
        self,
        soup: Union[BeautifulSoup, Tag],
        tag: str,
        attribute: str,
        class_name: Optional[str] = None,
    ) -> Optional[str]:
        """Utility method to extract attribute from a specific tag"""
        element = soup.find(tag, class_=class_name)
        return element.get(attribute) if element else None

    def get_location_from_maps_url(self, url: str) -> str:
        """Utility method to extract the location from a google maps URL"""
        if "goo.gl" in url or "maps.app.goo.gl" in url:
            # Follow the shortened URL to get the actual Google Maps URL
            res = self.fetch(url, allow_redirects=True)
            # Use the final URL after all redirects
            url = res.url

        parsed_url = urlparse(url)

        # Check if 'place' is in the path segments
        if "place" in parsed_url.path.split("/"):
            # Find the 'maps/place/' segment in the path
            path_segments = parsed_url.path.split("/")
            address_segment_index = path_segments.index("place") + 1
            # Extract the address
            address = unquote(
                path_segments[address_segment_index]).replace("+", " ")
            return address

        return None

    def clean_whitespace(self, text: str) -> str:
        """Replace one or more whitespace characters (including non-breaking spaces) with a single space"""
        return re.sub(r"\s+", " ", text)

    def parse_iso8601_date(self, date_str: str) -> datetime:
        """Parse an ISO 8601 formatted date string to a datetime object."""
        # Removes z at end
        return datetime.fromisoformat(date_str[:-1])

    def sleep(self, min: int = 0, max: int = 2):
        """Sleeps a random amount of time"""
        sleep_duration = round(random.uniform(min, max), 2)
        logging.info(f"Sleeping for {sleep_duration} seconds")
        time.sleep(sleep_duration)

    def add_function(self, function):
        """Add a function to the list of functions to execute."""
        self.functions.append(function)

    def execute(self, *args):
        """Execute the list of functions, passing the result of each as input to the next."""
        if not self.functions:
            raise ValueError("No functions to execute.")

        # Initialize 'result' with the first function call using provided arguments
        result = self.functions[0](self, *args)
        if result is None:
            logging.error(
                f"Function {function.__name__} returned nothing. An error occurred"
            )
            return None

        # Iterate over the rest of the functions, passing the previous result as the only argument
        for function in self.functions[1:]:
            result = function(self, result)

            if result is None:
                logging.error(
                    f"Function {function.__name__} returned nothing. An error occurred"
                )
                return None
        return result


if __name__ == "__main__":
    s = Scraper()
    r = s.fetch("https://httpbin.org/status/200", use_proxy=True)
    print(r)
