import allay
from discord.ext.commands import Bot, Cog, Context, command


class AllayCog(Cog, name="commanderbot.ext.allay"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.parser = allay.Parser()

    @command(name="allay")
    async def cmd_vote(self, ctx: Context):
        contents = ctx.message.content.partition("\n")

        indent = None
        command_and_optional_indent = contents[0].split(" ")
        if len(command_and_optional_indent) > 1:
            str_indent = command_and_optional_indent[1]

            # Handle trailing space after ">allay"
            if not str_indent:
                indent = None

            else:
                indent = int(command_and_optional_indent[1])
                # Large indents hang the bot
                if indent > 10:
                    await ctx.reply(
                        "Indent level cannot be greater than 10", mention_author=False
                    )
                    return

        # Remove the backticks and newlines
        code_block = contents[2][4:-4]
        # Parse the output and print it in a code block
        parsed_contents = (
            self.parser.parse(code_block)
            if not indent
            else self.parser.parse(code_block, indent)
        )
        await ctx.send("```json\n" + parsed_contents + "\n```")
