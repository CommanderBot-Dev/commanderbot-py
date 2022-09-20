from logging import Logger, getLogger

from discord import Interaction, ui, Embed
from discord.app_commands import command
from discord.ext.commands import Bot, Cog

from commanderbot.ext.jira.jira_client import JiraClient
from commanderbot.ext.jira.jira_issue import JiraIssue


class JiraCog(Cog, name="commanderbot.ext.jira"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.log: Logger = getLogger(self.qualified_name)

        # Get the URL from the config
        url = options.get("url", "")
        if not url:
            # Log an error if the URL doesn't exist
            self.log.error("No Jira URL was given in the bot config")

        # Create the Jira client
        self.jira_client: JiraClient = JiraClient(url)

    @command(name="jira", description="Query a Jira issue")
    async def cmd_jira(self, interaction: Interaction, issue_or_url: str):
        # Try to get the issue
        issue: JiraIssue = await self.jira_client.get_issue(issue_or_url)

        # Create embed title and limit it to 256 characters
        title: str = f"[{issue.issue_id}] {issue.summary}"
        if len(title) > 256:
            title = f"{title[:253]}..."

        # Create issue embed
        issue_embed: Embed = Embed(
            title=title,
            url=issue.url,
            color=issue.status_color.value,
        )

        issue_embed.set_thumbnail(url=issue.icon_url)

        for k, v in issue.fields.items():
            issue_embed.add_field(name=k, value=v)

        # Create view with link button
        view: ui.View = ui.View()
        view.add_item(ui.Button(label="View on Jira", url=issue.url))

        await interaction.response.send_message(embed=issue_embed, view=view)
