from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class User(Base):
    """
    Represents a user in the system.

    Stores personal and contact information about a user, along with
    relationships to their address, company, and (optionally) credit card.

    Table: users

    Attributes:
        id (int): Unique identifier for the user (primary key).
        name (str): Full name of the user.
        username (str): Unique username.
        email (str): User's email address.
        phone (str): User's phone number.
        website (str): User's personal or company website.
        address_id (int): Foreign key referencing the `addresses` table.
        company_id (int): Foreign key referencing the `companies` table.
        credit_card_id (int | None): Optional foreign key referencing `credit_cards`.
        address (Address): Related Address object.
        company (Company): Related Company object.
        credit_card (CreditCard | None): Related CreditCard object if assigned.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    username: Mapped[str]
    email: Mapped[str]
    phone: Mapped[str]
    website: Mapped[str]

    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    credit_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("credit_cards.id"), unique=True, nullable=True
    )

    address: Mapped["Address"] = relationship(back_populates="users")
    company: Mapped["Company"] = relationship(back_populates="users")
    credit_card: Mapped["CreditCard"] = relationship(back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return (
            f"User(id={self.id}, name='{self.name}', username='{self.username}', "
            f"email='{self.email}', phone='{self.phone}', website='{self.website}', "
            f"address_id={self.address_id}, company_id={self.company_id}, credit_card_id={self.credit_card_id})"
        )


class Address(Base):
    """
    Represents a postal address.

    Stores detailed address and geolocation data. One address can be associated
    with multiple users.

    Table: addresses

    Attributes:
        id (int): Unique identifier (primary key).
        street (str): Street name.
        suite (str): Apartment or suite number.
        city (str): City name.
        zipcode (str): Postal code.
        geo_lat (str): Latitude coordinate.
        geo_lng (str): Longitude coordinate.
        users (list[User]): List of users linked to this address.
    """

    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    street: Mapped[str]
    suite: Mapped[str]
    city: Mapped[str]
    zipcode: Mapped[str]
    geo_lat: Mapped[str]
    geo_lng: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="address")

    def __repr__(self) -> str:
        return (
            f"Address(id={self.id}, street='{self.street}', suite='{self.suite}', city='{self.city}', "
            f"zipcode='{self.zipcode}', geo_lat='{self.geo_lat}', geo_lng='{self.geo_lng}')"
        )


class Company(Base):
    """
    Represents a company entity.

    Contains information about a user's employer, including name,
    marketing slogan, and business specialization.

    Table: companies

    Attributes:
        id (int): Unique identifier (primary key).
        name (str): Company name.
        catch_phrase (str): Company motto or slogan.
        bs (str): Business statement or description.
        users (list[User]): Users associated with this company.
    """

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    catch_phrase: Mapped[str]
    bs: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="company")

    def __repr__(self) -> str:
        return f"Company(id={self.id}, name='{self.name}', catch_phrase='{self.catch_phrase}', bs='{self.bs}')"


class CreditCard(Base):
    """
    Represents a user's credit card.

    Each credit card belongs to a single user.

    Table: credit_cards

    Attributes:
        id (int): Unique identifier (primary key).
        type (str): Type of card (e.g., Visa, MasterCard).
        number (str): Credit card number.
        expiration (str): Expiration date (MM/YY format).
        owner (str): Name of the cardholder.
        user (User): Linked user (one-to-one relationship).
    """

    __tablename__ = "credit_cards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str]
    number: Mapped[str]
    expiration: Mapped[str]
    owner: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="credit_card", uselist=False)

    def __repr__(self) -> str:
        return f"CreditCard(id={self.id}, type='{self.type}', number='{self.number}', expiration='{self.expiration}', owner='{self.owner}')"
