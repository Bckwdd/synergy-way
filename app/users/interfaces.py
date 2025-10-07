from abc import ABC, abstractmethod
from typing import Any

from users.models import Address, Company, CreditCard, User


class AbstractUsersRepository(ABC):
    """
    Abstract interface for working with the user storage.
    Isolates the business logic from the database implementation details.
    """

    @abstractmethod
    def create_address(self, data: dict[str, Any]) -> Address:
        """Creates and adds an Address to the session."""
        pass

    @abstractmethod
    def create_company(self, data: dict[str, Any]) -> Company:
        """Creates and adds a Company to the session."""
        pass

    @abstractmethod
    def create_credit_card(self, data: dict[str, Any]) -> CreditCard:
        """Creates and adds a CreditCard to the session."""
        pass

    @abstractmethod
    def create_user(
        self,
        user_data: dict[str, Any],
        address_id: int,
        company_id: int,
        credit_card_id: int,
    ) -> User:
        """Creates and adds a User to the session."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by ID."""
        pass

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """Retrieves all users."""
        pass

    @abstractmethod
    def flush_changes(self) -> None:
        """Forces writing changes to the database to obtain the ID."""
        pass


class AbstractUserApiClient(ABC):
    """
    Abstract interface for retrieving user data.
    """

    @abstractmethod
    def get_users(self) -> list[dict[str, Any]]:
        """Retrieves a list of user data."""
        pass


class AbstractCreditCardApiClient(ABC):
    """
    Abstract interface for retrieving credit card data.
    """

    @abstractmethod
    def get_credit_cards(self, quantity: int) -> list[dict[str, Any]]:
        """
        Retrieves data for a specified quantity of credit cards.
        :param quantity: The number of cards to retrieve.
        :return: A list of dictionaries, one for each card.
        """
        pass
