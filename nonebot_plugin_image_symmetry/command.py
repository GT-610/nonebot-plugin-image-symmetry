from dataclasses import dataclass
from typing import Callable, Optional

from nonebot.log import logger
from nonebot_plugin_alconna import Args, Image

from .functions import (
    process_image_symmetric_left,
    process_image_symmetric_right,
    process_image_symmetric_top,
    process_image_symmetric_bottom
)

# 定义图像参数，用于命令匹配器接收图片输入
arg_image = Args["img", Image]

# 定义命令数据类，用于存储命令关键词、参数和处理函数的映射关系
@dataclass
class Command:
    """命令数据类，封装命令关键词、参数和对应的处理函数"""
    keywords: tuple[str, ...]  # 命令关键词列表，用于触发命令
    args: Args  # 参数定义，指定命令需要的参数类型
    func: Callable  # 处理函数，执行对应图像处理操作

# 定义处理函数，直接处理字节流并返回结果
def symmetric_left_process(temp_path: str, image_type: str = None) -> Optional[bytes]:
    """执行图像左侧对称处理
    
    Args:
        temp_path: 临时图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节流，如果处理失败返回None
    """
    try:
        return process_image_symmetric_left(temp_path, image_type)
    except Exception as e:
        logger.debug(f"图像左侧对称处理失败: {e}")
        return None


def symmetric_right_process(temp_path: str, image_type: str = None) -> Optional[bytes]:
    """执行图像右侧对称处理
    
    Args:
        temp_path: 临时图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节流，如果处理失败返回None
    """
    try:
        return process_image_symmetric_right(temp_path, image_type)
    except Exception as e:
        logger.debug(f"图像右侧对称处理失败: {e}")
        return None


def symmetric_top_process(temp_path: str, image_type: str = None) -> Optional[bytes]:
    """执行图像上方对称处理
    
    Args:
        temp_path: 临时图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节流，如果处理失败返回None
    """
    try:
        return process_image_symmetric_top(temp_path, image_type)
    except Exception as e:
        logger.debug(f"图像上方对称处理失败: {e}")
        return None


def symmetric_bottom_process(temp_path: str, image_type: str = None) -> Optional[bytes]:
    """执行图像下方对称处理
    
    Args:
        temp_path: 临时图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节流，如果处理失败返回None
    """
    try:
        return process_image_symmetric_bottom(temp_path, image_type)
    except Exception as e:
        logger.debug(f"图像下方对称处理失败: {e}")
        return None

# 创建命令列表，定义所有可用的对称处理命令
commands = [
    Command(("对称左", "对称"), arg_image, symmetric_left_process),
    Command(("对称右",), arg_image, symmetric_right_process),
    Command(("对称上",), arg_image, symmetric_top_process),
    Command(("对称下",), arg_image, symmetric_bottom_process),
]