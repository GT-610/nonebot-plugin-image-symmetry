from dataclasses import dataclass
from typing import Callable, Optional

from nonebot.log import logger
from nonebot_plugin_alconna import Args, Image

from .functions import (
    symmetric_left,
    symmetric_right,
    symmetric_top,
    symmetric_bottom
)

arg_image = Args["img", Image]

@dataclass
class Command:
    """命令数据类，封装命令关键词、参数和对应的处理函数"""
    keywords: tuple[str, ...]
    args: Args
    func: Callable

def _create_symmetric_process_func(func: Callable, direction_name: str) -> Callable:
    """创建对称处理函数的工厂方法
    
    Args:
        func: 实际的处理函数
        direction_name: 方向名称，用于日志记录
    
    Returns:
        包装后的处理函数
    """
    def process_func(img_bytes: bytes = None, image_type: str = None) -> Optional[bytes]:
        try:
            return func(img_bytes, image_type)
        except Exception as e:
            logger.debug(f"图像{direction_name}对称处理失败: {e}")
            return None
    return process_func

symmetric_left_process = _create_symmetric_process_func(symmetric_left, "左")
symmetric_right_process = _create_symmetric_process_func(symmetric_right, "右")
symmetric_top_process = _create_symmetric_process_func(symmetric_top, "上")
symmetric_bottom_process = _create_symmetric_process_func(symmetric_bottom, "下")

commands = [
    Command(("对称左", "对称"), arg_image, symmetric_left_process),
    Command(("对称右",), arg_image, symmetric_right_process),
    Command(("对称上",), arg_image, symmetric_top_process),
    Command(("对称下",), arg_image, symmetric_bottom_process),
]