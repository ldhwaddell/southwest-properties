import copy
import json
import logging
import pendulum
import re

from airflow.providers.redis.hooks.redis import RedisHook
from requests import ConnectionError
from typing import Optional, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from modules.scraper.scraper import Scraper
from modules.utils import generate_hash, clean_whitespace, load_from_redis


logger = logging.basicConfig(
# Set up logger
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)

schema = {
    "url": None,
    "summary": None,
    "title": None,
    "id": None,
    "last_updated": None,
    "update_notice": None,
    "request": None,
    "proposal": None,
    "process": None,
    "status": None,
    "documents_submitted_for_evaluation": None,
    "contact_info": {
        "name": None,
        "telephone": None,
        "fax": None,
        "email": None,
        "mailing_address": [],
        "attention": None,
    },
}


def get_contact_info(contact_info_html: Tag) -> str:
    """
    Extract all relevant contact info from the contact html of the applications list

    Args:
    contact_info_html (Tag): The html div containing the contact info

    Returns:
    str: a stringified json dict of the extracted info
    """

    contact_schema = {
        "name": None,
        "telephone": None,
        "fax": None,
        "email": None,
        "mailing_address": [],
        "attention": None,
    }

    try:
        # Every application has 2 contact info divs at the bottom
        name_div, mailing_div = contact_info_html.find_all(
            "div", class_="o-layout__item col-6"
        )

        name_div: Tag
        mailing_div: Tag

        # Extract name, telephone, fax, email
        for p_tag in name_div.find_all("p", class_="u-text-small"):
            if "text-bold" in p_tag["class"]:
                contact_schema["name"] = p_tag.get_text(strip=True)

            elif "Telephone:" in p_tag.get_text():
                contact_schema["telephone"] = p_tag.find("a").get_text(strip=True)

            elif "Fax:" in p_tag.get_text():
                contact_schema["fax"] = p_tag.get_text(strip=True).replace("Fax:", "")

            elif "Email:" in p_tag.get_text():
                contact_schema["email"] = p_tag.find("a").get_text(strip=True)

        # Extract mailing address and attention
        for p_tag in mailing_div.find_all("p", class_="u-text-small"):
            if "Attention:" in p_tag.get_text():
                contact_schema["attention"] = p_tag.get_text(strip=True).replace(
                    "Attention:", ""
                )

            else:
                # Add other parts to the mailing address list
                contact_schema["mailing_address"].append(
                    p_tag.get_text(strip=True).replace("PO Box:", "")
                )

        # Join the address parts into a single string
        contact_schema["mailing_address"] = " ".join(contact_schema["mailing_address"])

    except Exception as e:
        logging.error(f"Error getting contact info: {e}")

    return contact_schema


def get_sections(sections: List[Tag]) -> Dict:
    """
    Extract all relevant info from the sections html of the applications list

    Args:
    sections (List[Tag]): The list of section elements that were found

    Returns:
    Dict: A dict of the extracted sections
    """
    section_data = {}

    for section in sections:
        try:
            header = section.find("h2")
            if not header:
                continue

            section_title = header.get_text().lower().strip().replace(" ", "_")

            # Remove h2 title tags
            h2_tags: List[Tag] = section.find_all("h2", class_="h3")
            if h2_tags:
                [h2.extract() for h2 in h2_tags]

            inner_html = section.decode_contents()

            # Removes the spacers
            html_no_spaces = re.sub(r"<p>\s*_{10,}\s*</p>", "", inner_html)

            if not html_no_spaces:
                continue

            soup = BeautifulSoup(html_no_spaces, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                if not a_tag["href"].startswith(("http", "cdn")):
                    a_tag["href"] = "https://halifax.ca" + a_tag["href"]

            # Convert the soup object back to a string after modification
            modified_html = str(soup)

            section_data[section_title] = clean_whitespace(modified_html)

        except Exception as e:
            logging.error(f"Error getting section: {e}")

    return section_data


def get_update_notice(soup: BeautifulSoup) -> Optional[str]:
    """
    Finds and extracts the html that makes up the update notice, if it exists

    Args:
    soup (BeautifulSoup): The soup to search

    Returns:
    Optional[str]: html of the update notice, or none if there isn't one
    """
    element_container = soup.find("div", class_="c-planning-notification")
    if not element_container:
        return None

    text_container = element_container.find("p", class_="u-text-body-color")
    return text_container.decode_contents()


def get_applications() -> Dict:
    """
    Get each application from a list of application urls and corresponding summaries

    Returns:
    Dict: A dict of the scraped applications
    """
    # Read from redis
    redis_hook = RedisHook(redis_conn_id="redis_conn").get_conn()

    value = load_from_redis(conn_id="redis_conn", key="applications_data")
    applications_data = json.loads(value)

    applications: List[Dict] = applications_data["data"]

    scraper = Scraper()

    for application in applications:

        try:
            res = scraper.fetch(application["url"])
            soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

            application["title"] = scraper.get_text_from_element(
                soup, "h1", class_name="title"
            )

            application["id"] = generate_hash(application["title"])

            # Get and parse the last time it was updated
            last_updated = scraper.get_attribute_from_element(
                soup, "time", attribute="datetime", class_name="datetime"
            )
            if last_updated:
                application["last_updated"] = (
                    pendulum.parse(last_updated).to_datetime_string() + "+00:00"
                )

            # Get the last updated notice if there is one
            update_notice = get_update_notice(soup)
            if update_notice:
                application["update_notice"] = clean_whitespace(update_notice)

            # Get the main sections
            sections = soup.find_all("div", class_="u-text-lighter")
            if sections:
                sections_data = get_sections(sections)
                application.update(sections_data)

            contact_info_html = soup.find("div", class_="paragraph--type--contact-info")
            if contact_info_html:
                contact_info = get_contact_info(contact_info_html)
                application["contact_info"] = contact_info

            logging.info(f"Scraped application: {application['title']}")

        except ConnectionError as e:
            logging.error(
                f"Connection failed for URL: {application['url']}. Error: {e}"
            )
        except Exception as err:
            logging.error(
                f"Error processing case data from {application['url']}: {err}"
            )
        finally:
            scraper.sleep()

    redis_hook.set("scraped_applications", json.dumps(applications_data))


def parse_application_row(scraper: Scraper, row: Tag, base_url: str) -> Optional[Dict]:
    """
    Parses a single row of the application data using a predefined schema.

    Args:
    scraper (Scraper): The scraper instance
    row (Tag): The row element extracted by bs4
    base_url (str): The base url to apped the href to

    Returns:
    Optional[Dict]: A dictionary containing data about the application, or None if no href is found.
    """
    row_data = copy.deepcopy(schema)

    href = scraper.get_attribute_from_element(row, "a", "href")
    if not href:
        logging.warning("Unable to find href in the row.")
        return None

    row_data["url"] = urljoin(base_url, href)
    row_data["summary"] = scraper.get_text_from_element(
        row, "div", class_name="views-field views-field-field-summary"
    )

    return row_data


def get_application_urls() -> Optional[Dict]:
    """
    Scrapes the application URLs and summaries from each row on the planning applications page.

    Returns:
    Optional[Dict]: A dictionary containing data about the scrape and each application, or None if an error occurs.
    """
    url = "https://www.halifax.ca/business/planning-development/applications"
    redis_hook = RedisHook(redis_conn_id="redis_conn").get_conn()

    scraper = Scraper()
    data = {"source": url, "ran_at": pendulum.now().to_iso8601_string(), "data": None}

    try:
        res = scraper.fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")

        rows = soup.find_all("div", class_="views-row")
        if not rows:
            raise ValueError(f"No rows to scrape found for URL: {url}")

        applications = []
        for row in rows:
            parsed_row = parse_application_row(scraper, row, url)

            if parsed_row:
                applications.append(parsed_row)

        data["data"] = applications

        # Save to redis
        redis_hook.set("applications_data", json.dumps(data))

    except ConnectionError as e:
        logging.error(f"Connection failed for URL: {url}. Error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unknown error occurred fetching: {url}. Error: {e}")
        raise
