import json
import logging
import random
import time
from typing import Optional, Dict, Union, List
from urllib.parse import urljoin, urlparse, unquote

from bs4 import BeautifulSoup, Tag

from src.utils import fetch, generate_hash

# from src.database.database import Database
# from src.database.models import ActivePlanningApplications


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def get_text_from_element(
    soup: BeautifulSoup, tag: str, class_name: Optional[str] = None
) -> Optional[str]:
    element = soup.find(tag, class_=class_name)
    return element.get_text(strip=True) if element else None


def get_location_from_maps_url(url: str) -> str:
    if "goo.gl" in url or "maps.app.goo.gl" in url:
        # Follow the shortened URL to get the actual Google Maps URL
        res = fetch(url, allow_redirects=True)
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


def get_features_data(soup: BeautifulSoup) -> Dict[str, str]:
    features = {}

    # Finds the first one
    features_div = soup.find("div", class_="floatboxbottom")

    for element in features_div.find_all("div", class_="element"):
        key = element.find("h3").get_text(strip=True).lower().strip().replace(" ", "_")
        # The value is the next sibling of the h3 element which is navigable string
        value = (
            element.find("h3").next_sibling.strip()
            if element.find("h3").next_sibling
            else None
        )
        features[key] = value

    return features


def get_listing(url: str):
    listing_data = {
        "title": None,
        "price": None,
        "category": None,
        "description": None,
        "address": None,
        "features": None,
    }

    try:
        res = fetch(url)
        soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
        listing_data["title"] = get_text_from_element(soup, "h2")
        listing_data["id"] = generate_hash(listing_data["title"])
        listing_data["price"] = get_text_from_element(soup, "h3")
        listing_data["category"] = get_text_from_element(
            soup, "div", class_name="element element-itemcategory first"
        )
        listing_data["description"] = get_text_from_element(
            soup, "ul", class_name="pos-taxonomy"
        )

        location_tag = soup.find("a", {"title": "Location Map"})
        listing_data["address"] = get_location_from_maps_url(location_tag.get("href"))
        listing_data["features"] = get_features_data(soup)

        return listing_data

    except Exception as err:
        logging.error(f"Error processing case data from {url}: {err}")
        return None


def scrape(url: str) -> Optional[Dict]:
    scraped_data = []

    try:
        res = fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Each row represents a current application
        rows = soup.find_all("div", class_="teaser-item")

        for row in rows:
            a_tag = row.find("a")

            # Skip broken links
            if not a_tag or not a_tag.has_attr("href"):
                logging.warning("Unable to find href for row")
                continue

            # Build the url for the case represented by the tag
            href = a_tag.get("href")
            listing_url = urljoin(url, href)

            listing_data = get_listing(listing_url)
            listing_data["url"] = listing_url
            # print(listing_data)
            scraped_data.append(listing_data)

            logging.info(f"Scraped application: {listing_data['title']}")
            sleep_duration = round(random.uniform(0, 2), 1)
            logging.info(f"Sleeping for {sleep_duration} seconds")
            time.sleep(sleep_duration)

        logging.info("Checking for more pages")
        next_page_tag = soup.find("a", class_="next")
        if next_page_tag:
            href = next_page_tag.get("href")
            next_page_url = urljoin(url, href)

            scraped_data.extend(scrape(next_page_url))
        else:
            logging.info("No more pages found")

        return scraped_data

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def main():
    url = "https://www.halifaxqualityhomes.com/index.php?option=com_zoo&view=category&layout=category&Itemid=236"

    data = scrape(url)
    print(data)

    # db = Database("sqlite:///southwest.db")
    # db.compare_and_insert(ActivePlanningApplications, data)


if __name__ == "__main__":
    main()
