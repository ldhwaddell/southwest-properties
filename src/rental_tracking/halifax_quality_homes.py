import logging
import random
import time
from typing import Optional, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.utils import generate_hash
from src.scraper.scraper import Scraper

# from src.database.database import Database
# from src.database.models import ActivePlanningApplications


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def get_features_data(_: Scraper, listings: List[Dict]) -> Dict[str, str]:
    """Extracts the features from each listing 'floatboxbottom' div"""
    for listing in listings:
        features = {}

        # Use 'get' to avoid key error
        if not listing.get("features"):
            continue

        for element in listing["features"].find_all("div", class_="element"):
            key = (
                element.find("h3")
                .get_text(strip=True)
                .lower()
                .strip()
                .replace(" ", "_")
            )
            # The value is the next sibling of the h3 element which is navigable string
            value = (
                element.find("h3").next_sibling.strip()
                if element.find("h3").next_sibling
                else None
            )
            features[key] = value

        listing["features"] = features

    return listings


def get_listings(scraper: Scraper, listing_urls: List[str]):
    """Gets each listing from a list of URLs"""
    listings = []

    for url in listing_urls:

        listing_data = {
            "title": None,
            "price": None,
            "category": None,
            "description": None,
            "address": None,
            "features": None,
        }
        try:
            res = scraper.fetch(url)
            soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

            listing_data["title"] = scraper.get_text_from_element(soup, "h2")
            listing_data["id"] = generate_hash(listing_data["title"])
            listing_data["price"] = scraper.get_text_from_element(soup, "h3")
            listing_data["category"] = scraper.get_text_from_element(
                soup, "div", class_name="element element-itemcategory first"
            )
            listing_data["description"] = scraper.get_text_from_element(
                soup, "ul", class_name="pos-taxonomy"
            )

            location_tag = soup.find("a", {"title": "Location Map"})
            listing_data["address"] = scraper.get_location_from_maps_url(
                location_tag.get("href")
            )
            # listing_data["features"] = get_features_data(soup)
            listing_data["features"] = soup.find("div", class_="floatboxbottom")

            listings.append(listing_data)

            logging.info(f"Scraped application: {listing_data['title']}")
            sleep_duration = round(random.uniform(0, 2), 1)
            logging.info(f"Sleeping for {sleep_duration} seconds")
            time.sleep(sleep_duration)

        except Exception as err:
            logging.error(f"Skipping. Error processing case data from {url}: {err}")
            listings.append(None)

    return listings


def fetch_rows(scraper: Scraper, url: str) -> Optional[Dict]:
    """Scrapes the listing urls from each row on the rentals page"""
    scraped_urls = []

    try:
        res = scraper.fetch(url)
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

            scraped_urls.append(listing_url)

        logging.info("Checking for more pages")
        next_page_tag = soup.find("a", class_="next")
        if next_page_tag:
            href = next_page_tag.get("href")
            next_page_url = urljoin(url, href)

            scraped_urls.extend(fetch_rows(scraper, next_page_url))
        else:
            logging.info("No more pages found")

        return scraped_urls[:5]

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def main():
    url = "https://www.halifaxqualityhomes.com/index.php?option=com_zoo&view=category&layout=category&Itemid=236"
    scraper = Scraper()
    scraper.add_function(fetch_rows)
    scraper.add_function(get_listings)
    scraper.add_function(get_features_data)

    data = scraper.execute(url)
    print(data)


if __name__ == "__main__":
    main()
