import logging
from typing import Any

import requests
from requests.exceptions import HTTPError, RequestException

from core.config import settings
from users.interfaces import AbstractCreditCardApiClient, AbstractUserApiClient

logger = logging.getLogger(__name__)


class BaseApiClient:
    """Base class for all external API clients, handling common request logic."""

    @staticmethod
    def _get(url: str) -> Any:
        """
        Executes a synchronous GET request. Raises exceptions on network or HTTP errors.

        :param url: The URL address for the request.
        :return: Deserialized JSON response data.
        :raises requests.RequestException: If a request error (network or timeout) occurs.
        :raises requests.HTTPError: If an HTTP status code 4xx or 5xx is received.
        """
        logger.debug("Starting GET request to URL: %s", url)

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            logger.debug("Request to %s successful. Status: %d", url, response.status_code)
            return response.json()
        except HTTPError as e:
            logger.error("HTTP Error when requesting %s: %s", url, e)
            raise e
        except RequestException as e:
            logger.error("Network/Request Error when requesting %s: %s", url, e)
            raise e


class JsonPlaceholderClient(BaseApiClient, AbstractUserApiClient):
    """Client for fetching user data from JsonPlaceholder API."""

    BASE_URL = settings.JSON_PLACEHOLDER_URL

    def get_users(self) -> list[dict[str, Any]]:
        """
        Fetches the complete list of users. Returns an empty list on API/network failure.
        """
        endpoint = f"{self.BASE_URL}/users"

        try:
            data = self._get(endpoint)
            return data
        except RequestException:
            logger.warning(
                "Failed to fetch user data from JsonPlaceholder due to API error. Returning empty list."
            )
            return []


class FakerApiClient(BaseApiClient, AbstractCreditCardApiClient):
    """Client for fetching random credit card data from FakerAPI."""

    BASE_URL = settings.FAKERAPI_URL

    def get_credit_cards(self, quantity: int) -> list[dict[str, Any]]:
        """
        Fetches data for a specified quantity of random credit cards.
        """
        if quantity <= 0:
            return []

        endpoint = f"{self.BASE_URL}/creditCards?_quantity={quantity}"

        try:
            data = self._get(endpoint)

            if not isinstance(data, dict) or not data.get("data"):
                logger.error("FakerAPI returned unexpected data structure: %s", data)
                return []

            return data["data"]
        except RequestException:
            logger.warning(
                "Failed to fetch credit card data from FakerAPI due to API error. Returning empty list."
            )
            return []
