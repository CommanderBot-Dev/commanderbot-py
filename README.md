# CommanderBot Ext

A collection of cogs and extensions for discord.py bots.

[![package-badge]](https://pypi.python.org/pypi/commanderbot/)
[![version-badge]](https://pypi.python.org/pypi/commanderbot/)

## Requirements

- Python 3.10+
- discord.py 2.0+

## Running your bot

You can run your own bot without writing any code.

You will need the following:

1. Your own [Discord Application](https://discordapp.com/developers/applications) with a bot token.
2. A [configuration file](#configuring-your-bot) for the bot.
3. A Python 3.10+ environment with the `commanderbot` package installed.
   - It is recommended to use a [virtual environment](https://docs.python.org/3/tutorial/venv.html) for this.
   - Run `pip install commanderbot` to install the bot core package.

The first thing you should do is check the CLI help menu:

```bash
python -m commanderbot --help
```

There are three ways to provide your bot token:

1. (Recommended) As the `BOT_TOKEN` environment variable: `BOT_TOKEN=put_your_bot_token_here`
2. As a CLI option: `--token put_your_bot_token_here`
3. Manually, when prompted during start-up

Here's an example that provides the bot token as an argument:

```bash
python -m commanderbot bot.json --token put_your_bot_token_here
```

## Configuring your bot

The current set of configuration options is limited. Following is an example configuration that sets the command prefix and loads the `status` and `faq` extensions.

> Note that with this configuration, the `faq` extension will require read-write access to `faq.json` in the working directory.

```json
{
  "command_prefix": ">",
  "extensions": [
    "commanderbot.ext.status",
    {
      "name": "commanderbot.ext.faq",
      "enabled": true,
      "options": {
        "database": "faq.json",
        "prefix": "?"
      }
    }
  ]
}
```

[package-badge]: https://img.shields.io/pypi/v/commanderbot.svg
[version-badge]: https://img.shields.io/pypi/pyversions/commanderbot.svg
