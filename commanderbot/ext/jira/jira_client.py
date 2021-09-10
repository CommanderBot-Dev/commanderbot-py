from datetime import datetime
from typing import Optional

import aiohttp

from commanderbot.ext.jira.jira_issue import JiraIssue, StatusColor


class JiraClient:
    def __init__(self, url: str):
        self.url = url

    @staticmethod
    async def _request_data(url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def get_issue(self, issue_id: str) -> Optional[JiraIssue]:
        try:
            data: dict = await self._request_data(
                f"{self.url}/rest/api/latest/issue/{issue_id}"
            )
        except KeyError:
            return None
            
        # Extract fields into their own dictionary
        if "fields" not in data.keys():
            return None

        fields: dict = data["fields"]

        assignee: str = "Unassigned"
        if user := fields.get("assignee"):
            assignee = user["displayName"]

        resolution: str = "Unresolved"
        if res := fields.get("resolution"):
            resolution = res["name"]

        since_version: str = "None"
        if ver := fields.get("versions"):
            since_version = ver[0]["name"]

        fix_version: str = "None"
        if ver := fields.get("fixVersions"):
            fix_version = ver[-1]["name"]

        return JiraIssue(
            url=f"{self.url}/browse/{issue_id}",
            icon_url=f"{self.url}/favicon.png",
            issue_id=issue_id,

            summary=fields["summary"],
            created_on=datetime.strptime(fields["created"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            status=fields["status"]["name"],
            status_color=StatusColor.from_str(
                fields["status"]["statusCategory"]["colorName"]
            ),
            votes=fields["votes"]["votes"],

            assignee=assignee,
            resolution=resolution,
            since_version=since_version,
            fix_version=fix_version,
        )
