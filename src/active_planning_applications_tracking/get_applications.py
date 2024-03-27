import json
import logging

from typing import Optional, Dict, List
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.utils import generate_hash
from src.scraper.scraper import Scraper


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def get_contact_info(
    scraper: Scraper, applications: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Optional[str]]]:
    """Extract all relevant contact info from the contact html of the applications list"""

    for application in applications:
        contact_info_html = application.pop("contact_info_html", None)
        if not contact_info_html:
            continue

        contact_info = {
            "name": None,
            "telephone": None,
            "fax": None,
            "email": None,
            "mailing_address": [],
            "attention": None,
        }

        # Every application has 2 contact info divs at the bottom
        name_div, mailing_div = contact_info_html.find_all(
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

        application["contact_info"] = json.dumps(contact_info)

    return applications


def get_sections(
    scraper: Scraper, applications: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Optional[str]]]:
    """Extract all relevant info from the sections html of the applications list"""

    for application in applications:
        sections = application.pop("sections_html", None)
        if not sections:
            continue

        section_data = {
            "request": None,
            "proposal": None,
            "process": None,
            "status": None,
            "documents_submitted_for_evaluation": None,
        }

        for section in sections:
            header: Tag = section.find("h2")
            if header:
                section_title = header.get_text().lower().strip().replace(" ", "_")

                # Avoid rescraping the h2 tag that contains the title of section
                text_parts = []
                for elem in section.children:
                    if isinstance(elem, Tag) and elem.name != "h2":
                        text_parts.append(elem.get_text(strip=True))

                joined_text = " ".join(text_parts).strip()
                section_data[section_title] = scraper.clean_whitespace(joined_text)

        application.update(section_data)

    return applications


def get_cases(
    scraper: Scraper, applications: List[Dict[str, Optional[str]]]
) -> List[Dict[str, Optional[str]]]:
    """Get each case from a list of case urls and corresponding summaries"""
    # applications = []

    for application in applications:
        application_data = {
            "title": None,
            "id": None,
            "last_updated": None,
            "update_notice": None,
            "sections_html": None,
            "contact_info_html": None,
        }

        try:
            res = scraper.fetch(application["url"])
            soup: BeautifulSoup = BeautifulSoup(res.content, "html.parser")

            application_data["title"] = scraper.get_text_from_element(
                soup, "h1", "title"
            )
            application_data["id"] = generate_hash(application_data["title"])

            # Get and parse the last time it was updated
            last_updated = scraper.get_attribute_from_element(
                soup, "time", attribute="datetime", class_name="datetime"
            )
            application_data["last_updated"] = scraper.parse_iso8601_date(last_updated)

            application_data["update_notice"] = scraper.get_text_from_element(
                soup, "div", "c-planning-notification"
            )

            # Get the html for the sections and contact info for futher processing
            application_data["sections_html"] = soup.find_all(
                "div", class_="u-text-lighter"
            )
            application_data["contact_info_html"] = soup.find(
                "div", class_="paragraph--type--contact-info"
            )

            application.update(application_data)

            logging.info(f"Scraped application: {application_data['title']}")
            scraper.sleep()

        except Exception as err:
            logging.error(
                f"Error processing case data from {application['url']}: {err}"
            )
            # applications.append(None)

    return applications


def get_rows(scraper: Scraper, url: str) -> Optional[Dict]:
    """Scrapes the applications urls and summary from each row on the planning applications page"""
    applications = []

    try:
        res = scraper.fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Each row represents a current application
        rows = soup.find_all("div", class_="views-row")

        for row in rows:
            row_data = {"url": None, "summary": None}
            href = scraper.get_attribute_from_element(row, "a", "href")

            # Skip broken links
            if not href:
                logging.warning("Unable to find href for row")
                continue

            # Build the url for the case represented by the row
            row_data["url"] = urljoin(url, href)

            # Extract the summary from row
            row_data["summary"] = scraper.get_text_from_element(
                row, "div", class_name="views-field views-field-field-summary"
            )

            applications.append(row_data)

        return applications

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def scrape(url: str) -> Optional[List[Dict[str, Optional[str]]]]:
    """Build and executed the scraper"""
    scraper = Scraper()
    scraper.add_function(get_rows)
    scraper.add_function(get_cases)
    scraper.add_function(get_sections)
    scraper.add_function(get_contact_info)
    data = scraper.execute(url)

    return data


# if __name__ == "__main__":
#     main()
