from nonebot.plugin import PluginMetadata
from nonebot import get_app, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
from nonebot.adapters.onebot.v11.event import PrivateMessageEvent
from fastapi import FastAPI
from fastapi.requests import Request

from qqchan.config import Config
from qqchan.exc import NotGroupAdminError
from qqchan import service

__plugin_meta__ = PluginMetadata(
    name="qqchan",
    description="QQ酱，一个运行在Onebot11上的、类似于Server酱的消息推送服务",
    usage="""/register：为当前用户注册，会返回一个id
/register <群号>：为指定群聊注册（必须是管理员）
/list：列出当前用户的所有id
/list <群号>：列出当前用户在指定群聊的所有id
/list all：列出当前用户的所有id，以及当前用户注册的所有群聊id
/revoke <id>：注销指定id（当前用户或当前用户注册的群聊）
/revoke me：注销当前用户的所有id
/revoke all：注销当前用户的所有id，以及当前用户注册的所有群聊id
""",
    config=Config,
)
assert isinstance(app := get_app(), FastAPI), '不支持的驱动器'


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


@app.get('/qqchan/send')
@app.post('/qqchan/send')
async def _(bot: Bot, id: str, req: Request, msg: str | None = None):
    if not msg:
        if not (body := await req.body()):
            return {"success": False, 'msg': '请提供消息内容'}
        try:
            msg = body.decode('utf-8')
        except Exception:
            return {"success": False, "msg": '该消息无法被UTF-8解码'}
    try:
        await service.send_msg(bot, msg, id)
    except KeyError:
        return {"success": False, "msg": '无此id'}
    except NotGroupAdminError:
        return {"success": False, "msg": '你不是管理员，已吊销id'}
    else:
        return {"success": True, "msg": '发送成功'}
