import logging

from users.interfaces import (
    AbstractCreditCardApiClient,
    AbstractUserApiClient,
    AbstractUsersRepository,
)

logger = logging.getLogger(__name__)


class UsersService:
    """
    Service layer responsible for the main business logic of synchronizing user data
    from external APIs to the database.
    """

    def __init__(
        self,
        repo: AbstractUsersRepository,
        user_client: AbstractUserApiClient,
        credit_card_client: AbstractCreditCardApiClient,
    ):
        self.repo = repo
        self.user_client = user_client
        self.credit_card_client = credit_card_client

    def sync_users(self) -> list:
        """
        Performs the periodic synchronization task. Uses a batch request for credit card data
        to minimize API calls and latency.

        1. Fetches all users from the primary API.
        2. Filters the list to include only new users.
        3. Executes a single batch request to get credit card data for all new users.
        4. Iterates through the new users, creating records using the batched data.

        :raises Exception: Raises an exception on critical failure (API error, insufficient data) to trigger Celery rollback/retry.
        :return: A list of newly created User model instances.
        """
        logger.info("Starting user data synchronization process.")

        users_data = self.user_client.get_users()
        created_users = []

        if not users_data:
            logger.warning(
                "Failed to retrieve user data from the primary API. Synchronization aborted."
            )
            return []

        new_users_data = []
        for d in users_data:
            if not self.repo.get_user_by_id(d.get("id")):
                new_users_data.append(d)

        num_new_users = len(new_users_data)
        if num_new_users == 0:
            logger.info("No new users found in the external source to process.")
            return []

        logger.info(
            "Identified %d new users. Starting batch request for credit card data.", num_new_users
        )

        all_credit_cards = self.credit_card_client.get_credit_cards(num_new_users)

        if len(all_credit_cards) < num_new_users:
            logger.error(
                "Received only %d credit cards, but need %d. Aborting sync for data consistency.",
                len(all_credit_cards),
                num_new_users,
            )
            raise Exception(
                "Insufficient credit card data received from external API batch request."
            )

        card_iterator = iter(all_credit_cards)

        try:
            for d in new_users_data:
                user_id = d.get("id")

                faker_card_data = next(card_iterator)

                logger.debug("Processing new user ID: %s", user_id)

                address = self.repo.create_address(d["address"])
                company = self.repo.create_company(d["company"])
                credit_card = self.repo.create_credit_card(faker_card_data)

                self.repo.flush_changes()

                user = self.repo.create_user(
                    user_data=d,
                    address_id=address.id,
                    company_id=company.id,
                    credit_card_id=credit_card.id,
                )
                created_users.append(user)
                logger.debug("User ID %s created successfully.", user.id)

            logger.info(
                "Synchronization finished. Successfully processed %d new users.", len(created_users)
            )
        except Exception as e:
            logger.error(
                "Synchronization error occurred during database operations. Details: %s",
                e,
                exc_info=True,
            )
            raise

        return created_users

    def get_all_users_data(self) -> list[dict]:
        """
        Retrieves all users from the repository and converts them into a list of dictionaries
        suitable for display or serialisation.

        :return: A list of dictionaries containing user and related entity data.
        """
        logger.info("Retrieving all users from the database.")
        users = self.repo.get_all_users()

        results = []
        for user in users:
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "address": user.address.__repr__(),
                "company": user.company.__repr__(),
                "credit_card": user.credit_card.__repr__() if user.credit_card else "N/A",
            }
            results.append(user_data)

        return results
