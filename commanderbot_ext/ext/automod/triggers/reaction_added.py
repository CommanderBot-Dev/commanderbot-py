from dataclasses import dataclass

from commanderbot_ext.ext.automod import events
from commanderbot_ext.ext.automod.automod_trigger import AutomodTrigger
from commanderbot_ext.ext.automod.triggers.reaction import Reaction
from commanderbot_ext.lib import JsonObject


@dataclass
class ReactionAdded(Reaction):
    """
    Fires when an `on_reaction_add` event is received.

    See: https://discordpy.readthedocs.io/en/stable/api.html?highlight=events#discord.on_reaction_add

    Attributes
    ----------
    reactions
        The reactions to match against. If empty, all reactions will match.
    channels
        The channels to match against. If empty, all channels will match.
    author_roles
        The author roles to match against. If empty, all roles will match.
    actor_roles
        The actor roles to match against. If empty, all roles will match.
    """

    event_types = (events.ReactionAdded,)


def create_trigger(data: JsonObject) -> AutomodTrigger:
    return ReactionAdded.from_data(data)
