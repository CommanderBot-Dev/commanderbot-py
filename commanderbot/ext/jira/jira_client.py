import re
from datetime import datetime

import aiohttp

from commanderbot.ext.jira.jira_issue import JiraIssue, StatusColor
from commanderbot.lib.responsive_exception import ResponsiveException

ISSUE_ID_PATTERN = re.compile(r"\w+-\d+")


class JiraException(ResponsiveException):
    pass


class IssueNotFound(JiraException):
    def __init__(self, issue_id: str):
        self.issue_id = issue_id
        super().__init__(f"`{self.issue_id}` does not exist or it may be private")


class IssueHasNoFields(JiraException):
    def __init__(self, issue_id: str):
        self.issue_id = issue_id
        super().__init__(f"`{self.issue_id}` does not have any fields")


class InvalidIssueFormat(JiraException):
    def __init__(self):
        super().__init__("Jira issues must use the `<project>-<id>` format")


class ConnectionError(JiraException):
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Could not connect to `{self.url}`")


class RequestError(JiraException):
    def __init__(self, issue_id: str):
        self.issue_id = issue_id
        super().__init__(f"There was an error while requesting `{self.issue_id}`")


class JiraClient:
    def __init__(self, url: str):
        self.url = url

    async def _request_issue_data(self, issue_id: str) -> dict:
        try:
            issue_url: str = f"{self.url}/rest/api/latest/issue/{issue_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(issue_url, raise_for_status=True) as response:
                    return await response.json()

        except aiohttp.ClientResponseError:
            raise IssueNotFound(issue_id)

        except aiohttp.ClientConnectorError:
            raise ConnectionError(self.url)

        except aiohttp.ClientError:
            raise RequestError(issue_id)

    async def get_issue(self, issue_id: str) -> JiraIssue:
        # Check if issue ID is using the correct format
        if not ISSUE_ID_PATTERN.match(issue_id):
            raise InvalidIssueFormat

        # Request issue data and get its fields
        data: dict = await self._request_issue_data(issue_id)
        fields: dict = data.get("fields", {})
        if not fields:
            raise IssueHasNoFields(issue_id)

        # Extract data from fields and construct an issue
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
            issue_id=issue_id,
            url=f"{self.url}/browse/{issue_id}",
            icon_url=f"{self.url}/jira-favicon-hires.png",
            summary=fields["summary"],
            reporter=fields["reporter"]["displayName"],
            assignee=assignee,
            created=datetime.strptime(fields["created"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            updated=datetime.strptime(fields["updated"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            status=fields["status"]["name"],
            status_color=StatusColor.from_str(
                fields["status"]["statusCategory"]["colorName"]
            ),
            resolution=resolution,
            since_version=since_version,
            fix_version=fix_version,
            votes=fields["votes"]["votes"],
        )
