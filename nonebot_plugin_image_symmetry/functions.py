import io
import os
import hashlib
from typing import Optional, List, Tuple, Union
from PIL import Image, ImageSequence
from nonebot.log import logger

from .utils import SymmetryUtils


def _process_single_frame(img: Image.Image, direction: str) -> Image.Image:
    """处理单帧图像，执行指定方向的对称变换，正确处理透明度和图像模式
    
    Args:
        img: 需要处理的PIL图像对象
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
    
    Returns:
        处理后的PIL图像对象
    """
    try:
        # 统一转换为RGBA模式以正确处理透明度
        img_rgba = img.convert('RGBA')
        
        # 获取图片尺寸
        width, height = img_rgba.size
        
        # 创建透明背景的新图像作为结果容器
        result_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        if direction == "left":
            # 计算水平对称轴位置
            mid_point = width // 2
            
            # 裁剪左半部分
            left_half = img_rgba.crop((0, 0, mid_point, height))
            
            # 水平翻转左半部分，准备镜像效果
            mirrored_left = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            
            # 粘贴左半部分，对于RGBA图像，使用其alpha通道作为遮罩以保留透明度
            result_img.paste(left_half, (0, 0), left_half)
            
            # 粘贴镜像后的左半部分到右半部分，实现左侧对称效果
            result_img.paste(mirrored_left, (mid_point, 0), mirrored_left)
        elif direction == "right":
            # 计算水平对称轴位置
            mid_point = width // 2
            
            # 裁剪右半部分
            right_half = img_rgba.crop((mid_point, 0, width, height))
            
            # 水平翻转右半部分，准备镜像效果
            mirrored_right = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            
            # 粘贴右半部分，使用其alpha通道作为遮罩
            result_img.paste(right_half, (mid_point, 0), right_half)
            
            # 粘贴镜像后的右半部分到左半部分，实现右侧对称效果
            result_img.paste(mirrored_right, (0, 0), mirrored_right)
        elif direction == "top":
            # 计算垂直对称轴位置
            mid_point = height // 2
            
            # 裁剪上半部分
            top_half = img_rgba.crop((0, 0, width, mid_point))
            
            # 垂直翻转上半部分，准备镜像效果
            mirrored_top = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            
            # 粘贴上半部分，使用其alpha通道作为遮罩
            result_img.paste(top_half, (0, 0), top_half)
            
            # 粘贴镜像后的上半部分到下半部分，实现上方对称效果
            result_img.paste(mirrored_top, (0, mid_point), mirrored_top)
        elif direction == "bottom":
            # 计算垂直对称轴位置
            mid_point = height // 2
            
            # 裁剪下半部分
            bottom_half = img_rgba.crop((0, mid_point, width, height))
            
            # 垂直翻转下半部分，准备镜像效果
            mirrored_bottom = bottom_half.transpose(Image.FLIP_TOP_BOTTOM)
            
            # 粘贴下半部分，使用其alpha通道作为遮罩
            result_img.paste(bottom_half, (0, mid_point), bottom_half)
            
            # 粘贴镜像后的下半部分到上半部分，实现下方对称效果
            result_img.paste(mirrored_bottom, (0, 0), mirrored_bottom)
        else:
            logger.warning(f"不支持的对称方向: {direction}，使用原图")
            return img.copy()
        
        # 如果原图不是RGBA模式，转换回原图模式以保持格式一致性
        if img.mode != 'RGBA':
            # 对于P模式（调色板模式）或其他模式，使用白色背景处理透明度
            if img.mode == 'P':
                # 创建白色背景
                background = Image.new('RGB', result_img.size, (255, 255, 255))
                # 粘贴RGBA图像到白色背景上，使用alpha通道作为遮罩
                background.paste(result_img, mask=result_img.split()[3])
                return background.convert(img.mode)
            else:
                # 其他模式直接转换
                return result_img.convert(img.mode)
        
        return result_img
    except Exception as e:
        logger.error(f"处理图像帧对称变换失败: {type(e).__name__}: {e}")
        # 如果处理失败，返回原图的副本
        return img.copy()
    finally:
        # 确保所有临时图像资源被释放
        if 'img_rgba' in locals():
            img_rgba.close()
        if 'result_img' in locals():
            # 检查result_img是否是最终返回的图像，如果不是则关闭
            if 'result' in locals() and result_img is not result:
                result_img.close()
        # 关闭裁剪的临时图像
        for temp_img_name in ['left_half', 'mirrored_left', 'right_half', 'mirrored_right', 
                             'top_half', 'mirrored_top', 'bottom_half', 'mirrored_bottom']:
            if temp_img_name in locals():
                locals()[temp_img_name].close()


def _process_gif_frames(img: Image.Image, direction: str) -> Tuple[List[Image.Image], List[int]]:
    """处理GIF动画的所有帧并提取延迟信息
    
    Args:
        img: GIF动画的PIL图像对象
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
    
    Returns:
        一个元组，包含处理后的帧列表和每帧的延迟时间列表（毫秒）
    """
    frames = []
    durations = []
    
    # 遍历GIF的每一帧
    for frame in ImageSequence.Iterator(img):
        # 对每一帧执行指定方向的对称处理
        processed_frame = _process_single_frame(frame, direction)
        frames.append(processed_frame)
        
        # 获取帧延迟时间，如果没有则使用默认值100ms
        durations.append(frame.info.get('duration', 100))
    
    return frames, durations


# _save_processed_gif函数已被_save_gif_frames_to_bytes替代，保持兼容性


def _save_gif_frames_to_bytes(frames: List[Image.Image], durations: List[int], original_img: Image.Image) -> io.BytesIO:
    """将处理后的GIF帧保存到BytesIO对象中
    
    Args:
        frames: 处理后的帧列表
        durations: 每帧的延迟时间列表（毫秒）
        original_img: 原始GIF图像对象，用于获取透明度信息
    
    Returns:
        包含GIF动画字节数据的BytesIO对象
    """
    output_stream = io.BytesIO()
    
    # 确保所有帧都是相同的模式（RGBA）以保证透明度一致性
    processed_frames = []
    for frame in frames:
        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')
        processed_frames.append(frame)
    
    # 准备GIF保存参数
    gif_params = {
        'format': 'GIF',
        'append_images': processed_frames[1:],
        'save_all': True,
        'duration': durations,
        'loop': 0,
        'disposal': 2,
        'optimize': False
    }
    
    # 只在原始图像有透明色信息时添加transparency参数
    if hasattr(original_img, 'info') and 'transparency' in original_img.info:
        gif_params['transparency'] = original_img.info['transparency']
    
    # 保存GIF动画
    processed_frames[0].save(output_stream, **gif_params)
    return output_stream

def _process_image_symmetric_from_bytes(img_bytes: bytes, direction: str, image_type: Optional[str] = None) -> Optional[bytes]:
    """从字节数据处理图像对称变换（无缓存模式）
    
    Args:
        img_bytes: 输入图像字节数据
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
        image_type: 图像类型，如果为None则自动识别
    
    Returns:
        处理后图像的字节数据，如果处理失败返回None
    """
    try:
        logger.debug(f"开始无缓存模式图像处理，方向: {direction}")
        
        # 创建BytesIO对象
        img_io = io.BytesIO(img_bytes)
        
        # 将字节数据转换为图像对象
        try:
            img = SymmetryUtils.bytes_to_image(img_bytes)
            if img is None:
                logger.error("无法将字节数据转换为图像")
                return None
        except Exception as e:
            logger.error(f"创建图像对象失败: {type(e).__name__}: {e}")
            return None
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            try:
                # 处理GIF动画的所有帧
                frames, durations = _process_gif_frames(img, direction)
                
                # 保存处理后的GIF到BytesIO
                output_stream = _save_gif_frames_to_bytes(frames, durations, img)
                result = output_stream.getvalue()
                return result
            except Exception as e:
                logger.error(f"处理GIF动画失败: {type(e).__name__}: {e}")
                return None
        else:
            try:
                # 处理静态图像
                result_img = _process_single_frame(img, direction)
                
                # 转换回字节数据
                result = SymmetryUtils.image_to_bytes(result_img, image_type)
                
                # 关闭图像以释放资源
                result_img.close()
                return result
            except Exception as e:
                logger.error(f"处理静态图像失败: {type(e).__name__}: {e}")
                # 确保资源被释放
                try:
                    if 'result_img' in locals():
                        result_img.close()
                except:
                    pass
                return None
    except Exception as e:
        logger.error(f"从字节数据处理图像对称变换失败: {e}")
        return None
    finally:
        # 确保资源被释放
        try:
            if 'img_io' in locals():
                img_io.close()
        except:
            pass
        try:
            if 'img' in locals():
                img.close()
        except:
            pass


def _process_image_symmetric(image_path: str, direction: str, img_bytes: Optional[bytes] = None, image_type: Optional[str] = None) -> Tuple[Union[str, bytes, None], bool]:
    """通用图像对称处理函数，支持缓存和无缓存两种模式
    
    Args:
        image_path: 图像文件路径（缓存模式使用）
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
        img_bytes: 输入图像字节数据（无缓存模式使用）
        image_type: 图像类型
    
    Returns:
        一个元组，包含处理后的图像字节数据或文件路径，以及是否为字节数据的标志
    """
    # 无缓存模式
    if SymmetryUtils.is_cacheless_mode() and img_bytes:
        logger.debug(f"无缓存模式处理图像对称: {direction}")
        processed_bytes = _process_image_symmetric_from_bytes(img_bytes, direction, image_type)
        return processed_bytes, True
    
    # 缓存模式
    try:
        logger.debug(f"开始缓存模式图像处理，方向: {direction}")
        
        # 打开图像文件
        try:
            img = Image.open(image_path)
        except Exception as e:
            logger.error(f"打开图像失败: {type(e).__name__}: {e}")
            return None, False
        
        # 生成唯一标识符（基于原始文件路径）
        image_hash = hashlib.md5(image_path.encode()).hexdigest()
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            try:
                # 处理GIF动画的所有帧
                frames, durations = _process_gif_frames(img, direction)
                
                # 创建临时输出路径
                output_path = os.path.join(SymmetryUtils.get_after_cache_dir(), f"{image_hash}_{direction}.gif")
                
                # 确保目录存在
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # 使用统一的GIF保存函数
                gif_bytesio = _save_gif_frames_to_bytes(frames, durations, img)
                
                # 将BytesIO内容写入文件
                with open(output_path, 'wb') as f:
                    f.write(gif_bytesio.getvalue())
                return output_path, False
            except Exception as e:
                logger.error(f"处理GIF动画失败: {type(e).__name__}: {e}")
                return None, False
        else:
            # 处理静态图片
            result_img = _process_single_frame(img, direction)
            
            # 获取原始图片格式，保持格式一致性
            original_format = img.format if img.format else 'PNG'
            
            # 创建临时输出路径
            output_path = os.path.join(SymmetryUtils.get_after_cache_dir(), f"{image_hash}_{direction}.{original_format.lower()}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 对于JPEG和其他非透明格式，需要确保没有透明度通道或正确处理
            if original_format.upper() == 'JPEG' and result_img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', result_img.size, (255, 255, 255))
                # 粘贴RGBA图像到白色背景上
                background.paste(result_img, mask=result_img.split()[3])  # 使用alpha通道作为遮罩
                result_img = background
            
            # 保留图像的EXIF信息，特别是方向信息
            exif = img.info.get('exif')
            if exif:
                result_img.save(output_path, format=original_format, exif=exif)
            else:
                result_img.save(output_path, format=original_format)
                
            return output_path, False
    except Exception as e:
        logger.debug(f"{direction}方向对称处理失败: {e}")
        return None, False


def process_image_symmetric_left(image_path: str, img_bytes: Optional[bytes] = None, image_type: Optional[str] = None) -> Tuple[Union[str, bytes, None], bool]:
    """处理图片，将左半部分镜像覆盖到右半部分
    
    Args:
        image_path: 图像文件路径（缓存模式使用）
        img_bytes: 输入图像字节数据（无缓存模式使用）
        image_type: 图像类型，可选参数
    
    Returns:
        一个元组，包含处理后的图像字节数据或文件路径，以及是否为字节数据的标志
    """
    return _process_image_symmetric(image_path, "left", img_bytes, image_type)


def process_image_symmetric_right(image_path: str, img_bytes: Optional[bytes] = None, image_type: Optional[str] = None) -> Tuple[Union[str, bytes, None], bool]:
    """处理图片，将右半部分镜像覆盖到左半部分
    
    Args:
        image_path: 图像文件路径（缓存模式使用）
        img_bytes: 输入图像字节数据（无缓存模式使用）
        image_type: 图像类型，可选参数
    
    Returns:
        一个元组，包含处理后的图像字节数据或文件路径，以及是否为字节数据的标志
    """
    return _process_image_symmetric(image_path, "right", img_bytes, image_type)


def process_image_symmetric_top(image_path: str, img_bytes: Optional[bytes] = None, image_type: Optional[str] = None) -> Tuple[Union[str, bytes, None], bool]:
    """处理图片，将上半部分镜像覆盖到下半部分
    
    Args:
        image_path: 图像文件路径（缓存模式使用）
        img_bytes: 输入图像字节数据（无缓存模式使用）
        image_type: 图像类型，可选参数
    
    Returns:
        一个元组，包含处理后的图像字节数据或文件路径，以及是否为字节数据的标志
    """
    return _process_image_symmetric(image_path, "top", img_bytes, image_type)


def process_image_symmetric_bottom(image_path: str, img_bytes: Optional[bytes] = None, image_type: Optional[str] = None) -> Tuple[Union[str, bytes, None], bool]:
    """处理图片，将下半部分镜像覆盖到上半部分
    
    Args:
        image_path: 图像文件路径（缓存模式使用）
        img_bytes: 输入图像字节数据（无缓存模式使用）
        image_type: 图像类型，可选参数
    
    Returns:
        一个元组，包含处理后的图像字节数据或文件路径，以及是否为字节数据的标志
    """
    return _process_image_symmetric(image_path, "bottom", img_bytes, image_type)