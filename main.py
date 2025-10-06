from core.database import session_factory
from core.logger_config import setup_logging
from users.infrastructure.api_client import FakerApiClient, JsonPlaceholderClient
from users.infrastructure.repository import UsersRepository
from users.service import UsersService

logger = setup_logging()


def display_users():
    """
    Initializes the necessary components to connect to the DB and display all saved users.
    """
    user_client = JsonPlaceholderClient()
    credit_card_client = FakerApiClient()

    try:
        with session_factory() as session:
            repository = UsersRepository(db=session)

            service = UsersService(
                repo=repository, user_client=user_client, credit_card_client=credit_card_client
            )

            user_list = service.get_all_users_data()

            if not user_list:
                logger.info("No user data found in the database.")
                return

            print("\n--- SAVED USERS ---")
            for user in user_list:
                print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
                print(f"  Address: {user['address']}")
                print(f"  Company: {user['company']}")
                print(f"  Card: {user['credit_card']}")
                print("-" * 20)

    except Exception as e:
        logger.error("Failed to display users due to database error: %s", e, exc_info=True)


def main():
    """
    Main entry point for the application.
    """
    display_users()


if __name__ == "__main__":
    main()
