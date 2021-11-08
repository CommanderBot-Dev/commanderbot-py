from textwrap import dedent

import allay
from discord.ext.commands import Bot, Cog, Context, command

from commanderbot.lib.responsive_exception import ResponsiveException

CMD_HELP = """
    Convert plaintext into a text-component via Allay
    Usage: https://github.com/DoubleF3lix/Allay

    Example usage:

        .allay [indent]
        `​`​`
        text
        `​`​`
    
    Both plain-text, inline code blocks, and normal code blocks are all supported. There should always be a newline in between the command (and optional indent, if supplied), and the text.
"""


class AllayCog(Cog, name="commanderbot.ext.allay"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.parser = allay.Parser()

    @command(
        name="allay",
        brief="Generate a text-component from plaintext",
        help=dedent(CMD_HELP).strip(),
    )
    async def cmd_allay(self, ctx: Context):
        contents = ctx.message.content.partition("\n")

        indent = None

        # The first part of the command (before any newlines), split by spaces so we can separate the command name and the indent
        command_and_optional_indent = contents[0].split(" ")

        # Handle indent passed on the same line as the command
        if len(command_and_optional_indent) > 1:
            # Store the variable
            after_allay_command = command_and_optional_indent[1]

            # Check if anything was found (the above condition can trigger with a trailing space)
            if after_allay_command:
                try:
                    # Try converting it into an integer
                    indent = int(after_allay_command)
                except ValueError:
                    # If it failed, the user probably passed a string, so we'll print an error and quit
                    await ctx.reply(
                        # Python raises a SyntaxError if a backslash is inside an f-string, so we use chr(10) instead of \n
                        f"Invalid indent level: '{after_allay_command.replace('```', '').replace(chr(10), '')}'",
                        mention_author=False,
                    )
                    return

                # Large indents hang the bot
                if indent > 10:
                    await ctx.reply(
                        "Indent level cannot be greater than 10", mention_author=False
                    )
                    return

        # Remove the backticks and newlines
        code_block = contents[2]
        if code_block.startswith("```\n"):
            start = 4
        elif code_block.startswith("```"):
            start = 3
        elif code_block.startswith("`"):
            start = 1
        else:
            start = None

        if code_block.endswith("\n```"):
            end = -4
        elif code_block.endswith("```"):
            end = -3
        elif code_block.endswith("`"):
            end = -1
        else:
            end = None

        code_block = code_block[start:end]

        if code_block:
            # Parse the output and print it in a code block (None is fine to pass)
            try:
                parsed_contents = self.parser.parse(code_block, indent)
            except Exception as error:
                raise ResponsiveException(
                    f"```\n{error}\n```\nUsage: <https://github.com/DoubleF3lix/Allay#format>"
                ) from error
            await ctx.send("```json\n" + parsed_contents + "\n```")
        else:
            await ctx.reply(
                "No text specified (did you forget to add a newline?)",
                mention_author=False,
            )
            return
