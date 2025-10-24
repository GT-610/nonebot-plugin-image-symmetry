import hashlib
import os
from typing import Any
from nonebot_plugin_localstore import get_cache_dir
from nonebot.log import logger


class SymmetryUtils:
    """对称处理工具类"""
    
    @staticmethod
    def get_cache_dir() -> str:
        """获取缓存目录"""
        cache_dir = get_cache_dir(plugin_name="nonebot_plugin_image_symmetry")
        os.makedirs(cache_dir, exist_ok=True)
        return str(cache_dir)
    
    @staticmethod
    def bytes_to_temp_file(img_bytes: bytes) -> str:
        """将字节流转换为临时文件并返回路径"""
        cache_dir = SymmetryUtils.get_cache_dir()
        # 生成唯一的文件名（基于内容的哈希值）
        temp_path = os.path.join(cache_dir, f"temp_{hashlib.md5(img_bytes).hexdigest()}.jpg")
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(img_bytes)
            return temp_path
        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            return None
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """清理临时文件"""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")