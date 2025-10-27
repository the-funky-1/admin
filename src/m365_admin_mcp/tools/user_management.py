"""
User management tools for creating and configuring M365 users.
"""

import logging
from typing import Any

from msgraph.generated.models.user import User
from msgraph.generated.models.password_profile import PasswordProfile

from ..auth import get_graph_client
from ..utils.validation import validate_email

logger = logging.getLogger(__name__)


class UserManagementTools:
    """Tools for M365 user account management."""

    @staticmethod
    async def create_user(
        email: str,
        display_name: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        force_password_change: bool = True,
    ) -> dict[str, Any]:
        """
        Create a new Microsoft 365 user account.

        Args:
            email: User principal name (email address)
            display_name: Display name for the user
            password: Initial password
            first_name: First name (optional)
            last_name: Last name (optional)
            force_password_change: Require password change on first login

        Returns:
            Dictionary with user creation result

        Raises:
            ValueError: If email is invalid
            Exception: If user creation fails
        """
        # Validate email
        if not validate_email(email):
            raise ValueError(f"Invalid email format: {email}")

        logger.info(f"Creating user: {email}")

        try:
            client = get_graph_client()

            # Create password profile
            password_profile = PasswordProfile()
            password_profile.password = password
            password_profile.force_change_password_next_sign_in = force_password_change

            # Create user object
            user = User()
            user.user_principal_name = email
            user.display_name = display_name
            user.mail_nickname = email.split("@")[0]  # Use email prefix as nickname
            user.account_enabled = True
            user.password_profile = password_profile

            # Set names if provided
            if first_name:
                user.given_name = first_name
            if last_name:
                user.surname = last_name

            # Create user via Graph API
            created_user = await client.users.post(user)

            logger.info(f"Successfully created user: {created_user.user_principal_name}")

            return {
                "success": True,
                "userId": created_user.id,
                "userPrincipalName": created_user.user_principal_name,
                "displayName": created_user.display_name,
                "message": f"User {created_user.user_principal_name} created successfully",
            }

        except Exception as e:
            logger.error(f"Failed to create user {email}: {e}", exc_info=True)
            raise Exception(f"User creation failed: {str(e)}")

    @staticmethod
    async def get_user(user_email: str) -> dict[str, Any]:
        """
        Get user information by email.

        Args:
            user_email: User principal name (email)

        Returns:
            Dictionary with user information

        Raises:
            ValueError: If email is invalid
            Exception: If user not found or fetch fails
        """
        if not validate_email(user_email):
            raise ValueError(f"Invalid email format: {user_email}")

        logger.info(f"Fetching user: {user_email}")

        try:
            client = get_graph_client()
            user = await client.users.by_user_id(user_email).get()

            if not user:
                raise Exception(f"User not found: {user_email}")

            return {
                "success": True,
                "userId": user.id,
                "userPrincipalName": user.user_principal_name,
                "displayName": user.display_name,
                "givenName": user.given_name,
                "surname": user.surname,
                "accountEnabled": user.account_enabled,
                "mail": user.mail,
            }

        except Exception as e:
            logger.error(f"Failed to fetch user {user_email}: {e}", exc_info=True)
            raise Exception(f"User fetch failed: {str(e)}")

    @staticmethod
    async def list_users(max_results: int = 100) -> dict[str, Any]:
        """
        List all users in the tenant.

        Args:
            max_results: Maximum number of users to return

        Returns:
            Dictionary with list of users

        Raises:
            Exception: If list operation fails
        """
        logger.info(f"Listing users (max: {max_results})")

        try:
            client = get_graph_client()
            users_result = await client.users.get()

            if not users_result or not users_result.value:
                return {
                    "success": True,
                    "users": [],
                    "count": 0,
                    "message": "No users found",
                }

            # Convert to simple dict format
            users_list = []
            for user in users_result.value[:max_results]:
                users_list.append({
                    "id": user.id,
                    "userPrincipalName": user.user_principal_name,
                    "displayName": user.display_name,
                    "mail": user.mail,
                    "accountEnabled": user.account_enabled,
                })

            return {
                "success": True,
                "users": users_list,
                "count": len(users_list),
                "message": f"Found {len(users_list)} users",
            }

        except Exception as e:
            logger.error(f"Failed to list users: {e}", exc_info=True)
            raise Exception(f"User list failed: {str(e)}")
