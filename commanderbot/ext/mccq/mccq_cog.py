from logging import Logger, getLogger
from sre_constants import error as RegexError
from typing import Optional

import mccq.errors
from discord import Game
from discord.ext.commands import Bot, Cog, Context, command
from mccq.query_manager import QueryManager
from mccq.version_database import VersionDatabase

from commanderbot.lib import checks


class MCCQCog(Cog, name="commanderbot.ext.mccq"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.log: Logger = getLogger(self.qualified_name)

        # java edition commands.json
        self.java_url: str = options.get("java_url", "")
        if not self.java_url:
            self.log.warning("No Java URL was provided")

        # bedrock edition commands.json
        self.bedrock_url: str = options.get("bedrock_url", "")
        if not self.bedrock_url:
            self.log.warning("No Bedrock URL was provided")

        # path to the file containing nothing but the version of the generated files
        self.version_file: str = options.get("version_file", "VERSION.txt")

        # labels to print instead of database keys
        self.version_labels: dict[str, str] = options.get("version_labels", {})

        # version whitelist, disabled if empty
        self.version_whitelist = tuple(options.get("version_whitelist", []))

        # versions to render in the output by default
        # if not specified, defaults to the last whitelist entry
        last_version = self.version_whitelist[-1] if self.version_whitelist else None
        self.show_versions = tuple(
            options.get("show_versions", [last_version] if last_version else ())
        )

        # url format to provide a help link, if any
        # the placeholder `{command}` will be replaced by the base command
        self.help_url = options.get("help_url", None)

        # version to set as the "playing" status, if any
        self.presence_version = options.get("presence_version", None)

        # max lines of results, useful to prevent potential chat spam
        self.max_results = options.get("max_results", None)

        # create java edition query manager, if a url was provided
        self.java_query_manager: Optional[QueryManager] = None
        if self.java_url:
            self.java_query_manager = QueryManager(
                database=VersionDatabase(
                    uri=self.java_url,
                    version_file=self.version_file,
                    whitelist=self.version_whitelist,
                ),
                show_versions=self.show_versions,
            )

        # create java edition query manager, if a url was provided
        self.bedrock_query_manager: Optional[QueryManager] = None
        if self.bedrock_url:
            self.bedrock_query_manager = QueryManager(
                database=VersionDatabase(
                    uri=self.bedrock_url,
                    version_file=self.version_file,
                    whitelist=self.version_whitelist,
                ),
                show_versions=self.show_versions,
            )

    def get_version_label(self, version: str, query_manager: QueryManager) -> str:
        actual_version = query_manager.database.get_actual_version(version) or version
        return self.version_labels.get(version, version).format(
            version=version, actual=actual_version
        )

    async def reload(self):
        if self.java_query_manager:
            self.java_query_manager.reload()

        if self.bedrock_query_manager:
            self.bedrock_query_manager.reload()

        if self.presence_version:
            presence_parts: list[str] = []

            # get the latest java version, if configured
            if self.java_query_manager:
                self.java_query_manager.database.get(self.presence_version)
                java_presence_version = (
                    self.java_query_manager.database.get_actual_version(
                        self.presence_version
                    )
                )
                presence_parts.append(f"{java_presence_version} (Java)")

            # and the latest bedrock version, if configured
            if self.bedrock_query_manager:
                self.bedrock_query_manager.database.get(self.presence_version)
                bedrock_presence_version = (
                    self.bedrock_query_manager.database.get_actual_version(
                        self.presence_version
                    )
                )
                presence_parts.append(f"{bedrock_presence_version} (Bedrock)")

            # and then set the bot's presence status
            if presence_parts:
                presence_text = ", ".join(presence_parts)
                self.log.info(
                    "Setting presence to latest version: {}".format(presence_text)
                )
                await self.bot.change_presence(activity=Game(name=presence_text))
            else:
                self.log.warning("No presence version to update")

    async def mccreload(self, ctx: Context):
        try:
            await self.reload()

        except:
            self.log.exception("An unexpected error occurred while reloading commands")
            await ctx.message.add_reaction("🤯")
            return

        await ctx.message.add_reaction("✅")

    async def mcc(self, ctx: Context, command: str, query_manager: QueryManager):
        # if no command was provided, print help and short-circuit
        if not command:
            help_message = "".join(
                ("```", QueryManager.ARGUMENT_PARSER.format_help(), "```")
            )
            await ctx.message.reply(help_message)
            return

        try:
            # get a copy of the parsed arguments so we can tell the user about them
            arguments = QueryManager.parse_query_arguments(command)

            # get the command results to render
            full_results = query_manager.results_from_arguments(arguments)
            num_full_results = sum(len(lines) for lines in full_results.values())

            # trim results, if enabled
            results = full_results
            num_trimmed_results = 0
            if self.max_results and (num_full_results > self.max_results):
                num_trimmed_results = num_full_results - self.max_results
                results = {}
                num_results = 0
                for version, lines in full_results.items():
                    results[version] = []
                    for line in lines:
                        results[version].append(line)
                        num_results += 1
                        if num_results == self.max_results:
                            break

        except mccq.errors.ArgumentParserFailed:
            self.log.info(
                "Failed to parse arguments for the command: {}".format(command)
            )
            await ctx.message.reply("Invalid arguments for that command")
            return

        except mccq.errors.NoVersionsAvailable:
            self.log.info("No versions available for the command: {}".format(command))
            await ctx.message.reply("No versions available for that command")
            return

        except (mccq.errors.LoaderFailure, mccq.errors.ParserFailure):
            self.log.exception(
                "Failed to load data for the command: {}".format(command)
            )
            await ctx.message.reply("Failed to load data for that command")
            return

        except RegexError:
            self.log.info("Invalid regex for the command: {}".format(command))
            await ctx.message.reply(
                "Invalid regex for that command (you may need to use escaping)",
            )
            return

        except:
            self.log.exception(
                "An unexpected error occurred while processing the command: {}".format(
                    command
                )
            )
            await ctx.message.add_reaction("🤯")
            return

        if not results:
            # let the user know if there were no results, and short-circuit
            # note this is different from an invalid base command
            await ctx.message.reply("No results found for that command")
            return

        # if any version produced more than one command, render one paragraph per version
        if next((True for lines in results.values() if len(lines) > 1), False):
            paragraphs = (
                "\n".join(
                    (
                        "# {}".format(self.get_version_label(version, query_manager)),
                        *lines,
                    )
                )
                for version, lines in results.items()
            )
            command_text = "\n".join(paragraphs)

        # otherwise, if all versions rendered just 1 command, render one line per version (compact)
        else:
            command_text = "\n".join(
                "{}  # {}".format(
                    lines[0], self.get_version_label(version, query_manager)
                )
                for version, lines in results.items()
                if lines
            )

        # if results were trimmed, make note of them
        if num_trimmed_results:
            command_text += "\n# ... trimmed {} results".format(num_trimmed_results)

        # render the full code section
        code_section = "```python\n{}\n```".format(command_text)

        help_section = None

        # don't bother with the help link unless it's been configured
        if self.help_url:
            base_commands = set()
            for lines in results.values():
                for line in lines:
                    base_commands.add(line.split(maxsplit=1)[0])

            # only post the help link if we can unambiguously determine the base command
            base_command = (
                tuple(base_commands)[0] if (len(base_commands) == 1) else None
            )
            if base_command:
                help_section = "".join(
                    ("<", self.help_url.format(command=base_command), ">")
                )

        # leave out blank sections
        message = "\n".join(
            section for section in (code_section, help_section) if section is not None
        )

        # sometimes the message is too big to send
        try:
            await ctx.message.reply(message)
        except:
            num_full_results = sum(len(lines) for lines in results.values())
            self.log.exception(
                "Something went wrong while trying to respond with {} results ({} characters)".format(
                    num_full_results, len(message)
                )
            )
            await ctx.message.add_reaction("😬")

    @command(
        name="mccqreload",
        aliases=["mccreload"],
        hidden=True,
    )
    @checks.is_owner()
    async def cmd_mccreload(self, ctx):
        await self.mccreload(ctx)

    @command(
        name="mccq",
        aliases=["mcc"],
        help=QueryManager.ARGUMENT_PARSER.format_help(),
    )
    async def cmd_mccq(self, ctx: Context, *, command: str = ""):
        if self.java_query_manager:
            await self.mcc(ctx, command, self.java_query_manager)
        else:
            await ctx.message.add_reaction("🤷")

    @command(
        name="mccb",
        aliases=["mccbedrock"],
        help=QueryManager.ARGUMENT_PARSER.format_help(),
    )
    async def cmd_mccb(self, ctx: Context, *, command: str = ""):
        if self.bedrock_query_manager:
            await self.mcc(ctx, command, self.bedrock_query_manager)
        else:
            await ctx.message.add_reaction("🤷")
