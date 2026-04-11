from pydantic import BaseModel
from nonebot import get_plugin_config


class Config(BaseModel):
    """Plugin Config Here"""
    DATABASE_URL: str#  = 'sqlite:///./targets.db'

# config = Config.model_validate(get_driver().config)
config = get_plugin_config(Config)
