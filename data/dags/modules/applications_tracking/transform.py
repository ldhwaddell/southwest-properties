import logging

from typing import Tuple, List, Dict

from .data import data

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


def transform(record: Tuple) -> List[Dict]:
    """
    Cleans up scraped applications and formats them for storage in processed data table

    Currently a dummy function. Used to illustrate data flow

    Args:
    record (Tuple): The record pulled from the scraped data table to process

    Returns:
    """
    record_id = record[0]
    created_at = record[1]
    source = record[2]
    ran_at = record[3]
    data = record[4]

    logging.info(f"Processing record id {record_id} created at {created_at}")

    # for entry in data:
    #     # Individual transformation steps will occur here
    #     ...

    return data
