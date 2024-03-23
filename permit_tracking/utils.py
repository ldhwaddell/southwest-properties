import functools
import logging
import time
from typing import Callable, Any

import requests
from fake_useragent import UserAgent
from requests import Response, HTTPError


def retry(retries: int, retry_sleep_sec: int) -> Callable[..., Any]:
    """
    Decorator to add retry logic to a function.

    :param retries: the maximum number of retries.
    :param retry_sleep_sec: the number of seconds to sleep between retries.
    :return: A decorator that adds retry logic to a function.
    """

    def decorator(func):

        # Preserves info about original function. Otherwise func name will be "wrapper" not "func"
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(retries):
                try:
                    return func(
                        *args, **kwargs
                    )  # should return the raw function's return value
                except Exception as e:
                    logging.error(f"Error: {e}")
                    time.sleep(retry_sleep_sec)

                logging.error(f"Trying attempt {attempt+1} of {retries}")

            logging.error(f"Function {func} retry failed")

            raise Exception(f"Exceeded max retry num: {retries} failed")

        return wrapper

    return decorator


@retry(retries=3, retry_sleep_sec=5)
def fetch(url: str) -> Response:
    """
    Fetches a URL, streams the response. Raises exception if the status code is invalid.

    :param url: The URL to fetch
    :return: The response if valid, otherwise raises exception
    """
    user_agent = UserAgent()
    headers = {"User-Agent": user_agent.random}
    res = requests.get(url, stream=True, headers=headers)
    res.raise_for_status()
    return res
