import logging
import pendulum
import re

from typing import Tuple, List, Dict
import pendulum.exceptions

from modules.utils import generate_hash

import psycopg2


# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def get_building(building: str) -> str:
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
    elif "7037 mumford" in building:
        return "West22 Living"
    elif "1254 hollis" in building:
        return "Acadia Suites"
    elif "5157 morris" in building:
        return "Renaissance South"
    else:
        return building


def parse_unit(unit: str) -> int:

    cleaned_unit = unit.split("-")[-1]

    return parse_number(cleaned_unit, int)


def parse_square_feet(square_feet: str) -> float:

    cleaned_str = square_feet.replace("ft2", "")

    return parse_number(cleaned_str, float)


def parse_number(s: str, type):
    try:
        cleaned_str = "".join(filter(lambda x: x.isdigit() or x == ".", s))

        return type(cleaned_str)
    except ValueError as e:
        logging.error(f"Error ocurred parsing float: {e}")
        return s


def parse_date(date: str):

    if date == "Now":
        return pendulum.now().date().to_date_string()

    format_string = "MMM D, YYYY"

    try:
        parsed_date = pendulum.from_format(date, format_string)
        return parsed_date.date().to_date_string()
    except Exception as e:
        logging.error(f"Error ocurred parsing date: {e}")
        return date


def parse_bedrooms(bedrooms: str):
    if bedrooms == "Bachelor":
        return 1
    else:
        return parse_number(bedrooms, int)


def parse_bathrooms(bathrooms: str):
    if bathrooms == "Bachelor":
        return 1

    match = re.search(r"(\d+)\s*Baths?", bathrooms, re.IGNORECASE)
    return parse_number(match.group(1), int)


def parse_den(rooms: str) -> bool:
    return "DEN" in rooms


def clean_leasing_info(info: Dict) -> Dict:
    for key, val in info.items():

        if val:
            cleaned_val = [s.replace("\xa0", " ") for s in val]
            info[key] = cleaned_val

        if key == "deposit":
            cleaned_deposit = parse_number(info[key][0], float)
            info[key][0] = cleaned_deposit

    return info


def clean_suite_info(info: Dict) -> Dict:
    for key, val in info.items():
        if val:
            cleaned_val = [s.replace("\xa0", " ") for s in val]
            info[key] = cleaned_val
    return info


def transform(record: Tuple) -> List[Dict]:
    """
    Extracts applications from the raw data
    """

    record_id = record[0]
    created_at = record[1]
    source = record[2]
    ran_at = record[3]
    data = record[4]
    logging.info(f"Processing record id {record_id} created at {created_at}")

    for listing in data:
        # Generate unique ID
        id_str = str(listing["building"]) + str(listing["unit"])
        listing["id"] = generate_hash(id_str)
        
        # Assign record source
        listing["source"] = source

        # Get building name if it exists
        listing["building"] = get_building(listing["building"])

        # Turn the unit to number
        listing["unit"] = parse_unit(listing["unit"])

        # Turn the square feet to number
        listing["square_feet"] = parse_square_feet(listing["square_feet"])

        # Available date?
        listing["available_date"] = parse_date(listing["available_date"])

        # Turn the price to number
        listing["price"] = parse_number(listing["price"], float)

        # Get the number of bedrooms
        listing["bedrooms"] = parse_bedrooms(listing["bedrooms"])

        # Check if listing has den
        listing["den"] = parse_den(listing["bathrooms"])

        # Get number of bathrooms
        listing["bathrooms"] = parse_bathrooms(listing["bathrooms"])

        # Description info does not need to be cleaned
        listing["leasing_info"] = clean_leasing_info(listing["leasing_info"])
        listing["description_info"] = listing["description_info"].replace("\xa0", " ")
        listing["suite_info"] = clean_suite_info(listing["suite_info"])

    return data


if __name__ == "__main__":
    conn = psycopg2.connect(user="airflow", password="southwest2024", host="localhost")
    cursor = conn.cursor()
    sql = f"SELECT * FROM scraped_fffrent_listings ORDER BY created_at DESC LIMIT 1"
    cursor.execute(sql)
    record = cursor.fetchone()

    data = transform(record)

    for d in data:
        print(d)
        print("\n\n")
