import logging
import time

from itertools import cycle
from typing import Optional
from urllib.parse import urlparse, unquote


import requests
from bs4 import BeautifulSoup, Tag


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


PROXIES_API = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&proxy_format=protocolipport&format=text&timeout=20000"


class Scraper:
    def __init__(self):
        self.proxies = self.fetch_proxies()
        self.proxy_pool = cycle(self.proxies) if self.proxies else None
        self.functions = []

    def fetch_proxies(self) -> list:
        """Fetch list of proxies from ProxyScrape and return as list of dicts."""
        try:
            res = requests.get(PROXIES_API)
            proxy_string = res.content.decode("utf-8")
            proxy_list = proxy_string.strip().split("\r\n")
            proxies = [{"http": proxy, "https": proxy} for proxy in proxy_list]
            return proxies
        except requests.RequestException as e:
            logging.error(f"Failed to fetch proxies: {e}")
            return []

    def fetch(
        self,
        url: str,
        use_proxy: bool = False,
        allow_redirects: bool = False,
        retries: int = 3,
        retry_sleep_sec: int = 5,
    ) -> Optional[requests.Response]:
        """Fetch URL using optional proxy rotation."""
        if use_proxy and not self.proxies:
            logging.error(f"'use_proxy' set to {use_proxy} but no proxies available.")
            return

        for attempt in range(retries):
            proxy = next(self.proxy_pool, None) if use_proxy else None
            try:
                response = requests.get(
                    url, proxies=proxy, timeout=5, allow_redirects=allow_redirects
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logging.error(f"Request failed for URL: {url}. Error: {e}")
                logging.error(f"Trying attempt {attempt+1} of {retries}")
                time.sleep(retry_sleep_sec)

        return

    def get_text_from_element(
        self, soup: BeautifulSoup, tag: str, class_name: Optional[str] = None
    ) -> Optional[str]:
        """Utility method to extract text from a specific tag"""
        element = soup.find(tag, class_=class_name)
        return element.get_text(strip=True) if element else None

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
            address = unquote(path_segments[address_segment_index]).replace("+", " ")
            return address

        return None

    def add_function(self, function):
        """Add a function to the list of functions to execute."""
        self.functions.append(function)

    def execute(self, input):
        """Execute the list of functions, passing the result of each as input to the next."""
        result = input
        for function in self.functions:
            result = function(self, result)
            if not result:
                logging.error(
                    f"Function {function.__name__} returned nothing. An error occurred"
                )
                return None
        return result


if __name__ == "__main__":
    s = Scraper()
    r = s.fetch("https://httpbin.org/status/200", use_proxy=True)
    print(r)
