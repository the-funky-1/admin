"""
Microsoft Teams provisioning tools.

Provides functionality for:
- Team creation with configuration
- Channel management (create, update, delete)
- Member and owner assignment
- Team settings configuration
- Multi-service orchestration with rollback
"""

import logging
from enum import Enum
from typing import Any

from msgraph.generated.models.aad_user_conversation_member import (
    AadUserConversationMember,
)
from msgraph.generated.models.channel import Channel
from msgraph.generated.models.channel_membership_type import ChannelMembershipType
from msgraph.generated.models.team import Team
from msgraph.generated.models.team_fun_settings import TeamFunSettings
from msgraph.generated.models.team_guest_settings import TeamGuestSettings
from msgraph.generated.models.team_member_settings import TeamMemberSettings
from msgraph.generated.models.team_messaging_settings import TeamMessagingSettings
from msgraph.generated.models.team_visibility_type import TeamVisibilityType

from ..auth import get_graph_client
from ..utils.validation import validate_email

logger = logging.getLogger(__name__)


class TeamVisibility(str, Enum):
    """Team visibility options."""

    PUBLIC = "public"
    PRIVATE = "private"


class ChannelType(str, Enum):
    """Channel type options."""

    STANDARD = "standard"
    PRIVATE = "private"


class MemberRole(str, Enum):
    """Team member role options."""

    OWNER = "owner"
    MEMBER = "member"


class RollbackAction:
    """Represents a rollback action for orchestration."""

    def __init__(self, description: str, action_func, *args, **kwargs):
        """Initialize rollback action."""
        self.description = description
        self.action_func = action_func
        self.args = args
        self.kwargs = kwargs

    async def execute(self) -> None:
        """Execute the rollback action."""
        logger.info(f"Executing rollback: {self.description}")
        await self.action_func(*self.args, **self.kwargs)


class OrchestrationContext:
    """Context manager for multi-service orchestration with rollback."""

    def __init__(self):
        """Initialize orchestration context."""
        self.rollback_stack: list[RollbackAction] = []
        self.success = False

    def add_rollback(self, description: str, action_func, *args, **kwargs) -> None:
        """Add a rollback action to the stack."""
        self.rollback_stack.append(RollbackAction(description, action_func, *args, **kwargs))

    async def __aenter__(self):
        """Enter orchestration context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit orchestration context and execute rollback if needed."""
        if exc_type is not None and not self.success:
            logger.warning(f"Orchestration failed, executing rollback: {exc_val}")
            await self.rollback()
            return False
        return False

    async def rollback(self) -> None:
        """Execute all rollback actions in reverse order."""
        logger.info(f"Executing {len(self.rollback_stack)} rollback action(s)")

        for action in reversed(self.rollback_stack):
            try:
                await action.execute()
            except Exception as e:
                logger.error(f"Rollback action failed: {action.description} - {e}")

    def mark_success(self) -> None:
        """Mark orchestration as successful (prevents rollback)."""
        self.success = True


class TeamsProvisioningTools:
    """Microsoft Teams provisioning and management tools."""

    @staticmethod
    async def create_team(
        display_name: str,
        description: str,
        visibility: str = "private",
        owner_email: str | None = None,
        allow_guest_create_channels: bool = False,
        allow_guest_delete_channels: bool = False,
        allow_create_update_channels: bool = True,
        allow_delete_channels: bool = True,
        allow_add_remove_apps: bool = True,
        allow_create_update_remove_tabs: bool = True,
        allow_create_update_remove_connectors: bool = True,
        allow_user_edit_messages: bool = True,
        allow_user_delete_messages: bool = True,
        allow_team_mentions: bool = True,
        allow_channel_mentions: bool = True,
        allow_giphy: bool = True,
        giphy_content_rating: str = "moderate",
    ) -> dict[str, Any]:
        """Create a new Microsoft Team with configuration."""
        logger.info(f"Creating team: {display_name}")

        # Validate visibility
        if visibility.lower() not in ["public", "private"]:
            raise ValueError(f"Invalid visibility: {visibility}. Must be 'public' or 'private'")

        # Validate owner email if provided
        if owner_email and not validate_email(owner_email):
            raise ValueError(f"Invalid owner email: {owner_email}")

        client = get_graph_client()

        # Create team object
        team = Team()
        team.display_name = display_name
        team.description = description

        # Set visibility
        if visibility.lower() == "public":
            team.visibility = TeamVisibilityType.Public
        else:
            team.visibility = TeamVisibilityType.Private

        # Configure member settings
        member_settings = TeamMemberSettings()
        member_settings.allow_create_update_channels = allow_create_update_channels
        member_settings.allow_delete_channels = allow_delete_channels
        member_settings.allow_add_remove_apps = allow_add_remove_apps
        member_settings.allow_create_update_remove_tabs = allow_create_update_remove_tabs
        member_settings.allow_create_update_remove_connectors = (
            allow_create_update_remove_connectors
        )
        team.member_settings = member_settings

        # Configure messaging settings
        messaging_settings = TeamMessagingSettings()
        messaging_settings.allow_user_edit_messages = allow_user_edit_messages
        messaging_settings.allow_user_delete_messages = allow_user_delete_messages
        messaging_settings.allow_team_mentions = allow_team_mentions
        messaging_settings.allow_channel_mentions = allow_channel_mentions
        team.messaging_settings = messaging_settings

        # Configure fun settings
        fun_settings = TeamFunSettings()
        fun_settings.allow_giphy = allow_giphy
        fun_settings.giphy_content_rating = giphy_content_rating
        team.fun_settings = fun_settings

        # Configure guest settings
        guest_settings = TeamGuestSettings()
        guest_settings.allow_create_update_channels = allow_guest_create_channels
        guest_settings.allow_delete_channels = allow_guest_delete_channels
        team.guest_settings = guest_settings

        # Create the team
        created_team = await client.teams.post(team)

        logger.info(f"Team created: {created_team.id}")

        # Add owner if specified
        if owner_email:
            try:
                await TeamsProvisioningTools.add_team_member(
                    team_id=created_team.id,
                    user_email=owner_email,
                    role="owner",
                )
            except Exception as e:
                logger.warning(f"Failed to add owner {owner_email}: {e}")

        return {
            "success": True,
            "team_id": created_team.id,
            "display_name": created_team.display_name,
            "web_url": created_team.web_url,
            "message": f"Team '{display_name}' created successfully",
        }

    @staticmethod
    async def get_team(team_id: str) -> dict[str, Any]:
        """Get team information."""
        logger.info(f"Retrieving team: {team_id}")

        client = get_graph_client()
        team = await client.teams.by_team_id(team_id).get()

        return {
            "team_id": team.id,
            "display_name": team.display_name,
            "description": team.description,
            "visibility": str(team.visibility),
            "web_url": team.web_url,
            "is_archived": team.is_archived,
        }

    @staticmethod
    async def list_teams(max_results: int = 100) -> dict[str, Any]:
        """List all teams in the organization."""
        logger.info(f"Listing teams (max: {max_results})")

        client = get_graph_client()

        # Get all groups first, then filter for teams
        groups = await client.groups.get(top=max_results)

        teams_list = []
        if groups and groups.value:
            for group in groups.value:
                # Check if group has a team
                try:
                    team = await client.teams.by_team_id(group.id).get()
                    if team:
                        teams_list.append(
                            {
                                "team_id": team.id,
                                "display_name": team.display_name,
                                "description": team.description,
                                "visibility": str(team.visibility),
                                "web_url": team.web_url,
                            }
                        )
                except Exception:
                    # Group doesn't have a team, skip
                    continue

        return {"count": len(teams_list), "teams": teams_list}

    @staticmethod
    async def delete_team(team_id: str) -> dict[str, Any]:
        """Delete a team (archives the group)."""
        logger.info(f"Deleting team: {team_id}")

        client = get_graph_client()

        # Archive the team instead of deleting (Microsoft best practice)
        team = Team()
        team.is_archived = True
        await client.teams.by_team_id(team_id).patch(team)

        logger.info(f"Team archived: {team_id}")

        return {
            "success": True,
            "team_id": team_id,
            "message": "Team archived successfully",
        }

    @staticmethod
    async def create_channel(
        team_id: str,
        display_name: str,
        description: str | None = None,
        channel_type: str = "standard",
    ) -> dict[str, Any]:
        """Create a channel in a team."""
        logger.info(f"Creating channel '{display_name}' in team {team_id}")

        # Validate channel type
        if channel_type.lower() not in ["standard", "private"]:
            raise ValueError(
                f"Invalid channel type: {channel_type}. Must be 'standard' or 'private'"
            )

        client = get_graph_client()

        channel = Channel()
        channel.display_name = display_name
        channel.description = description

        # Set channel membership type
        if channel_type.lower() == "private":
            channel.membership_type = ChannelMembershipType.Private
        else:
            channel.membership_type = ChannelMembershipType.Standard

        created_channel = await client.teams.by_team_id(team_id).channels.post(channel)

        logger.info(f"Channel created: {created_channel.id}")

        return {
            "success": True,
            "channel_id": created_channel.id,
            "display_name": created_channel.display_name,
            "web_url": created_channel.web_url,
            "message": f"Channel '{display_name}' created successfully",
        }

    @staticmethod
    async def list_channels(team_id: str) -> dict[str, Any]:
        """List all channels in a team."""
        logger.info(f"Listing channels for team: {team_id}")

        client = get_graph_client()
        channels = await client.teams.by_team_id(team_id).channels.get()

        channels_list = []
        if channels and channels.value:
            for channel in channels.value:
                channels_list.append(
                    {
                        "channel_id": channel.id,
                        "display_name": channel.display_name,
                        "description": channel.description,
                        "email": channel.email,
                        "web_url": channel.web_url,
                        "membership_type": str(channel.membership_type),
                    }
                )

        return {"count": len(channels_list), "channels": channels_list}

    @staticmethod
    async def delete_channel(team_id: str, channel_id: str) -> dict[str, Any]:
        """Delete a channel from a team."""
        logger.info(f"Deleting channel {channel_id} from team {team_id}")

        client = get_graph_client()
        await client.teams.by_team_id(team_id).channels.by_channel_id(channel_id).delete()

        logger.info(f"Channel deleted: {channel_id}")

        return {
            "success": True,
            "channel_id": channel_id,
            "message": "Channel deleted successfully",
        }

    @staticmethod
    async def add_team_member(
        team_id: str,
        user_email: str,
        role: str = "member",
    ) -> dict[str, Any]:
        """Add a member or owner to a team."""
        logger.info(f"Adding {role} {user_email} to team {team_id}")

        # Validate email
        if not validate_email(user_email):
            raise ValueError(f"Invalid email address: {user_email}")

        # Validate role
        if role.lower() not in ["owner", "member"]:
            raise ValueError(f"Invalid role: {role}. Must be 'owner' or 'member'")

        client = get_graph_client()

        # Get user by email
        users = await client.users.get(filter=f"userPrincipalName eq '{user_email}'")
        if not users or not users.value or len(users.value) == 0:
            raise ValueError(f"User not found: {user_email}")

        user = users.value[0]

        # Create conversation member
        conversation_member = AadUserConversationMember()
        conversation_member.odata_type = "#microsoft.graph.aadUserConversationMember"
        conversation_member.roles = ["owner"] if role.lower() == "owner" else []
        conversation_member.user_id = user.id

        # Add member to team
        added_member = await client.teams.by_team_id(team_id).members.post(conversation_member)

        logger.info(f"Member added: {user_email} as {role}")

        return {
            "success": True,
            "member_id": added_member.id,
            "user_email": user_email,
            "role": role,
            "message": f"Added {user_email} as {role}",
        }

    @staticmethod
    async def remove_team_member(team_id: str, member_id: str) -> dict[str, Any]:
        """Remove a member from a team."""
        logger.info(f"Removing member {member_id} from team {team_id}")

        client = get_graph_client()
        await client.teams.by_team_id(team_id).members.by_conversation_member_id(
            member_id
        ).delete()

        logger.info(f"Member removed: {member_id}")

        return {
            "success": True,
            "member_id": member_id,
            "message": "Member removed successfully",
        }

    @staticmethod
    async def list_team_members(team_id: str) -> dict[str, Any]:
        """List all members of a team."""
        logger.info(f"Listing members for team: {team_id}")

        client = get_graph_client()
        members = await client.teams.by_team_id(team_id).members.get()

        members_list = []
        if members and members.value:
            for member in members.value:
                # Type check for AadUserConversationMember
                if hasattr(member, "user_id") and hasattr(member, "roles"):
                    is_owner = member.roles and "owner" in member.roles
                    members_list.append(
                        {
                            "member_id": member.id,
                            "user_id": member.user_id,
                            "display_name": member.display_name,
                            "email": member.email,
                            "role": "owner" if is_owner else "member",
                        }
                    )

        return {"count": len(members_list), "members": members_list}

    @staticmethod
    async def provision_team_with_structure(
        team_name: str,
        team_description: str,
        owner_email: str,
        channels: list[dict[str, str]],
        members: list[dict[str, str]] | None = None,
        visibility: str = "private",
    ) -> dict[str, Any]:
        """
        Orchestrate full team provisioning with channels and members.

        Includes automatic rollback on failure.
        """
        logger.info(f"Provisioning team with structure: {team_name}")

        async with OrchestrationContext() as ctx:
            # Step 1: Create team
            team_result = await TeamsProvisioningTools.create_team(
                display_name=team_name,
                description=team_description,
                visibility=visibility,
                owner_email=owner_email,
            )
            team_id = team_result["team_id"]

            # Add rollback for team creation
            ctx.add_rollback(
                f"Delete team {team_name}",
                TeamsProvisioningTools.delete_team,
                team_id,
            )

            # Step 2: Create channels
            created_channels = []
            for channel_data in channels:
                channel_result = await TeamsProvisioningTools.create_channel(
                    team_id=team_id,
                    display_name=channel_data["name"],
                    description=channel_data.get("description"),
                    channel_type=channel_data.get("type", "standard"),
                )
                created_channels.append(channel_result)

                # Add rollback for each channel
                ctx.add_rollback(
                    f"Delete channel {channel_data['name']}",
                    TeamsProvisioningTools.delete_channel,
                    team_id,
                    channel_result["channel_id"],
                )

            # Step 3: Add members
            added_members = []
            if members:
                for member_data in members:
                    member_result = await TeamsProvisioningTools.add_team_member(
                        team_id=team_id,
                        user_email=member_data["email"],
                        role=member_data.get("role", "member"),
                    )
                    added_members.append(member_result)

                    # Add rollback for each member
                    ctx.add_rollback(
                        f"Remove member {member_data['email']}",
                        TeamsProvisioningTools.remove_team_member,
                        team_id,
                        member_result["member_id"],
                    )

            # Mark as successful (prevents rollback)
            ctx.mark_success()

            logger.info(f"Team provisioning completed: {team_id}")

            return {
                "success": True,
                "team_id": team_id,
                "team_name": team_name,
                "team_url": team_result["web_url"],
                "channels_created": len(created_channels),
                "members_added": len(added_members),
                "message": f"Team '{team_name}' provisioned with {len(created_channels)} channels and {len(added_members)} members",
            }
