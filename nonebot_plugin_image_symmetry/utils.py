import io
from PIL import Image
from nonebot import get_driver
from nonebot.log import logger

# 获取NoneBot驱动实例，用于读取配置
driver = get_driver()

class SymmetryUtils:
    """对称处理工具类，提供图像处理相关的工具方法"""
    
    # 无缓存模式始终启用
    CACHELESS_MODE = True
    
    @staticmethod
    def is_cacheless_mode() -> bool:
        """检查是否启用无缓存模式
        
        Returns:
            bool: True表示启用无缓存模式
        """
        return True
    
    @staticmethod
    def initialize_directories() -> None:
        """初始化所有必要的目录结构，无缓存模式下不需要初始化目录"""
        logger.info("已启用无缓存模式，跳过目录初始化")
    
    @staticmethod
    def cleanup_global_cache(max_size: int = None) -> None:
        """清理全局缓存，无缓存模式下不需要执行缓存清理"""
        logger.debug("无缓存模式: 跳过缓存清理")
    @staticmethod
    def identify_image_type(img_bytes: bytes) -> str:
        """识别图像类型
        
        Args:
            img_bytes: 图像字节数据
            
        Returns:
            图像类型字符串，如'jpg', 'png', 'gif'等，如果无法识别则返回'unknown'
        """
        try:
            with Image.open(io.BytesIO(img_bytes)) as img:
                # 获取图像格式
                format_type = img.format.lower() if img.format else None
                # 检查是否为GIF动画
                if format_type == 'gif' and getattr(img, 'is_animated', False):
                    return 'gif_animated'
                return format_type
        except Exception as e:
            logger.debug(f"PIL识别图像格式失败: {e}")
            return 'unknown'
    
    @staticmethod
    def bytes_to_temp_file(img_bytes: bytes) -> tuple:
        """将字节流转换为临时文件并返回路径和图像类型
        
        Args:
            img_bytes: 图像字节数据
            
        Returns:
            tuple: (临时文件路径, 图像类型)，无缓存模式下返回(None, 图像类型)
        """
        # 识别图像类型
        image_type = SymmetryUtils.identify_image_type(img_bytes)
        logger.debug(f"识别到的图像类型: {image_type}")
        
        # 无缓存模式下，直接返回None路径和识别到的类型
        logger.debug("无缓存模式: 跳过临时文件保存")
        return None, image_type
    
    @staticmethod
    def bytes_to_image(img_bytes: bytes) -> Image.Image:
        """将字节数据转换为PIL图像对象
        
        Args:
            img_bytes: 图像字节数据
            
        Returns:
            Image.Image: PIL图像对象，如果转换失败则返回None
        """
        try:
            img_stream = io.BytesIO(img_bytes)
            img = Image.open(img_stream)
            return img
        except Exception as e:
            logger.error(f"字节数据转换为图像失败: {e}")
            return None
    
    @staticmethod
    def image_to_bytes(img: Image.Image, image_type: str = None) -> bytes:
        """将PIL图像对象转换为字节数据
        
        Args:
            img: PIL图像对象
            image_type: 图像类型，如果为None则使用图像原始格式
            
        Returns:
            bytes: 图像字节数据，如果转换失败则返回None
        """
        try:
            img_stream = io.BytesIO()
            
            # 确定保存格式
            format = image_type.upper() if image_type else img.format or 'PNG'
            
            # 对于JPEG和其他非透明格式，需要确保没有透明度通道
            if format == 'JPEG' and img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                # 粘贴RGBA图像到白色背景上
                background.paste(img, mask=img.split()[3])  # 使用alpha通道作为遮罩
                img = background
                
            # 保留图像的EXIF信息
            exif = img.info.get('exif')
            if exif:
                img.save(img_stream, format=format, exif=exif)
            else:
                img.save(img_stream, format=format)
            
            img_bytes = img_stream.getvalue()
            return img_bytes
        except Exception as e:
            logger.error(f"图像转换为字节数据失败: {e}")
            return None
