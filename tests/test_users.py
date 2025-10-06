from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from users.infrastructure.repository import UsersRepository
from users.models import Address, Base, Company, CreditCard, User
from users.service import UsersService
from users.tasks import sync_users_task


@pytest.fixture
def db_session():
    """Creates an in-memory SQLite database for each test and manages the session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_clients_data():
    """
    Provides test data and configured MagicMocks for external API clients.
    The FakerClient is mocked for batch requests (returns a list of cards).
    """
    mock_user_data = {
        "id": 101,
        "name": "Test User",
        "username": "tester",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "website": "test.org",
        "address": {
            "street": "Test Street",
            "suite": "Apt. 100",
            "city": "Testville",
            "zipcode": "12345",
            "geo": {"lat": "1.0", "lng": "2.0"},
        },
        "company": {"name": "Test Company", "catchPhrase": "Test Phrase", "bs": "Test BS"},
    }

    mock_credit_card = {
        "type": "Visa",
        "number": "1111222233334444",
        "expiration": "12/25",
        "owner": "Test Owner",
    }

    mock_placeholder_client = MagicMock()
    mock_placeholder_client.get_users.return_value = [mock_user_data]

    mock_faker_client = MagicMock()
    mock_faker_client.get_credit_cards.return_value = [mock_credit_card]

    return mock_placeholder_client, mock_faker_client, mock_user_data, mock_credit_card


def test_sync_users_success(db_session, mock_clients_data):
    """
    Tests the successful creation of a new user, including calling the batch
    method for credit card retrieval with the correct quantity.
    """

    user_client, card_client, _, _ = mock_clients_data
    repo = UsersRepository(db=db_session)
    service = UsersService(repo, user_client, card_client)

    created_users = service.sync_users()

    assert len(created_users) == 1
    user_client.get_users.assert_called_once()
    card_client.get_credit_cards.assert_called_once_with(1)

    db_user = db_session.get(User, 101)

    assert db_user is not None
    assert db_user.name == "Test User"
    assert db_user.address.city == "Testville"
    assert db_user.company.name == "Test Company"
    assert db_user.credit_card.type == "Visa"


def test_sync_users_skip_existing(db_session, mock_clients_data):
    """
    Verifies that the service correctly skips a user already existing in the DB
    and does not make an external API call for credit cards.
    """

    user_client, card_client, mock_user_data, _ = mock_clients_data
    repo = UsersRepository(db=db_session)
    service = UsersService(repo, user_client, card_client)

    address = Address(street="a", suite="s", city="c", zipcode="z", geo_lat="1", geo_lng="1")
    company = Company(name="n", catch_phrase="c", bs="b")
    card = CreditCard(type="t", number="n", expiration="e", owner="o")
    db_session.add_all([address, company, card])
    db_session.flush()

    existing_user = User(
        id=mock_user_data["id"],
        name="Existing User",
        username="exist",
        email="e@e.com",
        phone="p",
        website="w",
        address_id=address.id,
        company_id=company.id,
        credit_card_id=card.id,
    )
    db_session.add(existing_user)
    db_session.commit()

    created_users = service.sync_users()

    assert len(created_users) == 0

    card_client.get_credit_cards.assert_not_called()

    updated_user = db_session.get(User, mock_user_data["id"])
    assert updated_user.name == "Existing User"


def test_sync_users_insufficient_cards(db_session, mock_clients_data):
    """
    Tests a scenario where the external card API returns less data than requested
    by the service, which should result in an exception and transaction rollback.
    """

    user_client, card_client, _, _ = mock_clients_data
    repo = UsersRepository(db=db_session)
    service = UsersService(repo, user_client, card_client)

    user_data_2 = {**mock_clients_data[2], "id": 102, "username": "t2"}
    user_data_3 = {**mock_clients_data[2], "id": 103, "username": "t3"}
    user_client.get_users.return_value = [mock_clients_data[2], user_data_2, user_data_3]

    with pytest.raises(Exception, match="Insufficient credit card data received"):
        service.sync_users()

    card_client.get_credit_cards.assert_called_once_with(3)
    assert db_session.query(User).count() == 0


@patch("users.tasks.session_factory")
@patch("users.tasks.UsersService")
def test_sync_users_task_success(MockUsersService, MockSessionFactory):
    """
    Verifies the successful execution of the Celery task, including the call to sync_users
    and the transaction commit (session.commit).
    """

    mock_session = MagicMock()
    MockSessionFactory.return_value.__enter__.return_value = mock_session
    MockUsersService.return_value.sync_users.return_value = [MagicMock()] * 5

    sync_users_task.run()

    MockUsersService.assert_called_once()
    MockUsersService.return_value.sync_users.assert_called_once()
    mock_session.commit.assert_called_once()
    assert "Total new users processed: 5" in sync_users_task.run()
