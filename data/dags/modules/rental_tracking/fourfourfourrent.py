import json
import logging
from typing import Optional, Dict, List, Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from modules.scraper.scraper import Scraper
from modules.utils import generate_hash


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def get_building_name(building: str) -> str:
    """Simple lookup table with the buildings owned by paramount who lists on 444rent"""
    building = building.lower()
    if "5450 kaye" in building:
        return "St Joseph's Square"
    if "5 horizon" in building:
        return "Avonhurst Gardens"
    elif "1530 birmingham" in building:
        return "Vertu Suites"
    elif "5144 morris" in building:
        return "Vic Suites"
    elif "1239 barrington" in building:
        return "W Suites"
    elif "1078 tower" in building:
        return "Tower Apartments"
    elif "31 russell lake" in building:
        return "Lakecrest Estates"
    elif "5251 south" in building:
        return "Hillside Suites"
    elif "19 irishtown" in building:
        return "Losts at Greenvale"
    elif "1343 hollis" in building:
        return "Waterford Suites"
    elif "1363 hollis" in building:
        return "Flynn Flats"
    elif "6016 pepperell" in building:
        return "The George"
    else:
        return building



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

    try:
        # Find the main table, then immediate tr children
        table = tab.find("table")
        # Some listings may not have table
        if not table:
            logging.info("No leasing table found")
            return []

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

        # Parse deposit if there is one:
        if leasing_info["deposit"]:
            leasing_info["deposit"] = float(
                leasing_info["deposit"][0].replace("$", "").replace(",", "")
            )

    except Exception as e:
        logging.error(f"Error getting leasing info: {e}")
    finally:
        return json.dumps(leasing_info)


def get_building_info(tab: Tag) -> List[Union[str, Dict[str, str]]]:
    """Extracts all building info from the building tab"""

    building_info = []

    try:
        table = tab.find("table")

        # Some listings may not have table
        if not table:
            logging.info("No building table found")
            return []

        main_row = table.find("tr")
        columns: List[Tag] = main_row.find_all("td", recursive=False)

        if not columns:
            logging.info("No building info columns found")
            return []

        paired_tables = []
        for column in columns:
            tables_to_process = column.find_all("table")

            for i in range(len(tables_to_process)):
                current_table = tables_to_process[i]

                # Check if the current table does not have the 'style' attribute
                if not current_table.get("style"):
                    # Then check the next one
                    if i + 1 < len(tables_to_process):
                        next_table = tables_to_process[i + 1]
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
                    pair[0]
                    .get_text(strip=True)
                    .lower()
                    .replace(" ", "_")
                    .replace(":", "")
                )
                value = pair[1].get_text(strip=True)

                building_info.append({key: value.replace("\xa0", " ")})

    except Exception as e:
        logging.error(f"Error getting building info: {e}")
    finally:
        return json.dumps(building_info)


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
            tables = miscellaneous.find_all("table")
            for table in tables:
                tds = table.find_all("td")

                for td in tds:
                    # Those that are styled are bullet points
                    if td.get("style"):
                        continue

                    suite_info["miscellaneous"].append(td.get_text(strip=True))

        # Get all tables, skipping the first if it's the miscellaneous section
        tables_to_process = tab.find_all("table", recursive=False)
        if miscellaneous:
            tables_to_process = tables_to_process[1:]

        # Identify paired tables and collect their information
        for i in range(0, len(tables_to_process), 2):
            # Assume tables come in pairs: title, details
            title_table = tables_to_process[i]

            # Check if the next table would be valid
            detail_table = (
                tables_to_process[i + 1] if i + 1 < len(tables_to_process) else None
            )

            # The use bgcolor on the details, not the title
            if (
                title_table
                and detail_table
                and not title_table.get("bgcolor")
                and detail_table.get("bgcolor")
            ):
                key = title_table.get_text(strip=True).lower()
                suite_info[key] = [
                    td.get_text(strip=True).replace("\xa0", " ")
                    for td in detail_table.find_all("td")
                ]
            elif title_table and not title_table.get("bgcolor"):
                # If there's a title table without a detail table following, add contents to miscellaneous
                suite_info["miscellaneous"].append(
                    title_table.get_text(strip=True).replace("\xa0", " ")
                )

    except Exception as e:
        logging.error(f"Error getting suite info: {e}")
    finally:
        return json.dumps(suite_info)


def get_tab_content(scraper: Scraper, listings: List[Dict[str, Optional[str]]]):
    """Get the content from the leasing, description, building, and suite tabs on the page"""

    for listing in listings:
        try:

            tabs = listing.pop("tabs", None)
            if not tabs:
                continue

            listing["leasing_info"] = get_leasing_info(tabs[0])
            listing["description_info"] = tabs[1].get_text(strip=True)
            listing["building_info"] = get_building_info(tabs[2])
            listing["suite_info"] = get_suite_info(tabs[3])

        except Exception as err:
            logging.error(f"Error processing tab content from {url}: {err}")

    return listings


def get_listings(
    scraper: Scraper, rows: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Optional[str]]]:
    """Scrape listing content from the rows of the main table"""
    for row in rows:

        try:
            res = scraper.fetch(row["url"])

            soup = BeautifulSoup(res.content, "html.parser")

            row["rooms"] = scraper.get_text_from_element(
                soup, "div", attributes={"id": "suitemain"}
            )
            row["address"] = scraper.get_text_from_element(
                soup, "div", attributes={"id": "addressmain"}
            )

            tab_container = soup.find("div", class_="tab_container")
            tabs = tab_container.find_all("div", class_="tab_content")

            if tabs:
                # Only want first 4 for now
                row["tabs"] = tabs[:4]

            logging.info(f"Scraped application: {row['url']}")

        except Exception as err:
            logging.error(f"Error processing listing data from {row['url']}: {err}")
        finally:
            scraper.sleep(min=1, max=2)

    return rows


def get_rows(scraper: Scraper, tables: List[Tag]) -> List[Dict]:
    """Extracts all the rows and relevant data from all the tables"""
    all_rows = []

    for table in tables:
        rows: List[Tag] = table.find_all("tr", bgcolor=True)

        for row in rows:
            row_data = {
                "id": None,
                "available": True,
                "url": None,
                "address": None,
                "building": None,
                "unit": None,
                "location": None,
                "square_feet": None,
                "available_date": None,
                "price": None,
                "management": "Paramount Management",
                "rooms": None,
                "tabs": None,
            }

            href = scraper.get_attribute_from_element(row, "a", "href")

            # Skip broken links
            if not href:
                logging.warning("Unable to find href for row")
                continue

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
                row_data[field] = scraper.clean_whitespace(
                    columns[i].get_text(strip=True)
                )

            # Update unit
            unit = row_data["unit"]
            if unit == "-":
                row_data["unit"] = None

            # Parse square feet and price
            row_data["square_feet"] = float(
                row_data["square_feet"].replace(",", "").replace(" ft2", "")
            )
            row_data["price"] = float(
                row_data["price"].replace("$", "").replace(",", "")
            )

            # Update building name:
            row_data["building"] = get_building_name(row_data["building"])

            # Create an id using the building name and unit:
            id_str = (
                row_data["building"] + row_data["unit"]
                if row_data["unit"]
                else row_data["building"]
            )
            row_data["id"] = generate_hash(id_str)

            all_rows.append(row_data)

    return all_rows


def get_tables(scraper: Scraper, url: str) -> List[Tag]:
    """Extracts tables containing listing info"""
    tables = []

    try:
        res = scraper.fetch(url)
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
