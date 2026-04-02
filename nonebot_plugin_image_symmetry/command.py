from dataclasses import dataclass
from typing import Callable, Optional

from nonebot.log import logger

from .functions import symmetric_bottom, symmetric_left, symmetric_right, symmetric_top


@dataclass
class Command:
    """命令数据类，封装命令关键词和对应的处理函数"""
    keywords: tuple[str, ...]
    func: Callable

def _create_symmetric_process_func(func: Callable, direction_name: str) -> Callable:
    def process_func(
        img_bytes: Optional[bytes] = None,
        image_type: Optional[str] = None,
    ) -> Optional[bytes]:
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
    Command(("对称左", "对称"), symmetric_left_process),
    Command(("对称右",), symmetric_right_process),
    Command(("对称上",), symmetric_top_process),
    Command(("对称下",), symmetric_bottom_process),
]
