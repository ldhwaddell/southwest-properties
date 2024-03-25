import json
import logging
import random
import time
from typing import Optional, Dict, Union, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.utils import fetch, generate_hash
from src.database.database import Database
from src.database.models import ActivePlanningApplications


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


def get_datetime_from_element(
    soup: BeautifulSoup, tag: str, class_name: Optional[str] = None
) -> Optional[str]:
    element = soup.find(tag, class_=class_name)
    return element.get("datetime") if element else None


def get_contact_info(soup: BeautifulSoup) -> Dict[str, Union[str, List[str], None]]:
    contact_info_div = soup.find("div", class_="paragraph--type--contact-info")

    if not contact_info_div:
        return None

    contact_info = {
        "name": None,
        "telephone": None,
        "fax": None,
        "email": None,
        "mailing_address": [],
        "attention": None,
    }

    # Every applicaiton has 2 contact info divs at the bottom
    name_div, mailing_div = contact_info_div.find_all(
        "div", class_="o-layout__item col-6"
    )

    # Extract name, telephone, fax, email
    for p_tag in name_div.find_all("p", class_="u-text-small"):
        if "text-bold" in p_tag["class"]:
            contact_info["name"] = p_tag.get_text(strip=True)

        elif "Telephone:" in p_tag.get_text():
            contact_info["telephone"] = p_tag.find("a").get_text(strip=True)

        elif "Fax:" in p_tag.get_text():
            contact_info["fax"] = p_tag.get_text(strip=True).replace("Fax:", "")

        elif "Email:" in p_tag.get_text():
            contact_info["email"] = p_tag.find("a").get_text(strip=True)

    # Extract mailing address and attention
    for p_tag in mailing_div.find_all("p", class_="u-text-small"):
        if "Attention:" in p_tag.get_text():
            contact_info["attention"] = p_tag.get_text(strip=True).replace(
                "Attention:", ""
            )

        else:
            # Add other parts to the mailing address list
            contact_info["mailing_address"].append(
                p_tag.get_text(strip=True).replace("PO Box:", "")
            )

    # Join the address parts into a single string
    contact_info["mailing_address"] = " ".join(contact_info["mailing_address"])

    return json.dumps(contact_info)


def get_section_data(soup: BeautifulSoup, class_name: str) -> Dict[str, str]:
    sections = soup.find_all("div", class_=class_name)

    section_data = {}
    for section in sections:
        header: Tag = section.find("h2")
        if header:
            section_title = header.get_text().lower().strip().replace(" ", "_")

            # Avoid rescraping the h2 tag that contains the title of section
            text_parts = []
            for elem in section.children:
                if isinstance(elem, Tag) and elem.name != "h2":
                    text_parts.append(elem.get_text(strip=True))

            section_data[section_title] = " ".join(text_parts).strip()

    return section_data


def get_case(url: str) -> Optional[Dict[str, Optional[str]]]:
    case_data = {
        "title": None,
        "last_updated": None,
        "update_notice": None,
        "request": None,
        "proposal": None,
        "process": None,
        "status": None,
        "contact_info": None,
        "documents_submitted_for_evaluation": None,
    }

    try:
        res = fetch(url)
        soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")
        case_data["title"] = get_text_from_element(soup, "h1", "title")
        case_data["id"] = generate_hash(case_data["title"])
        case_data["last_updated"] = get_datetime_from_element(
            soup, "time", class_name="datetime"
        )
        case_data["update_notice"] = get_text_from_element(
            soup, "div", "c-planning-notification"
        )
        case_data["contact_info"] = get_contact_info(soup)
        # Get the text from every section that appears in the application
        case_data.update(get_section_data(soup, "u-text-lighter"))

        return case_data

    except Exception as err:
        logging.error(f"Error processing case data from {url}: {err}")
        return None


def scrape(url: str) -> Optional[Dict]:
    scraped_data = []

    try:
        res = fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Each row represents a current application
        rows = soup.find_all("div", class_="views-row")

        for row in rows:
            a_tag = row.find("a")

            # Skip broken links
            if not a_tag or not a_tag.has_attr("href"):
                logging.warning("Unable to find href for row")
                continue

            # Build the url for the case represented by the row
            href = a_tag.get("href")
            row_url = urljoin(url, href)

            summary = row.find(
                "div", class_="views-field views-field-field-summary"
            ).get_text()

            case_data = get_case(row_url)
            case_data["summary"] = summary

            scraped_data.append(case_data)

            logging.info(f"Scraped application: {case_data['title']}")

            sleep_duration = round(random.uniform(0, 2), 1)
            logging.info(f"Sleeping for {sleep_duration} seconds")
            time.sleep(sleep_duration)

        return scraped_data

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def main():
    url = "https://www.halifax.ca/business/planning-development/applications"

    data = scrape(url)

    db = Database("sqlite:///southwest.db")
    db.compare_and_insert(ActivePlanningApplications, data)


if __name__ == "__main__":
    main()
