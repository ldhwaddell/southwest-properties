import logging
from typing import Optional, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from modules.scraper.scraper import Scraper


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

    try:
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

    except Exception as e:
        logging.error(f"Error getting leasing info: {e}")
    finally:
        return leasing_info


def get_building_info(tab: Tag) -> List[str | Dict[str, str]]:
    """Extracts all building info from the building tab"""

    building_info = []

    try:
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
                    td.get_text(strip=True).replace("\xa0", " ") for td in detail_table.find_all("td")
                ]
            elif title_table and not title_table.get("bgcolor"):
                # If there's a title table without a detail table following, add contents to miscellaneous
                suite_info["miscellaneous"].append(title_table.get_text(strip=True).replace("\xa0", " "))

    except Exception as e:
        logging.error(f"Error getting suite info: {e}")
    finally:
        return suite_info


def get_tab_content(scraper: Scraper, listings: List[Dict[str, Optional[str]]]):
    """Get the content from the leasing, description, building, and suite tabs on the page"""
    tabs_data = {"leasing": None, "description": None, "building": None, "suite": None}

    for listing in listings:
        try:

            tabs = listing.pop("tabs", None)
            if not tabs:
                continue

            tabs_data["leasing"] = get_leasing_info(tabs[0])
            tabs_data["description"] = tabs[1].get_text(strip=True)
            tabs_data["building"] = get_building_info(tabs[2])
            tabs_data["suite"] = get_suite_info(tabs[3])
            listing.update(tabs_data)

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
            tab_container = soup.find("div", class_="tab_container")
            tabs = tab_container.find_all("div", class_="tab_content")

            if tabs:
                # Only want first 4 for now
                row["tabs"] = tabs[:4]

            logging.info(f"Scraped application: {row['url']}")

        except Exception as err:
            logging.error(f"Error processing listing data from {row['url']}: {err}")
            print(res.content)
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
                "url": None,
                ######
                "management": "Paramount Management",
                "contact_info": None,
                "rooms": None,
                "tabs": None,
                ######
                "building": None,
                "unit": None,
                "location": None,
                "square_feet": None,
                "available_date": None,
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
