from typing import Optional

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot.ext.jira.jira_client import JiraClient
from commanderbot.ext.jira.jira_issue import JiraIssue


class JiraCog(Cog, name="commanderbot.ext.jira"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.jira_client: JiraClient = JiraClient(options.get("url", "bugs.mojang.com"))

    @command(name="jira", aliases=["bug"])
    async def cmd_jira(self, ctx: Context, issue_id: str):
        # Make uppercase so the project ID is valid
        issue_id = issue_id.upper()

        # Get issue or print an error if it couldn't be requested
        issue: Optional[JiraIssue] = await self.jira_client.get_issue(issue_id)
        if not issue:
            await ctx.send(
                f"**{issue_id}** is not accessible."
                " This may be due to it being private or it may not exist."
            )
            return

        # Create issue embed
        issue_embed: Embed = Embed(
            title=f"{issue.summary}",
            url=issue.url,
            color=issue.status_color.value,
        )

        issue_embed.set_author(name=issue.issue_id, url=issue.url, icon_url=issue.icon_url)

        for k, v in issue.fields.items():
            issue_embed.add_field(name=k, value=v)

        await ctx.send(embed=issue_embed)
