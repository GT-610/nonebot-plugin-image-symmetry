from dataclasses import dataclass
from typing import Callable, Optional, Any

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

# 定义处理函数，将字节流转换为临时文件路径后调用实际处理函数
def symmetric_left_process(img_bytes: bytes) -> Optional[bytes]:
    """对称左处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_left(temp_file)
    finally:
        SymmetryUtils.cleanup_temp_file(temp_file)


def symmetric_right_process(img_bytes: bytes) -> Optional[bytes]:
    """对称右处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_right(temp_file)
    finally:
        SymmetryUtils.cleanup_temp_file(temp_file)


def symmetric_top_process(img_bytes: bytes) -> Optional[bytes]:
    """对称上处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_top(temp_file)
    finally:
        SymmetryUtils.cleanup_temp_file(temp_file)


def symmetric_bottom_process(img_bytes: bytes) -> Optional[bytes]:
    """对称下处理函数"""
    temp_file = SymmetryUtils.bytes_to_temp_file(img_bytes)
    if not temp_file:
        return None
    
    try:
        return process_image_symmetric_bottom(temp_file)
    finally:
        SymmetryUtils.cleanup_temp_file(temp_file)


# 创建命令列表
commands = [
    Command(("对称左", "对称"), arg_image, symmetric_left_process),
    Command(("对称右",), arg_image, symmetric_right_process),
    Command(("对称上",), arg_image, symmetric_top_process),
    Command(("对称下",), arg_image, symmetric_bottom_process),
]