import asyncio
import io
from logging import Logger, getLogger
from textwrap import dedent
from typing import Optional

from discord import File, Message
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot_ext.ext.pack.pack_generate import generate_packs

PACK_HELP = """
    Compile messages into data packs and resource packs with lectern.
    https://github.com/mcbeet/lectern

    Example usage:

        .pack
        `@function demo:foo`
        `​`​`
        say hello
        `​`​`
"""


class PackCog(Cog, name="commanderbot_ext.ext.pack"):
    def __init__(self, bot: Bot, **options):
        self.bot: Bot = bot
        self.log: Logger = getLogger(self.qualified_name)
        self.project_config = options
        self.build_timeout = options.pop("timeout", 5)
        self.show_stacktraces = options.pop("stacktraces", False)

    @command(
        name="pack",
        brief="Generate a data pack or a resource pack.",
        usage="[name]",
        help=dedent(PACK_HELP).strip(),
    )
    async def cmd_pack(self, ctx: Context):
        if not ctx.message:
            self.log.warn("Command executed without message.")
            return

        message: Message = ctx.message
        author = message.author.display_name
        first_line, _, message_content = message.content.partition("\n")
        args = first_line.split()

        name = args[1] if len(args) == 2 else ""

        self.log.info("%s - Running build for %s.", message.id, author)

        loop = asyncio.get_running_loop()

        build_output, attachments = await loop.run_in_executor(
            None,
            generate_packs,
            self.project_config,
            self.build_timeout,
            self.show_stacktraces,
            name or author,
            message_content,
        )

        content = f"```\n{joined}\n```" if (joined := "\n\n".join(build_output)) else ""
        files = [
            File(io.BytesIO(data), filename=filename)
            for filename, data in attachments.items()
        ]

        if content or files:
            await ctx.send(content, files=files)
        else:
            await message.add_reaction("🤔")

        self.log.info("%s - Done.", message.id)
