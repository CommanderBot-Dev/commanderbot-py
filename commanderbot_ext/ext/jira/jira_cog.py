import discord
import aiohttp
from discord.ext.commands import Bot, Cog, command


class JiraCog(Cog, name="commanderbot_ext.ext.jira"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        self.resolution_table = {
            "https://bugs.mojang.com/rest/api/2/resolution/1": "Fixed",
            "https://bugs.mojang.com/rest/api/2/resolution/2": "Won't Fix",
            "https://bugs.mojang.com/rest/api/2/resolution/3": "Duplicate",
            "https://bugs.mojang.com/rest/api/2/resolution/4": "Incomplete",
            "https://bugs.mojang.com/rest/api/2/resolution/5": "Cannot Reproduce",
            "https://bugs.mojang.com/rest/api/2/resolution/6": "Works as Intended",
            "https://bugs.mojang.com/rest/api/2/resolution/7": "Invalid",
            "https://bugs.mojang.com/rest/api/2/resolution/10001": "Awaiting Response",
            "https://bugs.mojang.com/rest/api/2/resolution/10003": "Done",
        }

        self.status_table = {
            "https://bugs.mojang.com/rest/api/2/status/1": "Open",
            "https://bugs.mojang.com/rest/api/2/status/3": "In Progress",
            "https://bugs.mojang.com/rest/api/2/status/4": "Reopened",
            "https://bugs.mojang.com/rest/api/2/status/5": "Resolved",
            "https://bugs.mojang.com/rest/api/2/status/6": "Closed",
            "https://bugs.mojang.com/rest/api/2/status/10200": "Postponed",
        }

    # TODO think about keeping a global `session` object for the cog
    async def _request_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    # TODO remove hardcoded status and resolve values and add config for JIRA URL and bug ID format
    @command(name="jira", aliases=["bug"])
    async def cmd_jira(self, ctx: discord.Message, bug_id: str):
        # Assume the parameter is a URL, so get the ID from it
        if "/" in bug_id:
            bug_id = bug_id.split("/")[-1]

        try:
            data = await self._request_data(
                f"https://bugs.mojang.com/rest/api/latest/issue/{bug_id}"
            )
            report_data = data["fields"]

        # Bug report doesn't exist
        except KeyError:
            await ctx.send(
                f"**{bug_id.upper()}** is not accessible."
                " This may be due to it being private or it may not exist."
            )
            return

        title = f"[{bug_id.upper()}] {report_data['summary']}"
        if report_data["assignee"] is None:
            assignee = "Unassigned"
        else:
            assignee = report_data["assignee"]["name"]
        reporter = report_data["reporter"]["displayName"]
        creation_date = report_data["created"][:10]
        since_version = report_data["versions"][0]["name"]

        jira_embed = discord.Embed(
            title=title, url=f"https://bugs.mojang.com/browse/{bug_id}", color=0x00ACED
        )
        jira_embed.add_field(name="Reporter", value=reporter, inline=True)
        jira_embed.add_field(name="Assignee", value=assignee, inline=True)
        jira_embed.add_field(name="Created On", value=creation_date, inline=True)
        jira_embed.add_field(name="Since Version", value=since_version, inline=True)

        # The bug report is still open
        if report_data["resolution"] is None:
            status = self.status_table[report_data["status"]["self"]]
            votes = report_data["votes"]["votes"]

            """
            if not report_data["customfield_10500"]:
                confirmation = "Unconfirmed"
            confirmation = report_data["customfield_10500"]["value"]
            """

            jira_embed.add_field(name="Status", value=status, inline=True)
            jira_embed.add_field(name="Votes", value=votes, inline=True)
            # jira_embed.add_field(name="Confirmation", value=confirmation, inline=True)

        # The bug report is closed
        else:
            resolution_status = self.resolution_table[report_data["resolution"]["self"]]
            resolve_date = report_data["resolutiondate"][:10]
            if not report_data["fixVersions"]:
                fix_version = "None"
            else:
                fix_version = report_data["fixVersions"][0]["name"]

            jira_embed.add_field(
                name="Resolution", value=resolution_status, inline=True
            )
            jira_embed.add_field(name="Resolved On", value=resolve_date, inline=True)
            jira_embed.add_field(name="Fix Version", value=fix_version, inline=True)

        jira_embed.set_footer(
            text=str(ctx.message.author), icon_url=str(ctx.message.author.avatar_url)
        )
        await ctx.send(embed=jira_embed)
