import logging

from typing import Tuple, List, Dict

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


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

    return data
