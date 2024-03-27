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


def get_tab_content(tab: Tag):
    info_list = []

    print(len(tab.find_all("tr")))

    # for tr in tab.find_all("tr"):
    #     print(tr)
    #     print("\n\n\n")
    #     row_info = {}

    # tds = tr.find_all("td")
    # if tds:
    #     key = tds[0].find("b", class_="normal").get_text(strip=True).rstrip(":")
    #     print(key)

    #     value = " ".join(
    #         [item.get_text(strip=True) for item in tds[1].find_all(recursive=False)]
    #     )

    #     # Add the key-value pair to the row info
    #     row_info[key] = value

    # if row_info:  # If the row_info dict is not empty, add it to the info_list
    #     info_list.append(row_info)


# def get_listing(url: str):
#     try:
#         res = fetch(url)
#         soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
#         tab_container = soup.find("div", class_="tab_container")

#         tabs = tab_container.find_all("div", class_="tab_content")

#         for tab in tabs[:5]:
#             tab_info = get_tab_content(tab)

#     except Exception as err:
#         logging.error(f"Error processing case data from {url}: {err}")
#         return None


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
            a_tag = row.find("a")
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

    return all_rows


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
    # scraper.add_function()
    data = scraper.execute(url)

    return data


if __name__ == "__main__":
    url = "https://www.444rent.com/apartments.asp"

    data = scrape(url)
    print(data)
