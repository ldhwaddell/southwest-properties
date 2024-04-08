import logging
import re
from typing import Dict, List, Any

from bs4 import BeautifulSoup, Tag

from data.scraper.scraper import Scraper

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)

# Payload data for fetch
json_data = {
    "Map": {
        "BoundingBox": {
            "LowerRight": {
                "Latitude": 43.25112,
                "Longitude": -61.15951,
            },
            "UpperLeft": {
                "Latitude": 46.6022,
                "Longitude": -65.14205,
            },
        },
        "CountryCode": "CA",
    },
    "Geography": {
        "ID": "td9ygfc",
        "Display": "Halifax, NS",
        "GeographyType": 2,
        "Address": {
            "City": "Halifax",
            "CountryCode": "CAN",
            "County": "Halifax",
            "State": "NS",
        },
        "Location": {
            "Latitude": 44.592,
            "Longitude": -61.954,
        },
        "BoundingBox": {
            "LowerRight": {
                "Latitude": 43.90746,
                "Longitude": -59.67046,
            },
            "UpperLeft": {
                "Latitude": 45.27587,
                "Longitude": -64.2372,
            },
        },
        "v": 68579,
    },
    "Listing": {},
    "Paging": {
        "Page": "1",
    },
    "IsBoundedSearch": True,
    "ResultSeed": 83590,
    "Options": 0,
    "CountryAbbreviation": "CA",
}

# Default headers to help stop scraper from being found
headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://www.apartments.com",
    "referer": "https://www.apartments.com/halifax-ns/",
    "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
}


def get_amenities(amenities_section: Tag) -> List[str]:
    """Extract the amenities in list form"""
    if not amenities_section:
        return None

    amenities = []
    for ul in amenities_section.find_all("li"):
        amenities.append(ul.get_text(strip=True))

    return amenities


def get_listings(scraper: Scraper, scraped_rows: List[Dict[str, str]]):
    """Gets each listing from a list of URLs"""
    listings = []

    for row in scraped_rows:

        listing_data = {
            "title": None,
            "monthly_rent": None,
            "bedrooms": None,
            "bathrooms": None,
            "square_feet": None,
            "about": None,
            "description": None,
            "amenities": None,
            "fees": None,
        }

        try:
            res = scraper.fetch(row["url"])
            soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

            if soup.find("h3", {"id": "notAvailableText"}):
                logging.warning(f"Listing does not have availability. Skipping")
                continue

            listing_data["title"] = scraper.get_text_from_element(
                soup, "h1", class_name="propertyName"
            )

            info_table = soup.find("ul", class_="priceBedRangeInfo")

            for li in info_table.find_all("li", class_="column"):
                label = (
                    li.find("p", class_="rentInfoLabel")
                    .text.strip()
                    .lower()
                    .replace(" ", "_")
                )
                detail = li.find("p", class_="rentInfoDetail").text.strip()

                if label and detail:
                    listing_data[label] = detail

            about_text = scraper.get_text_from_element(
                soup, "section", class_name="aboutSectionSnippet"
            )

            listing_data["about"] = (
                scraper.clean_whitespace(about_text) if about_text else None
            )

            description_text = scraper.get_text_from_element(
                soup, "section", class_name="descriptionSection"
            )

            listing_data["description"] = (
                scraper.clean_whitespace(description_text) if description_text else None
            )

            amenities_section = soup.find("section", class_="amenitiesSection")
            listing_data["amenities"] = get_amenities(amenities_section)

            fees_text = scraper.get_text_from_element(
                soup, "section", class_name="feesSection"
            )

            listing_data["fees"] = (
                scraper.clean_whitespace(fees_text) if fees_text else None
            )

            row.update(listing_data)
            listings.append(row)
            logging.info(f"Scraped application: {listing_data['title']}")
            scraper.sleep(min=5, max=10)

        except Exception as err:
            logging.error(
                f"Skipping. Error processing case data from {row['url']}: {err}"
            )

    return listings


def get_rows(
    scraper: Scraper, url: str, json_data: Dict[str, Any], headers: Dict[str, Any]
):
    """Uses the apartments search API to fetch data for halifax"""
    scraped_rows = []

    try:

        res = scraper.fetch(url, method="POST", json_data=json_data, use_proxy=True)
        res = res.json()
        html = res["PlacardState"]["HTML"]

        soup = BeautifulSoup(html, "html.parser")

        # Each row represents a current application
        rows = soup.find_all("li", class_="mortar-wrapper")

        for row in rows:
            row_data = {"id": None, "url": None, "address": None}

            id = scraper.get_attribute_from_element(
                row, "article", attribute="data-listingid", class_name="placard"
            )
            listing_url = scraper.get_attribute_from_element(
                row, "article", attribute="data-url", class_name="placard"
            )
            address = scraper.get_attribute_from_element(
                row, "article", attribute="data-streetaddress", class_name="placard"
            )

            if not listing_url:
                logging.warning("Unable to find url for row")
                continue

            row_data["id"] = id
            row_data["url"] = listing_url
            row_data["address"] = address

            scraped_rows.append(row_data)

        # Check for more pages
        state: Dict = res["MetaState"]
        print(len(scraped_rows))

        next_page = state.get("PageNextUrl", None)
        if next_page:
            logging.info("Another page found")
            scraper.sleep(min=5, max=10)

            # Then update the json payload
            current_page = int(json_data["Paging"]["Page"])

            next_page = {"Page": str(current_page + 1)}
            json_data["Paging"] = next_page

            next_page_rows = get_rows(
                scraper, url, json_data=json_data, headers=headers
            )
            scraped_rows.extend(next_page_rows)
        else:
            logging.info("No more pages found")

        print(len(scraped_rows))
        return scraped_rows

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def get_x_csrf_token() -> str | None:
    """Fetches the csrf token"""

    url = "https://www.apartments.com/halifax-ns/"
    scraper = Scraper()
    res = scraper.fetch(url)

    text = res.text

    # Simple regex to match the JavaScript object pattern
    match = re.search(r"aft: \'(.*?)\'", text)

    if match:
        token = match.group(1)
        return token


def main():
    url = "https://www.apartments.com/services/search/"
    # token = get_x_csrf_token()

    # if not token:
    #     logging.error("Unable to get x-csrf-token")
    #     return

    # headers["x-csrf-token"] = token

    scraper = Scraper()
    scraper.add_function(get_rows)
    # scraper.add_function(get_listings)

    data = scraper.execute(url, json_data, headers)
    print(data)
    print(len(data))


if __name__ == "__main__":
    main()
