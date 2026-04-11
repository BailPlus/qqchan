from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import Bot


async def check_group_admin(bot: Bot, group_id: int, user_id: int) -> bool:
    try:
        member_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id, no_cache=True)
    except ActionFailed:
        return False
    return member_info['role'] in ['admin', 'owner']
