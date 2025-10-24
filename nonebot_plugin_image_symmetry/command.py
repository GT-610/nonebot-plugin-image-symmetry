from dataclasses import dataclass
from typing import Callable, Optional, Any

from nonebot.log import logger
from nonebot_plugin_alconna import Args, Image

from .functions import (
    process_image_symmetric_left,
    process_image_symmetric_right,
    process_image_symmetric_top,
    process_image_symmetric_bottom
)
from .utils import SymmetryUtils

# 定义参数
arg_image = Args["img", Image]

# 定义命令数据类
@dataclass
class Command:
    """命令数据类"""
    keywords: tuple[str, ...]  # 命令关键词列表
    args: Args  # 参数定义
    func: Callable  # 处理函数

# 定义处理函数，直接处理字节流并返回结果
def symmetric_left_process(img_bytes: bytes) -> Optional[bytes]:
    """对称左处理函数"""
    # 创建临时文件用于处理，但不清理（因为已经在before目录保存了原始图片）
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_left(temp_file)
    except Exception as e:
        logger.error(f"对称左处理函数执行失败: {e}")
        return None


def symmetric_right_process(img_bytes: bytes) -> Optional[bytes]:
    """对称右处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_right(temp_file)
    except Exception as e:
        logger.error(f"对称右处理函数执行失败: {e}")
        return None


def symmetric_top_process(img_bytes: bytes) -> Optional[bytes]:
    """对称上处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_top(temp_file)
    except Exception as e:
        logger.error(f"对称上处理函数执行失败: {e}")
        return None


def symmetric_bottom_process(img_bytes: bytes) -> Optional[bytes]:
    """对称下处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_bottom(temp_file)
    except Exception as e:
        logger.error(f"对称下处理函数执行失败: {e}")
        return None


# 创建命令列表
commands = [
    Command(("对称左", "对称"), arg_image, symmetric_left_process),
    Command(("对称右",), arg_image, symmetric_right_process),
    Command(("对称上",), arg_image, symmetric_top_process),
    Command(("对称下",), arg_image, symmetric_bottom_process),
]