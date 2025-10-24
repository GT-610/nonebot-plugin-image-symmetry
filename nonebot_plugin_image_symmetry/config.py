from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """图像对称插件配置类"""
    # 可以在这里添加配置项
    pass


# 获取配置实例
symmetry_config = get_plugin_config(Config)