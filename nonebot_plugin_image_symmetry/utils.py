import hashlib
import io
import os
from PIL import Image
from nonebot import get_driver
from nonebot_plugin_localstore import get_plugin_cache_dir
from nonebot.log import logger

# 获取NoneBot驱动实例，用于读取配置
driver = get_driver()

# 在模块级别先获取无缓存模式状态
def _get_cacheless_mode_module():
    """从NoneBot配置获取无缓存模式设置（模块级别）"""
    try:
        cacheless_value = getattr(driver.config, "image_symmetry_cacheless", "true")
        
        if isinstance(cacheless_value, bool):
            cacheless = cacheless_value
        else:
            cacheless = str(cacheless_value).lower() == "true"
        
        logger.debug(f"无缓存模式设置: {'启用' if cacheless else '禁用'} (从NoneBot配置获取)")
        return cacheless
    except Exception as e:
        logger.warning(f"获取无缓存模式配置失败: {e}，使用默认值False")
        logger.debug("无缓存模式设置: 禁用 (默认值)")
        return False

# 模块级别的无缓存模式状态
_CACHELESS_MODE_MODULE = _get_cacheless_mode_module()

# 在模块级别获取最大缓存数量
def _get_max_cache_size_module():
    """从NoneBot配置获取最大缓存数量（模块级别）"""
    # 在无缓存模式下，直接返回默认值而不读取配置
    if _CACHELESS_MODE_MODULE:
        logger.debug("无缓存模式已启用，跳过读取最大缓存图片数量")
        return 100
    
    try:
        max_size = getattr(driver.config, "image_symmetry_max_cache", 100)
        if 5 <= max_size <= 9999:
            logger.debug(f"使用最大缓存图片数量: {max_size} (从NoneBot配置获取)")
            return max_size
        else:
            logger.warning(f"配置image_symmetry_max_cache值{max_size}超出范围[5, 9999]，使用默认值100")
            logger.debug(f"使用最大缓存图片数量: 100 (默认值)")
            return 100
    except (ValueError, TypeError):
        logger.warning(f"配置image_symmetry_max_cache值无效，使用默认值100")
        logger.debug(f"使用最大缓存图片数量: 100 (默认值)")
        return 100

# 模块级别的最大缓存数量
_MAX_TOTAL_CACHE_SIZE_MODULE = _get_max_cache_size_module()


class SymmetryUtils:
    """对称处理工具类，提供图像缓存管理和文件操作相关的工具方法"""
    
    # 使用模块级变量作为类变量
    CACHELESS_MODE = _CACHELESS_MODE_MODULE
    
    # 无缓存模式开关，通过NoneBot配置控制，默认关闭
    @staticmethod
    def _get_cacheless_mode():
        """从NoneBot配置获取无缓存模式设置
        
        Returns:
            bool: True表示启用无缓存模式，False表示使用缓存模式
        """
        return _CACHELESS_MODE_MODULE
    
    # 从NoneBot配置获取最大缓存数量，默认为100，范围[5, 9999]
    @staticmethod
    def _get_max_cache_size():
        """从NoneBot配置获取最大缓存数量，并进行范围检查
        
        Returns:
            int: 有效的最大缓存数量，确保在[5, 9999]范围内
        """
        return _MAX_TOTAL_CACHE_SIZE_MODULE
    
    @staticmethod
    def is_cacheless_mode() -> bool:
        """检查是否启用无缓存模式
        
        Returns:
            bool: True表示启用无缓存模式，False表示使用缓存模式
        """
        return SymmetryUtils.CACHELESS_MODE
    
    @staticmethod
    def get_cache_dir() -> str:
        """获取插件的缓存根目录
        
        Returns:
            str: 缓存目录的绝对路径
        """
        cache_dir = get_plugin_cache_dir()
        os.makedirs(cache_dir, exist_ok=True)
        return str(cache_dir)
    
    @staticmethod
    def get_before_cache_dir() -> str:
        """获取原始图片缓存目录
        
        Returns:
            str: 原始图片缓存目录的绝对路径
        """
        try:
            cache_dir = SymmetryUtils.get_cache_dir()
            before_dir = os.path.join(cache_dir, "before")
            # 确保缓存目录存在
            os.makedirs(before_dir, exist_ok=True)
            return before_dir
        except Exception as e:
            logger.error(f"获取预处理缓存目录失败: {type(e).__name__}: {e}")
            # 失败时返回临时目录作为后备
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "image_symmetry_before")
            os.makedirs(temp_dir, exist_ok=True)
            logger.warning(f"使用临时目录作为后备: {temp_dir}")
            return temp_dir
    
    @staticmethod
    def get_after_cache_dir() -> str:
        """获取处理后图片缓存目录
        
        Returns:
            str: 处理后图片缓存目录的绝对路径
        """
        try:
            cache_dir = SymmetryUtils.get_cache_dir()
            after_dir = os.path.join(cache_dir, "after")
            # 确保缓存目录存在
            os.makedirs(after_dir, exist_ok=True)
            return after_dir
        except Exception as e:
            logger.error(f"获取后处理缓存目录失败: {type(e).__name__}: {e}")
            # 失败时返回临时目录作为后备
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), "image_symmetry_after")
            os.makedirs(temp_dir, exist_ok=True)
            logger.warning(f"使用临时目录作为后备: {temp_dir}")
            return temp_dir
    
    @staticmethod
    def initialize_directories() -> None:
        """初始化所有必要的目录结构，确保缓存目录存在"""
        # 只在非无缓存模式下初始化目录
        if not SymmetryUtils.is_cacheless_mode():
            try:
                before_dir = SymmetryUtils.get_before_cache_dir()
                after_dir = SymmetryUtils.get_after_cache_dir()
                logger.info(f"成功初始化目录结构\nbefore目录: {before_dir}\nafter目录: {after_dir}")
            except Exception as e:
                logger.error(f"初始化目录结构失败: {e}")
        else:
            logger.info("已启用无缓存模式，跳过目录初始化")
    
    @staticmethod
    def cleanup_global_cache(max_size: int = None) -> None:
        """清理全局缓存，控制两个目录（before和after）的总图片数量不超过限制
        
        Args:
            max_size: 两个目录总计的最大缓存文件数量，如不指定则使用配置值
        """
        try:
            if max_size is None:
                max_size = SymmetryUtils._get_max_cache_size()
            # 只在非无缓存模式下执行缓存清理
            if not SymmetryUtils.is_cacheless_mode():
                try:
                    # 获取两个目录的路径
                    before_dir = SymmetryUtils.get_before_cache_dir()
                    after_dir = SymmetryUtils.get_after_cache_dir()
                    
                    # 确保目录存在
                    os.makedirs(before_dir, exist_ok=True)
                    os.makedirs(after_dir, exist_ok=True)
                    
                    # 获取两个目录中所有的jpg文件及其修改时间
                    all_files = []
                    
                    # 检查before目录中的图片文件
                    if os.path.exists(before_dir):
                        for filename in os.listdir(before_dir):
                            if filename.lower().endswith('.jpg'):
                                file_path = os.path.join(before_dir, filename)
                                if os.path.isfile(file_path):
                                    try:
                                        mod_time = os.path.getmtime(file_path)
                                        all_files.append((mod_time, file_path))
                                    except (OSError, FileNotFoundError) as e:
                                        logger.warning(f"无法访问缓存文件 {file_path}: {e}")
                                        continue
                    
                    # 检查after目录中的图片文件
                    if os.path.exists(after_dir):
                        for filename in os.listdir(after_dir):
                            if filename.lower().endswith(('.jpg', '.png', '.gif')):
                                file_path = os.path.join(after_dir, filename)
                                if os.path.isfile(file_path):
                                    try:
                                        mod_time = os.path.getmtime(file_path)
                                        all_files.append((mod_time, file_path))
                                    except (OSError, FileNotFoundError) as e:
                                        logger.warning(f"无法访问缓存文件 {file_path}: {e}")
                                        continue
                    
                    # 按修改时间排序（旧的在前）
                    all_files.sort(key=lambda x: x[0])
                    
                    # 如果总文件数量超过限制，删除最旧的文件
                    if len(all_files) >= max_size:
                        files_to_delete = len(all_files) - max_size + 1  # +1表示达到限制时也删除
                        deleted_count = 0
                        for _, file_path in all_files[:files_to_delete]:
                            try:
                                os.remove(file_path)
                                logger.debug(f"全局缓存清理: 删除旧文件 {os.path.basename(file_path)} 来自 {os.path.dirname(file_path)}")
                                deleted_count += 1
                            except (OSError, FileNotFoundError) as e:
                                logger.warning(f"删除文件失败 {file_path}: {e}")
                                continue
                        
                        if deleted_count > 0:
                            logger.info(f"缓存清理完成: 删除了 {deleted_count} 个旧文件")
                except Exception as e:
                    logger.error(f"全局缓存清理失败: {type(e).__name__}: {e}")
        except Exception as e:
            logger.error(f"调用缓存清理方法时发生错误: {type(e).__name__}: {e}")
    
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
    def _prepare_for_caching() -> None:
        """准备缓存环境，执行缓存清理（仅在缓存模式下）"""
        if not SymmetryUtils.is_cacheless_mode():
            try:
                SymmetryUtils.cleanup_global_cache()
                logger.debug("缓存环境准备完成")
            except Exception as e:
                logger.warning(f"缓存准备过程中发生错误: {type(e).__name__}: {e}")
    
    @staticmethod
    def bytes_to_temp_file(img_bytes: bytes) -> tuple:
        """将字节流转换为临时文件并返回路径和图像类型
        
        Args:
            img_bytes: 图像字节数据
            
        Returns:
            tuple: (临时文件路径, 图像类型)，如果处理失败返回(None, None)
        """
        # 识别图像类型
        image_type = SymmetryUtils.identify_image_type(img_bytes)
        logger.debug(f"识别到的图像类型: {image_type}")
        
        # 在无缓存模式下，直接返回None路径和识别到的类型
        if SymmetryUtils.is_cacheless_mode():
            logger.debug("无缓存模式: 跳过临时文件保存")
            return None, image_type
        
        # 缓存模式下保存文件
        # 准备缓存环境
        SymmetryUtils._prepare_for_caching()
        
        # 使用before目录保存原始图片
        before_dir = SymmetryUtils.get_before_cache_dir()
        
        # 生成唯一的文件名（仅使用内容的哈希值）
        # 仍然使用.jpg扩展名以保持原有功能兼容性
        temp_path = os.path.join(before_dir, f"{hashlib.md5(img_bytes).hexdigest()}.jpg")
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(img_bytes)
            logger.debug(f"临时文件已保存: {os.path.basename(temp_path)}")
            return temp_path, image_type
        except Exception as e:
            logger.error(f"创建临时文件失败: {type(e).__name__}: {e}")
            return None, image_type  # 即使失败也返回识别到的类型
    
    @staticmethod
    def save_processed_image(image_hash: str, direction: str, processed_bytes: bytes, image_type: str = None) -> str:
        """保存处理后的图片到after目录，并自动清理全局缓存
        
        Args:
            image_hash: 图片的哈希标识符
            direction: 处理方向（left、right、top、bottom）
            processed_bytes: 处理后的图片字节数据
            image_type: 图像类型，用于确定保存格式
            
        Returns:
            str: 保存后的文件路径，如果保存失败返回None
        """
        # 在无缓存模式下，直接返回None路径
        if SymmetryUtils.is_cacheless_mode():
            logger.debug("无缓存模式: 跳过处理后文件保存")
            return None
        
        # 缓存模式下保存文件
        # 准备缓存环境
        SymmetryUtils._prepare_for_caching()
        
        after_dir = SymmetryUtils.get_after_cache_dir()
        
        # 根据图像类型确定文件扩展名
        if image_type and image_type.startswith('gif'):
            extension = '.gif'
        elif image_type == 'png':
            extension = '.png'
        elif image_type == 'jpg' or image_type == 'jpeg':
            extension = '.jpg'
        else:
            extension = '.jpg'  # 默认使用jpg
        
        # 生成唯一的输出文件名
        output_filename = f"{image_hash}_{direction}{extension}"
        output_path = os.path.join(after_dir, output_filename)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(processed_bytes)
            logger.debug(f"处理后图片已保存: {output_filename}")
            return output_path
        except Exception as e:
            logger.error(f"保存处理后图片失败: {type(e).__name__}: {e}")
            return None
    
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
