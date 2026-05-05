from typing import Iterable
from collections import defaultdict
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
import uuid

from qqchan import utils
from qqchan.db import Target, TargetType
from qqchan.exc import NotGroupAdminError


async def handle_register_private(user_id: int) -> str:
    id = str(uuid.uuid4())
    Target(
        id=id,
        type=TargetType.PRIVATE,
        target_id=user_id,
        registrant=user_id
    ).register()
    return id


async def handle_register_group(bot: Bot, group_id: int, user_id: int) -> str:
    if not await utils.check_group_admin(bot, group_id, user_id):
        raise NotGroupAdminError
    id = str(uuid.uuid4())
    Target(
        id=id,
        type=TargetType.GROUP,
        target_id=group_id,
        registrant=user_id
    ).register()
    return id


async def handle_list_private(user_id: int) -> Iterable[str]:
    targets = Target.get_targets_by_target_id(user_id)
    return (target.id for target in targets)


async def handle_list_group(group_id: int, user_id: int) -> Iterable[str]:
    targets = Target.get_targets_by_target_id(group_id, user_id)
    return (target.id for target in targets)


async def handle_list_user_all(user_id: int) -> Iterable[str]:
    target_objs = Target.get_targets_by_registrant(user_id)
    target_dict: dict[str | int, list[str]] = defaultdict(list) # type: ignore
    for t in target_objs:
        if t.type == TargetType.PRIVATE:
            target_dict['private'].append(t.id)
        else:
            target_dict[t.target_id].append(t.id)
    target_lst = [
        f'{target}:\n- ' + '\n- '.join(target_dict[target]) + '\n'
        for target in target_dict
    ]
    return target_lst

async def handle_revoke_private(user_id: int, id: str):
    target = Target.get_target_by_id(id)
    if target.registrant != user_id:
        raise NotGroupAdminError
    target.delete()


async def handle_revoke(id: str, user_id: int):
    target = Target.get_target_by_id(id)
    if target.registrant != user_id:
        raise KeyError
    target.delete()


async def handle_revoke_me(user_id: int):
    for t in Target.get_targets_by_target_id(user_id):
        if t.type != TargetType.PRIVATE:
            continue
        t.delete()


async def handle_revoke_all(user_id: int):
    for t in Target.get_targets_by_registrant(user_id):
        t.delete()


async def send_msg(bot: Bot, msg: str, id: str):
    target = Target.get_target_by_id(id)
    match target.type:
        case TargetType.GROUP:
            if not await utils.check_group_admin(bot, target.target_id, target.registrant):
                target.delete()
                raise NotGroupAdminError
            await bot.send_group_msg(
                group_id=target.target_id,
                message=MessageSegment.text(msg) +
                    MessageSegment.text("\n来自") +
                    MessageSegment.at(target.registrant) +
                    MessageSegment.text("的推送")
            )
        case TargetType.PRIVATE:
            await bot.send_msg(
                user_id=target.target_id,
                message=Message(MessageSegment.text(msg))
            )
