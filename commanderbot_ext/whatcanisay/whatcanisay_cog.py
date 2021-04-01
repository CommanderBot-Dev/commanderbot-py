import json
import math
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from commanderbot_lib.logging import get_logger
from discord import Message, TextChannel
from discord.abc import Messageable
from discord.ext.commands import Bot, Cog

MESSAGE_SPLIT_LENGTH = 1500


@dataclass
class Rule:
    name: str
    response: str
    pattern: Optional[re.Pattern] = None
    chance: float = 1.0
    cooldown: timedelta = field(default_factory=lambda: timedelta(seconds=600))
    last_response: Optional[datetime] = None
    hits: int = 0
    hit_scale: float = 1.0

    def current_cooldown(self) -> Optional[timedelta]:
        if self.last_response:
            now = datetime.utcnow()
            delta = now - self.last_response
            extra_cooldown = self.cooldown * self.hit_scale * self.hits
            actual_cooldown = self.cooldown + extra_cooldown
            if delta < actual_cooldown:
                return actual_cooldown - delta

    def match(self, content: str) -> bool:
        if self.pattern:
            return bool(self.pattern.search(content))
        return True

    def roll(self) -> bool:
        return random.random() < self.chance

    def available(self) -> bool:
        return not self.current_cooldown()

    def check(self, content: str) -> bool:
        if self.available() and self.roll() and self.match(content):
            now = datetime.utcnow()
            self.last_response = now
            self.hits += 1
            return True
        return False

    @staticmethod
    def deserialize(data: dict) -> "Rule":
        raw_pattern = data.get("pattern")
        pattern = re.compile(raw_pattern) if raw_pattern else None
        raw_last_response = data.get("last_response")
        last_response = (
            datetime.fromisoformat(raw_last_response) if raw_last_response else None
        )
        return Rule(
            name=data["name"],
            response=data["response"],
            pattern=pattern,
            chance=data.get("chance", 1.0),
            cooldown=timedelta(seconds=data.get("cooldown", 600)),
            last_response=last_response,
            hits=data.get("hits", 0),
            hit_scale=data.get("hit_scale", 1.0),
        )

    def serialize(self) -> dict:
        data = {
            "name": self.name,
            "response": self.response,
            "chance": self.chance,
            "cooldown": self.cooldown.total_seconds(),
            "hits": self.hits,
            "hit_scale": self.hit_scale,
        }
        if self.pattern:
            data["pattern"] = str(self.pattern.pattern)
        if self.last_response:
            data["last_response"] = self.last_response.isoformat()
        return data


class WhatcanisayCog(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.managers: Dict[int, str] = {}
        self.channels: Dict[int, str] = {}
        self.rules: List[Rule] = []
        self.log = get_logger("whatcanisay")

    def load(self):
        with open("data/whatcanisay.json") as fp:
            data = json.load(fp)
        self.managers = {int(k): v for k, v in data.get("managers", {}).items()}
        self.channels = {int(k): v for k, v in data.get("channels", {}).items()}
        raw_rules = data.get("rules", [])
        rules = [Rule.deserialize(raw_rule) for raw_rule in raw_rules]
        self.rules = rules

    def dump(self):
        data = {
            "managers": {str(k): v for k, v in self.managers.items()},
            "channels": {str(k): v for k, v in self.channels.items()},
            "rules": [rule.serialize() for rule in self.rules],
        }
        with open("data/whatcanisay.json", "w") as fp:
            json.dump(data, fp, indent=2)

    async def reload(self, channel: Messageable):
        self.load()
        await self.print_channels(channel)
        await self.print_rules(channel)

    async def print_lines(self, channel: Messageable, lines: List[str]):
        lines_iter = iter(lines)
        content = next(lines_iter)
        for line in lines_iter:
            would_be_content = content + "\n" + line
            would_be_len = len(would_be_content)
            if would_be_len < MESSAGE_SPLIT_LENGTH:
                content = would_be_content
            else:
                await channel.send(f"```\n{content}\n```")
                content = line
        if content:
            await channel.send(f"```\n{content}\n```")

    async def print_channels(self, channel: Messageable):
        resolved_channels = [self.bot.get_channel(ch_id) for ch_id in self.channels]
        sorted_channels = sorted(
            resolved_channels, key=lambda ch: (ch.guild.name, ch.name)
        )
        channel_lines = []
        for ch in sorted_channels:
            channel_lines.append(f"{ch.guild.name} #{ch.name} ({ch.id})")
        await self.print_lines(channel, channel_lines)

    async def print_rules(self, channel: Messageable):
        sorted_rules = sorted(self.rules, key=lambda rule: (-rule.hits, rule.name))
        max_hits = sorted_rules[0].hits
        justify = 3 + round(math.log10(max_hits))
        rule_lines = []
        for rule in sorted_rules:
            rule_line = str(rule.hits).ljust(justify) + rule.name
            if current_cooldown := rule.current_cooldown():
                rule_line += f" ⌛ {current_cooldown}"
            rule_lines.append(rule_line)
        await self.print_lines(channel, rule_lines)

    async def check_rules(self, channel: TextChannel, content: str):
        for rule in self.rules:
            if rule.check(content):
                self.log.critical(f"[{channel.guild} #{channel}] {rule.name}")
                await channel.send(rule.response)
                self.dump()
                return

    @Cog.listener()
    async def on_ready(self):
        self.load()

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return
        channel = message.channel
        content = str(message.clean_content).lower()
        if content.startswith("whatcanisay") and (message.author.id in self.managers):
            if content == "whatcanisay load":
                self.load()
            elif content == "whatcanisay dump":
                self.dump()
            elif content == "whatcanisay reload":
                await self.reload(channel)
            elif content == "whatcanisay channels":
                await self.print_channels(channel)
            elif content == "whatcanisay rules":
                await self.print_rules(channel)
        elif isinstance(channel, TextChannel) and channel.id in self.channels:
            await self.check_rules(channel, content)
