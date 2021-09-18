from logging import Logger, getLogger

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

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

    @command(name="jira", aliases=["bug"])
    async def cmd_jira(self, ctx: Context, issue_id: str):
        # Extract the issue ID if the command was given a URL. Issue IDs given
        # directly are not affected
        issue_id = issue_id.split("?")[0].split("/")[-1].upper()

        # Try to get the issue
        issue: JiraIssue = await self.jira_client.get_issue(issue_id)

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

        await ctx.send(embed=issue_embed)
