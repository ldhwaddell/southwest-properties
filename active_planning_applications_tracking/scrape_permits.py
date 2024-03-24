import logging
import random
import time
from typing import Optional, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from utils import fetch


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


"""
DB Schema
Title
Summary
last updated
Update notice (gray box thing)
Request
Proposal
Process
Status
Docs submitted for eval
contact info

"""

def get_case(url: str):
    try:
        res = fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")
        title = soup.find("h1", class_="title").get_text()
        last_updated = soup.find("time").get("datetime")

        # Get notification if there is one
        print(soup.find("div", class_="c-planning-notification"))

        return {"title": title, "last_updated": last_updated}

    except Exception as e:
        logging.error(f"Unable to get case: {url}. Error: {e}")
        return None


def halifax_business_planning_development_applications(url: str) -> Optional[Dict]:
    scraped_data = {}

    try:
        res = fetch(url)
        soup = BeautifulSoup(res.content, "html.parser")

        # Each row represents a current application
        rows = soup.find_all("div", class_="views-row")

        for row in rows:
            a_tag = row.find("a")

            if not a_tag or not a_tag.has_attr("href"):
                logging.warning("Unable to find href for row")
                continue

            href = a_tag.get("href")
            # The url for the case represented by the row
            row_url = urljoin(url, href)

            summary = row.find(
                "div", class_="views-field views-field-field-summary"
            ).get_text()
            case_data = get_case(row_url)

            sleep_duration = round(random.uniform(2, 4), 3)
            logging.info(f"Sleeping for {sleep_duration} seconds")
            time.sleep(sleep_duration)

        return scraped_data

    except Exception as e:
        logging.error(f"Unable to get URL: {url}. Error: {e}")
        return None


def main(url_function_map):
    for url in url_function_map:
        url_function_map[url](url)


if __name__ == "__main__":
    url_function_map = {
        "https://www.halifax.ca/business/planning-development/applications": halifax_business_planning_development_applications
    }
    main(url_function_map)
