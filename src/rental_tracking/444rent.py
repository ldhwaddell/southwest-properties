import json
import logging
import re
from typing import Optional, Dict, Union, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.utils import generate_hash
from src.scraper.scraper import Scraper


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def get_leasing_info(tab: Tag) -> Dict[str, Optional[List[str]]]:
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

    # Find the main table, then immediate tr children
    table = tab.find("table")
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
    return leasing_info


def get_building_info(tab: Tag):
    building_info = []

    table = tab.find("table")
    main_row = table.find("tr")
    columns = main_row.find_all("td", recursive=False)

    paired_tables = []
    for column in columns:
        tables = column.find_all("table")

        for i in range(len(tables)):
            current_table = tables[i]

            # Check if the current table does not have the 'style' attribute
            if not current_table.get("style"):
                # Then check the next one
                if i + 1 < len(tables):
                    next_table = tables[i + 1]
                    if next_table.get("style"):
                        # If the next one is a match, skip rest of iteration
                        paired_tables.append((current_table, next_table))
                        continue

                # This is only reached when the previous table has no style, but the next one doesnt either
                paired_tables.append((current_table,))

    # Now paired_tables contains tuples of (non-styled table, styled table) or (styled table,)
    for pair in paired_tables:

        if len(pair) == 1:
            building_info.append(pair[0].get_text(strip=True))
        else:
            key = (
                pair[0].get_text(strip=True).lower().replace(" ", "_").replace(":", "")
            )
            value = pair[1].get_text(strip=True)

            building_info.append({key: value})

    return building_info


def get_tab_content(scraper: Scraper, listings: List[Dict[str, Optional[str]]]):
    tabs_data = {"leasing": None, "description": None, "building": None, "suite": None}

    for listing in listings:
        try:

            tabs = listing.pop("tabs", None)
            if not tabs:
                continue

            tabs_data["leasing"] = get_leasing_info(tabs[0])
            tabs_data["description"] = tabs[1].get_text(strip=True)
            tabs_data["building"] = get_building_info(tabs[2])
            # tabs_data["suite"] = get_suite_info(tabs[3])
            listing.update(tabs_data)

        except Exception as err:
            logging.error(f"Error processing case data from {url}: {err}")

    return listings


def get_listings(
    scraper: Scraper, rows: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Optional[str]]]:
    for row in rows:
        row_data = {"rooms": None, "tabs": None}

        try:
            res = scraper.fetch(row["url"])
            soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

            row_data["rooms"] = scraper.get_text_from_element(
                soup, "div", attributes={"id": "suitemain"}
            )

            tab_container = soup.find("div", class_="tab_container")
            tabs = tab_container.find_all("div", class_="tab_content")

            if tabs:
                # Only want first 4 for now
                row_data["tabs"] = tabs[:4]

            row.update(row_data)

        except Exception as err:
            logging.error(f"Error processing case data from {url}: {err}")

    return rows


def get_rows(scraper: Scraper, tables: List[Tag]) -> List[Dict]:
    """Extracts all the rows and relevant data from all the tables"""
    all_rows = []

    for table in tables:
        rows = table.find_all("tr", bgcolor=True)

        for row in rows:
            row_data = {
                "url": None,
                "building": None,
                "unit": None,
                "location": None,
                "area": None,
                "available": None,
                "price": None,
            }

            href = scraper.get_attribute_from_element(row, "a", "href")

            # Skip broken links
            if not href:
                logging.warning("Unable to find href for row")
                continue

            # Generate listing URL
            row_data["url"] = urljoin("https://www.444rent.com", href)

            # Extract column data
            columns = row.find_all("td")
            row_data["building"] = scraper.clean_whitespace(
                columns[0].get_text(strip=True)
            )
            row_data["unit"] = scraper.clean_whitespace(columns[1].get_text(strip=True))
            row_data["location"] = scraper.clean_whitespace(
                columns[2].get_text(strip=True)
            )
            row_data["area"] = scraper.clean_whitespace(columns[3].get_text(strip=True))
            row_data["available"] = scraper.clean_whitespace(
                columns[4].get_text(strip=True)
            )
            row_data["price"] = scraper.clean_whitespace(
                columns[5].get_text(strip=True)
            )

            all_rows.append(row_data)

    return all_rows[:5]


def get_tables(scraper: Scraper, url: str) -> List[Tag]:
    """Extracts tables containing listing info"""
    tables = []

    try:
        res = scraper.fetch(url, allow_redirects=True)
        soup = BeautifulSoup(res.content, "html.parser")

        tables = soup.find_all("table", {"bgcolor": "#ffffff"})

        if not tables:
            logging.warning("Unable to find tables to scrape")
            return None

        return tables

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def scrape(url: str) -> Optional[List[Dict[str, Optional[str]]]]:
    """Build and executed the scraper"""
    scraper = Scraper()
    scraper.add_function(get_tables)
    scraper.add_function(get_rows)
    scraper.add_function(get_listings)
    scraper.add_function(get_tab_content)
    data = scraper.execute(url)

    return data


if __name__ == "__main__":
    url = "https://www.444rent.com/apartments.asp"

    data = scrape(url)
    for d in data:
        print(d)
        print("\n\n")
