import json
import logging
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from modules.scraper.scraper import Scraper

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def remove_letters(str: str) -> int:
    return "".join(i for i in str if i.isdigit())


def get_amenities(amenities_section: Tag) -> List[str]:
    """Extract the amenities in list form"""
    if not amenities_section:
        return None

    amenities = []
    for ul in amenities_section.find_all("li"):
        amenities.append(ul.get_text(strip=True))

    return json.dumps(amenities)


def get_listings(scraper: Scraper, scraped_rows: List[Dict[str, str]]):
    """Gets each listing from a list of URLs"""
    for row in scraped_rows:

        try:
            res = scraper.headless_fetch(row["url"])
            soup: BeautifulSoup = BeautifulSoup(res, "html.parser")

            if soup.find("h3", {"id": "notAvailableText"}):
                logging.warning(f"Listing does not have availability. Skipping")
                row["available"] = False

            row["building"] = scraper.get_text_from_element(
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
                    row[label] = detail

            about_text = scraper.get_text_from_element(
                soup, "section", class_name="aboutSectionSnippet"
            )

            row["about"] = scraper.clean_whitespace(about_text) if about_text else None

            description_text = scraper.get_text_from_element(
                soup, "section", class_name="descriptionSection"
            )

            row["description"] = (
                scraper.clean_whitespace(description_text) if description_text else None
            )

            amenities_section = soup.find("section", class_="amenitiesSection")
            row["amenities"] = get_amenities(amenities_section)

            fees_text = scraper.get_text_from_element(
                soup, "section", class_name="feesSection"
            )

            row["fees"] = scraper.clean_whitespace(fees_text) if fees_text else None

            # Clean up square feet
            row["square_feet"] = (
                remove_letters(row["square_feet"]) if row["square_feet"] else None
            )
            row["bedrooms"] = remove_letters(row["bedrooms"])
            row["bathrooms"] = remove_letters(row["bathrooms"])

            row.update(row)
            logging.info(f"Scraped application: {row['building']}")
            scraper.sleep(min=5, max=10)

        except Exception as err:
            logging.error(
                f"Skipping. Error processing case data from {row['url']}: {err}"
            )

    return scraped_rows


def get_rows(scraper: Scraper, url: str):
    """Extracts all the listings from the main page"""
    scraped_rows = []

    try:
        res = scraper.headless_fetch(url)
        soup = BeautifulSoup(res, "html.parser")

        # Each row represents a current application
        rows = soup.find_all("li", class_="mortar-wrapper")

        for row in rows:
            row_data = {
                "id": None,
                "available": True,
                "url": None,
                "address": None,
                "building": None,
                "monthly_rent": None,
                "bedrooms": None,
                "bathrooms": None,
                "square_feet": None,
                "about": None,
                "description": None,
                "amenities": None,
                "fees": None,
            }

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
        paging = soup.find("nav", {"id": "paging"})
        li_elements = paging.find_all("li")

        for i, li in enumerate(li_elements):
            if li.find("a", class_="active"):

                # Check if there is another li element following the active one
                if i + 1 < len(li_elements):
                    logging.info("Another page found")
                    scraper.sleep(min=10, max=20)
                    url = scraper.get_attribute_from_element(
                        li_elements[i + 1], "a", "href"
                    )
                    if not url:
                        logging.info("No URL for next page found. Breaking")
                        break

                    next_page_rows = get_rows(scraper, url)
                    scraped_rows.extend(next_page_rows)
                    break

        logging.info("No more pages found")

        return scraped_rows

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def scrape(url: str) -> Optional[List[Dict[str, Optional[str]]]]:
    try:
        scraper = Scraper()
        scraper.add_function(get_rows)
        scraper.add_function(get_listings)

        data = scraper.execute(url)
        return data
    finally:
        scraper.quit_web_driver()


if __name__ == "__main__":
    url = "https://www.apartments.com/halifax-ns/"

    data = scrape(url)
    print(len(data))
    for d in data:
        print(d)
        print("\n\n")
