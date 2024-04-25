import copy
import json
import logging
import pendulum

import redis

from typing import Optional, Dict, List, Union
from urllib.parse import urljoin

from airflow.providers.redis.hooks.redis import RedisHook
from bs4 import BeautifulSoup, Tag
from requests import ConnectionError

from modules.scraper.scraper import Scraper
from modules.utils import load_from_redis


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


schema = {
    "id": None,
    "url": None,
    "address": None,
    "building": None,
    "unit": None,
    "location": None,
    "square_feet": None,
    "available_date": None,
    "price": None,
    "management": "Paramount Management",
    "bedrooms": None,
    "bathrooms": None,
    "den": None,
    "leasing_info": {
        "lease": None,
        "included": None,
        "not_included": None,
        "parking": None,
        "storage": None,
        "deposit": None,
        "policy": None,
    },
    "description_info": None,
    "building_info": None,
    "suite_info": {
        "miscellaneous": [],
        "appliances": [],
        "kitchen": [],
        "bathroom": [],
        "flooring": [],
        "storage": [],
    },
}


def get_leasing_info(tab: Tag) -> Dict:
    """Extracts all leasing info from the leasing tab"""

    leasing_info = {
        "lease": None,
        "included": None,
        "not_included": None,
        "parking": None,
        "storage": None,
        "deposit": None,
        "policy": None,
    }

    try:
        # Find the main table, then immediate tr children
        table = tab.find("table")

        if not table:
            raise ValueError("No leasing table found")

        rows: List[Tag] = table.find_all("tr", recursive=False)

        for row in rows:
            # Category is always the first td
            category = (
                row.find("td")
                .get_text(strip=True)
                .lower()
                .replace(" ", "_")
                .replace(":", "")
            )
            values_tables = row.find_all("table")

            if not values_tables:
                continue

            values = []

            for table in values_tables:
                all_tds = table.find_all("td")

                # They used entire tables to display a bullet point, filter them out
                non_width_12_tds = [td for td in all_tds if td.get("width") == None]
                for td in non_width_12_tds:
                    text = td.get_text(strip=True)
                    values.append(text)

                # Assign the list of values to the category in the dictionary
                leasing_info[category] = values

    except Exception as e:
        logging.error(f"Error getting leasing info: {e}")
    finally:
        return leasing_info


def get_building_info(tab: Tag) -> List[Union[Dict, str]]:
    """Extracts all building info from the building tab"""

    building_info = []

    try:
        table = tab.find("table")

        # Some listings may not have table
        if not table:
            raise ValueError("No building table found")

        main_row = table.find("tr")
        columns: List[Tag] = main_row.find_all("td", recursive=False)

        if not columns:
            raise ValueError("No building table columns found")

        for column in columns:
            tables_to_process: Optional[List[Tag]] = column.find_all("table")

            if not tables_to_process:
                continue

            for i in range(len(tables_to_process)):
                current_table = tables_to_process[i]

                # Check if the current table does not have the 'style' attribute
                if not current_table.get("style"):
                    # Then check the next one
                    if i + 1 < len(tables_to_process):
                        next_table = tables_to_process[i + 1]
                        if next_table.get("style"):
                            key = (
                                current_table.get_text(strip=True)
                                .lower()
                                .replace(" ", "_")
                                .replace(":", "")
                            )
                            value = next_table.get_text(strip=True)
                            building_info.append({key: value})
                            continue

                    # This is only reached when the previous table has no style, but the next one doesnt either
                    building_info.append(current_table.get_text(strip=True))

    except Exception as e:
        logging.error(f"Error getting building info: {e}")
    finally:
        return building_info


def get_suite_info(tab: Tag) -> Dict[str, List[str]]:
    """Extracts all suite info from the suite tab"""

    suite_info = {
        "miscellaneous": [],
        "appliances": [],
        "kitchen": [],
        "bathroom": [],
        "flooring": [],
        "storage": [],
    }

    try:
        # Process miscellaneous section
        miscellaneous = tab.find("table", {"cellpadding": "6"})
        if miscellaneous:
            # Each row is a table
            tables: Optional[List[Tag]] = miscellaneous.find_all("table")
            if tables:
                for table in tables:
                    tds: List[Tag] = table.find_all("td")

                    for td in tds:
                        # Those that are styled are bullet points
                        if td.get("style"):
                            continue

                        suite_info["miscellaneous"].append(td.get_text(strip=True))

        # Get all tables, skipping the first if it's the miscellaneous section
        tables_to_process: Optional[List[Tag]] = tab.find_all("table", recursive=False)

        if not tables_to_process:
            raise ValueError("No tables to process")

        if miscellaneous:
            tables_to_process = tables_to_process[1:]

        # Identify paired tables and collect their information
        for i in range(len(tables_to_process)):
            current_table = tables_to_process[i]

            if not current_table.get("bgcolor"):

                # Then check the next one
                if i + 1 < len(tables_to_process):
                    next_table = tables_to_process[i + 1]
                    if next_table.get("bgcolor"):
                        key = (
                            current_table.get_text(strip=True)
                            .lower()
                            .replace(" ", "_")
                            .replace(":", "")
                        )
                        all_tds: Optional[List[Tag]] = next_table.find_all("td")
                        if not all_tds:
                            continue

                        values = [td.get_text(strip=True) for td in all_tds]
                        suite_info[key].extend(values)
                        continue

    except Exception as e:
        logging.error(f"Error getting suite info: {e}")
    finally:
        return suite_info


def get_tabs(tabs: List[Tag]) -> Dict:
    """Get the content from the leasing, description, building, and suite tabs on the page"""
    tabs_data = {
        "leasing_info": {
            "lease": None,
            "included": None,
            "not_included": None,
            "parking": None,
            "storage": None,
            "deposit": None,
            "policy": None,
        },
        "description_info": None,
        "building_info": None,
        "suite_info": {
            "miscellaneous": [],
            "appliances": [],
            "kitchen": [],
            "bathroom": [],
            "flooring": [],
            "storage": [],
        },
    }

    try:

        tabs_data["leasing_info"] = get_leasing_info(tabs[0])
        tabs_data["description_info"] = tabs[1].get_text(strip=True)
        tabs_data["building_info"] = get_building_info(tabs[2])
        tabs_data["suite_info"] = get_suite_info(tabs[3])

    except Exception as e:
        logging.error(f"Error processing tab content: {e}")

    return tabs_data


def get_listings() -> Dict:
    """
    Get each listing from a list of listings urls and corresponding summaries

    Returns:
    Dict: A dict of the scraped listings
    """
    # Read from redis
    redis_hook = RedisHook(redis_conn_id="redis_conn").get_conn()
    # redis_hook = redis.Redis(host="localhost", port=6379)
    # value = redis_hook.get("444rent_data")

    value = load_from_redis(conn_id="redis_conn", key="444rent_data")
    listings_data = json.loads(value)

    listings: List[Dict] = listings_data["data"]

    scraper = Scraper()

    for listing in listings:

        try:
            res = scraper.fetch(listing["url"])
            soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

            listing["bathrooms"] = scraper.get_text_from_element(
                soup, "div", attributes={"id": "suitemain"}
            )
            listing["address"] = scraper.get_text_from_element(
                soup, "div", attributes={"id": "addressmain"}
            )

            tab_container = soup.find("div", class_="tab_container")
            tabs = tab_container.find_all("div", class_="tab_content")

            if tabs:
                tabs_data = get_tabs(tabs)
                listing.update(tabs_data)

            logging.info(f"Scraped listing: {listing['address']}")

            print(listing)
            print("\n\n")

        except ConnectionError as e:
            logging.error(f"Connection failed for URL: {listing['url']}. Error: {e}")
        except Exception as err:
            logging.error(f"Error processing data from {listing['url']}: {err}")
        finally:
            scraper.sleep()

    redis_hook.set("scraped_fffrent_listings", json.dumps(listings_data))


def parse_listing_row(scraper: Scraper, row: Tag, bedrooms: str) -> Optional[Dict]:
    row_data = copy.deepcopy(schema)

    href = scraper.get_attribute_from_element(row, "a", "href")

    # Skip broken links
    if not href:
        logging.warning("Unable to find href for row")
        return None

    # Add rooms from table
    row_data["bedrooms"] = bedrooms

    # Generate listing URL
    row_data["url"] = urljoin("https://www.444rent.com", href)

    # Extract column data
    columns: List[Tag] = row.find_all("td")

    fields = [
        "building",
        "unit",
        "location",
        "square_feet",
        "available_date",
        "price",
    ]

    for i, field in enumerate(fields):
        row_data[field] = scraper.clean_whitespace(columns[i].get_text(strip=True))

    return row_data


def get_listing_urls() -> Optional[Dict]:
    """
    Scrapes the listing URL and preview information from each row on the apartments for rent.

    Returns:
    Optional[Dict]: A dictionary containing data about the scrape and each listing, or None if an error occurs.
    """
    url = "https://www.444rent.com/apartments.asp"
    redis_hook = RedisHook(redis_conn_id="redis_conn").get_conn()
    # redis_hook = redis.Redis(host="localhost", port=6379)

    scraper = Scraper()
    data = {"source": url, "ran_at": pendulum.now().to_iso8601_string(), "data": None}

    try:
        res = scraper.fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")

        tables: Optional[List[Tag]] = soup.find_all("table", {"bgcolor": "#ffffff"})

        if not tables:
            raise ValueError(f"No tables to scrape found for URL: {url}")

        listings = []
        for table in tables:
            rows: List[Tag] = table.find_all("tr", bgcolor=True)

            if not rows:
                logging.warning("No rows found in table")
                continue

            # Get the room type from table header
            bedrooms = scraper.get_text_from_element(
                table, "font", attributes={"color": "#FFFFFF"}
            )

            for row in rows:
                parsed_row = parse_listing_row(scraper, row, bedrooms)

                if parsed_row:
                    listings.append(parsed_row)

        data["data"] = listings
        # Save to redis
        redis_hook.set("444rent_data", json.dumps(data))

    except ConnectionError as e:
        logging.error(f"Connection failed for URL: {url}. Error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unknown error occurred fetching: {url}. Error: {e}")
        raise
