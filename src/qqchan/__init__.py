from nonebot.plugin import PluginMetadata
from nonebot import get_bot, get_app, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from fastapi import FastAPI

from qqchan.db import Target
from qqchan.config import Config
from qqchan.utils import check_group_admin
from qqchan.exceptions import *
from qqchan import service

__plugin_meta__ = PluginMetadata(
    name="qqchan",
    description="",
    usage="",
    config=Config,
)
app: FastAPI = get_app()


register_cmd = on_command('register')
@register_cmd.handle()
async def _(e: PrivateMessageEvent, bot: Bot, arg: Message = CommandArg()):
    user_id = e.user_id
    group_id = arg.extract_plain_text()

    # 为指定群聊注册（必须是管理员）
    if group_id:
        group_id = int(group_id)
        try:
            id = await service.handle_register_group(bot, group_id, user_id)
        except NotGroupAdminError:
            await register_cmd.finish('你不是管理员')
        else:
            await register_cmd.finish(MessageSegment.text(id))

    # 为当前用户注册
    else:
        id = await service.handle_register_private(user_id)
        await register_cmd.finish(MessageSegment.text(id))


list_cmd = on_command('list')
@list_cmd.handle()
async def _(e: PrivateMessageEvent, arg: Message = CommandArg()):
    user_id = e.user_id
    argstr = arg.extract_plain_text()

    # 列出当前用户的所有id，以及当前用户注册的所有群聊id
    if argstr == 'all':
        targets = await service.handle_list_user_all(user_id)

    # 列出当前用户的所有id，以及当前用户注册的所有群聊id
    elif argstr:
        group_id = int(argstr)
        targets = await service.handle_list_group(group_id, user_id)

    # 列出当前用户的所有id
    else:
        targets = await service.handle_list_private(e.user_id)
    
    targets = '\n'.join(targets)
    if not targets.strip():
        await list_cmd.finish(MessageSegment.text('你还没有注册'))
    await list_cmd.finish(MessageSegment.text(targets))


revoke_cmd = on_command('revoke')
@revoke_cmd.handle()
async def _(e: PrivateMessageEvent, arg: Message = CommandArg()):
    user_id = e.user_id
    argstr = arg.extract_plain_text()

    if not argstr:
        await revoke_cmd.finish('请输入id、`all`或`me`')

    # 注销当前用户的所有id，以及当前用户注册的所有群聊id
    elif argstr == 'all':
        await service.handle_revoke_all(user_id)

    # 注销当前用户的所有id
    elif argstr == 'me':
        await service.handle_revoke_me(user_id)

    # 注销指定id（当前用户或当前用户注册的群聊）
    else:
        id = argstr
        try:
            await service.handle_revoke(id, user_id)
        except KeyError:
            await revoke_cmd.finish('你无此id')

    await revoke_cmd.finish('删除成功')


@app.get('/send')
async def _(msg: str, id: str):
    assert isinstance(bot := get_bot(), Bot)
    try:
        await service.send_msg(bot, msg, id)
    except KeyError:
        return '无此id'
    except NotGroupAdminError:
        return '你不是管理员，已吊销id'
    else:
        return '发送成功'
