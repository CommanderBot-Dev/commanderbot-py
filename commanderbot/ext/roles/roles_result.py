from __future__ import annotations

from dataclasses import dataclass
from typing import List, Type, TypeVar

from discord import Member, Role

from commanderbot.ext.roles.roles_store import RolesStore

ST = TypeVar("ST")


@dataclass
class RolesResult:
    not_registered: List[Role]

    @staticmethod
    def _join_mentions(roles: List[Role]) -> str:
        if len(roles) > 1:
            return (
                ", ".join(role.mention for role in roles[:-1])
                + " and "
                + roles[-1].mention
            )
        if len(roles) == 1:
            return roles[0].mention
        return ""

    @classmethod
    async def build(cls: Type[ST], store: RolesStore, *args, **kwargs) -> ST:
        raise NotImplementedError()

    async def apply(self) -> List[str]:
        raise NotImplementedError()


@dataclass
class JoinableRolesResult(RolesResult):
    member: Member
    joinable: List[Role]
    not_joinable: List[Role]
    already_in: List[Role]

    @classmethod
    async def build(
        cls,
        store: RolesStore,
        member: Member,
        roles: List[Role],
    ) -> JoinableRolesResult:
        # A role is joinable if:
        # 1. it is registered; and
        # 2. it is configured as joinable; and
        # 3. the member does not already have it.
        joinable: List[Role] = []
        not_registered: List[Role] = []
        not_joinable: List[Role] = []
        already_in: List[Role] = []
        for role in roles:
            if role_enty := await store.get_role_entry(role):
                if not role_enty.joinable:
                    not_joinable.append(role)
                    continue
            else:
                not_registered.append(role)
                continue
            if role in member.roles:
                already_in.append(role)
                continue
            joinable.append(role)
        return JoinableRolesResult(
            member=member,
            joinable=joinable,
            not_registered=not_registered,
            not_joinable=not_joinable,
            already_in=already_in,
        )

    # @implements RolesResult
    async def apply(self) -> List[str]:
        lines = []
        if self.joinable:
            joinable_mentions = self._join_mentions(self.joinable)
            try:
                await self.member.add_roles(
                    *self.joinable, reason=f"{self.member} joined roles"
                )
            except:
                lines.append(f"⚠️ Failed to join {joinable_mentions}.")
            else:
                lines.append(f"✅ You joined {joinable_mentions}.")
        if self.not_joinable:
            not_leavable_mentions = self._join_mentions(self.not_joinable)
            lines.append(f"😔 You can't join {not_leavable_mentions}.")
        if self.already_in:
            already_in_mentions = self._join_mentions(self.already_in)
            lines.append(f"🤔 You're already in {already_in_mentions}.")
        if self.not_registered:
            not_registered_mentions = self._join_mentions(self.not_registered)
            lines.append(f"❌ These roles aren't registered: {not_registered_mentions}.")
        return lines


@dataclass
class LeavableRolesResult(RolesResult):
    member: Member
    leavable: List[Role]
    not_leavable: List[Role]
    not_in: List[Role]

    @classmethod
    async def build(
        cls,
        store: RolesStore,
        member: Member,
        roles: List[Role],
    ) -> LeavableRolesResult:
        # A role is leavable if:
        # 1. it is registered; and
        # 2. it is configured as leavable; and
        # 3. the member has it.
        leavable: List[Role] = []
        not_registered: List[Role] = []
        not_leavable: List[Role] = []
        not_in: List[Role] = []
        for role in roles:
            if role_enty := await store.get_role_entry(role):
                if not role_enty.leavable:
                    not_leavable.append(role)
                    continue
            else:
                not_registered.append(role)
                continue
            if role not in member.roles:
                not_in.append(role)
                continue
            leavable.append(role)
        return LeavableRolesResult(
            member=member,
            leavable=leavable,
            not_registered=not_registered,
            not_leavable=not_leavable,
            not_in=not_in,
        )

    # @implements RolesResult
    async def apply(self) -> List[str]:
        lines = []
        if self.leavable:
            leavable_mentions = self._join_mentions(self.leavable)
            try:
                await self.member.remove_roles(
                    *self.leavable, reason=f"{self.member} left roles"
                )
            except:
                lines.append(f"⚠️ Failed to leave {leavable_mentions}.")
            else:
                lines.append(f"✅ You left {leavable_mentions}.")
        if self.not_leavable:
            not_leavable_mentions = self._join_mentions(self.not_leavable)
            lines.append(f"😈 You can't leave {not_leavable_mentions}.")
        if self.not_in:
            not_in_mentions = self._join_mentions(self.not_in)
            lines.append(f"🤔 You're not in {not_in_mentions}.")
        if self.not_registered:
            not_registered_mentions = self._join_mentions(self.not_registered)
            lines.append(f"❌ These roles aren't registered: {not_registered_mentions}.")
        return lines


@dataclass
class AddableRolesResult(RolesResult):
    target: Member
    actor: Member
    addable: List[Role]
    already_in: List[Role]

    @classmethod
    async def build(
        cls,
        store: RolesStore,
        target_user: Member,
        roles: List[Role],
        acting_user: Member,
    ) -> AddableRolesResult:
        # A role is addable if:
        # 1. it is registered; and
        # 2. the member does not already have it.
        addable: List[Role] = []
        not_registered: List[Role] = []
        already_in: List[Role] = []
        for role in roles:
            if not await store.get_role_entry(role):
                not_registered.append(role)
                continue
            if role in target_user.roles:
                already_in.append(role)
                continue
            addable.append(role)
        return AddableRolesResult(
            target=target_user,
            actor=acting_user,
            addable=addable,
            not_registered=not_registered,
            already_in=already_in,
        )

    # @implements RolesResult
    async def apply(self) -> List[str]:
        lines = []
        if self.addable:
            addable_mentions = self._join_mentions(self.addable)
            try:
                await self.target.add_roles(
                    *self.addable, reason=f"{self.actor} added roles to user"
                )
            except:
                lines.append(
                    f"⚠️ Failed to add {addable_mentions} to {self.target.mention}."
                )
            else:
                lines.append(
                    f"✅ {self.target.mention} has been added to {addable_mentions}."
                )
        if self.already_in:
            already_in_mentions = self._join_mentions(self.already_in)
            lines.append(
                f"🤷 {self.target.mention} is already in {already_in_mentions}."
            )
        if self.not_registered:
            not_registered_mentions = self._join_mentions(self.not_registered)
            lines.append(f"❌ These roles aren't registered: {not_registered_mentions}.")
        return lines


@dataclass
class RemovableRolesResult(RolesResult):
    target: Member
    actor: Member
    removable: List[Role]
    not_in: List[Role]

    @classmethod
    async def build(
        cls,
        store: RolesStore,
        target_user: Member,
        roles: List[Role],
        acting_user: Member,
    ) -> RemovableRolesResult:
        # A role is removable if:
        # 1. it is registered; and
        # 2. the member has it.
        removable: List[Role] = []
        not_registered: List[Role] = []
        not_in: List[Role] = []
        for role in roles:
            if not await store.get_role_entry(role):
                not_registered.append(role)
                continue
            if role not in target_user.roles:
                not_in.append(role)
                continue
            removable.append(role)
        return RemovableRolesResult(
            target=target_user,
            actor=acting_user,
            removable=removable,
            not_registered=not_registered,
            not_in=not_in,
        )

    # @implements RolesResult
    async def apply(self) -> List[str]:
        lines = []
        if self.removable:
            removable_mentions = self._join_mentions(self.removable)
            try:
                await self.target.remove_roles(
                    *self.removable,
                    reason=f"{self.actor} removed roles from user",
                )
            except:
                lines.append(
                    f"⚠️ Failed to remove {removable_mentions} from {self.target.mention}."
                )
            else:
                lines.append(
                    f"✅ {self.target.mention} has been removed from {removable_mentions}."
                )
        if self.not_in:
            not_in_mentions = self._join_mentions(self.not_in)
            lines.append(f"🤷 {self.target.mention} is not in {not_in_mentions}.")
        if self.not_registered:
            not_registered_mentions = self._join_mentions(self.not_registered)
            lines.append(f"❌ These roles aren't registered: {not_registered_mentions}.")
        return lines
