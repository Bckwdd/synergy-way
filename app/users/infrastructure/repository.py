from typing import Any

from sqlalchemy.orm import Session

from users.interfaces import AbstractUsersRepository
from users.models import Address, Company, CreditCard, User


class UsersRepository(AbstractUsersRepository):
    """
    Concrete implementation of the AbstractUsersRepository using SQLAlchemy.
    Manages persistence logic for User, Address, Company, and CreditCard models.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_address(self, data: dict[str, Any]) -> Address:
        """
        Creates an Address instance from API data and adds it to the session.
        The changes must be flushed or committed to persist the record and get its ID.
        :param data: Dictionary containing address details.
        :return: The created Address model instance.
        """
        address = Address(
            street=data["street"],
            suite=data["suite"],
            city=data["city"],
            zipcode=data["zipcode"],
            geo_lat=data["geo"]["lat"],
            geo_lng=data["geo"]["lng"],
        )
        self.db.add(address)
        return address

    def create_company(self, data: dict[str, Any]) -> Company:
        """
        Creates a Company instance from API data and adds it to the session.
        :param data: Dictionary containing company details.
        :return: The created Company model instance.
        """
        company = Company(
            name=data["name"],
            catch_phrase=data["catchPhrase"],
            bs=data["bs"],
        )
        self.db.add(company)
        return company

    def create_credit_card(self, data: dict[str, Any]) -> CreditCard:
        """
        Creates a CreditCard instance from API data and adds it to the session.
        :param data: Dictionary containing credit card details.
        :return: The created CreditCard model instance.
        """
        credit_card = CreditCard(
            type=data["type"],
            number=data["number"],
            expiration=data["expiration"],
            owner=data["owner"],
        )
        self.db.add(credit_card)
        return credit_card

    def create_user(
        self,
        user_data: dict[str, Any],
        address_id: int,
        company_id: int,
        credit_card_id: int,
    ) -> User:
        """
        Creates a User instance, linking it to previously created Address, Company, and CreditCard records.
        :param user_data: Dictionary containing core user details (name, email, etc.).
        :param address_id: Foreign key ID for the associated Address.
        :param company_id: Foreign key ID for the associated Company.
        :param credit_card_id: Foreign key ID for the associated CreditCard.
        :return: The created User model instance.
        """
        user_data.pop("address", None)
        user_data.pop("company", None)
        user_data.pop("credit_card", None)

        user = User(
            **user_data,
            address_id=address_id,
            company_id=company_id,
            credit_card_id=credit_card_id,
        )
        self.db.add(user)

        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieves a user by their primary key (which matches the external API ID).
        Used to check if a user already exists in the database.
        :param user_id: The ID of the user to find.
        :return: User instance if found, otherwise None.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all_users(self) -> list[User]:
        """
        Retrieves all user records from the database.

        :return: A list of all User model instances.
        """
        return self.db.query(User).all()

    def flush_changes(self) -> None:
        """
        Forces a database write (flush) to obtain primary key IDs for newly created objects
        before they are linked to the User object.
        """
        self.db.flush()
