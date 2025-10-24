import hashlib
import os
import time
from nonebot_plugin_localstore import get_cache_dir
from nonebot.log import logger


class SymmetryUtils:
    """对称处理工具类"""
    
    # 从环境变量读取最大缓存数量，默认为100，范围[5, 9999]
    @staticmethod
    def _get_max_cache_size():
        """从环境变量获取最大缓存数量，并进行范围检查"""
        try:
            env_value = os.environ.get("IMAGE_SYMMETRY_MAX_CACHE", "100")
            max_size = int(env_value)
            # 确保值在有效范围内
            if 5 <= max_size <= 9999:
                logger.debug(f"使用最大缓存图片数量: {max_size} (从环境变量获取)")
                return max_size
            else:
                logger.warning(f"环境变量IMAGE_SYMMETRY_MAX_CACHE值{max_size}超出范围[5, 9999]，使用默认值100")
                logger.debug(f"使用最大缓存图片数量: 100 (默认值)")
                return 100
        except ValueError:
            logger.warning(f"环境变量IMAGE_SYMMETRY_MAX_CACHE值'{env_value}'无效，使用默认值100")
            logger.debug(f"使用最大缓存图片数量: 100 (默认值)")
            return 100
    
    # 两个目录总计的最大缓存图片数量
    MAX_TOTAL_CACHE_SIZE = _get_max_cache_size()
    
    @staticmethod
    def get_cache_dir() -> str:
        """获取缓存目录"""
        cache_dir = get_cache_dir(plugin_name="nonebot_plugin_image_symmetry")
        os.makedirs(cache_dir, exist_ok=True)
        return str(cache_dir)
    
    @staticmethod
    def get_before_cache_dir() -> str:
        """获取原始图片缓存目录"""
        cache_dir = SymmetryUtils.get_cache_dir()
        before_dir = os.path.join(cache_dir, "before")
        os.makedirs(before_dir, exist_ok=True)
        return before_dir
    
    @staticmethod
    def get_after_cache_dir() -> str:
        """获取处理后图片缓存目录"""
        cache_dir = SymmetryUtils.get_cache_dir()
        after_dir = os.path.join(cache_dir, "after")
        os.makedirs(after_dir, exist_ok=True)
        return after_dir
    
    @staticmethod
    def initialize_directories() -> None:
        """初始化所有必要的目录"""
        try:
            before_dir = SymmetryUtils.get_before_cache_dir()
            after_dir = SymmetryUtils.get_after_cache_dir()
            logger.info(f"成功初始化目录结构\nbefore目录: {before_dir}\nafter目录: {after_dir}")
        except Exception as e:
            logger.error(f"初始化目录结构失败: {e}")
    
    @staticmethod
    def cleanup_global_cache(max_size: int = MAX_TOTAL_CACHE_SIZE) -> None:
        """清理全局缓存，控制两个目录（before和after）的总图片数量不超过限制
        
        Args:
            max_size: 两个目录总计的最大缓存文件数量
        """
        try:
            # 获取两个目录的路径
            before_dir = SymmetryUtils.get_before_cache_dir()
            after_dir = SymmetryUtils.get_after_cache_dir()
            
            # 确保目录存在
            os.makedirs(before_dir, exist_ok=True)
            os.makedirs(after_dir, exist_ok=True)
            
            # 获取两个目录中所有的jpg文件及其修改时间
            all_files = []
            
            # 检查before目录
            if os.path.exists(before_dir):
                for filename in os.listdir(before_dir):
                    if filename.lower().endswith('.jpg'):
                        file_path = os.path.join(before_dir, filename)
                        if os.path.isfile(file_path):
                            mod_time = os.path.getmtime(file_path)
                            all_files.append((mod_time, file_path))
            
            # 检查after目录
            if os.path.exists(after_dir):
                for filename in os.listdir(after_dir):
                    if filename.lower().endswith('.jpg'):
                        file_path = os.path.join(after_dir, filename)
                        if os.path.isfile(file_path):
                            mod_time = os.path.getmtime(file_path)
                            all_files.append((mod_time, file_path))
            
            # 按修改时间排序（旧的在前）
            all_files.sort(key=lambda x: x[0])
            
            # 如果总文件数量超过限制，删除最旧的文件
            if len(all_files) >= max_size:
                files_to_delete = len(all_files) - max_size + 1  # +1表示达到限制时也删除
                for _, file_path in all_files[:files_to_delete]:
                    try:
                        os.remove(file_path)
                        logger.debug(f"全局缓存清理: 删除旧文件 {os.path.basename(file_path)} 来自 {os.path.dirname(file_path)}")
                    except Exception as e:
                        logger.debug(f"删除文件失败 {file_path}: {e}")
        except Exception as e:
            logger.error(f"全局缓存清理失败: {e}")
    
    @staticmethod
    def bytes_to_temp_file(img_bytes: bytes) -> str:
        """将字节流转换为临时文件并返回路径
        在保存前先检查并清理全局缓存
        """
        # 先清理全局缓存（控制两个目录的总数量）
        SymmetryUtils.cleanup_global_cache()
        
        # 使用before目录保存原始图片
        before_dir = SymmetryUtils.get_before_cache_dir()
        
        # 生成唯一的文件名（仅使用内容的哈希值）
        temp_path = os.path.join(before_dir, f"{hashlib.md5(img_bytes).hexdigest()}.jpg")
        
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
    
    @staticmethod
    def save_processed_image(image_hash: str, direction: str, processed_bytes: bytes) -> str:
        """保存处理后的图片到after目录，并自动清理全局缓存
        
        Args:
            image_hash: 图片的哈希标识符
            direction: 处理方向
            processed_bytes: 处理后的图片字节数据
            
        Returns:
            保存后的文件路径
        """
        # 先清理全局缓存（控制两个目录的总数量）
        SymmetryUtils.cleanup_global_cache()
        
        after_dir = SymmetryUtils.get_after_cache_dir()
        output_filename = f"{image_hash}_{direction}.jpg"
        output_path = os.path.join(after_dir, output_filename)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(processed_bytes)
            return output_path
        except Exception as e:
            logger.error(f"保存处理后图片失败: {e}")
            return None
