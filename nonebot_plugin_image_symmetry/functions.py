import io
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
    img_rgba = None
    result_img = None
    try:
        img_rgba = img.convert('RGBA')
        width, height = img_rgba.size
        result_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        if direction == "left":
            mid_point = width // 2
            left_half = img_rgba.crop((0, 0, mid_point, height))
            mirrored_left = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            result_img.paste(left_half, (0, 0), left_half)
            result_img.paste(mirrored_left, (mid_point, 0), mirrored_left)
        elif direction == "right":
            mid_point = width // 2
            right_half = img_rgba.crop((mid_point, 0, width, height))
            mirrored_right = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            result_img.paste(right_half, (mid_point, 0), right_half)
            result_img.paste(mirrored_right, (0, 0), mirrored_right)
        elif direction == "top":
            mid_point = height // 2
            top_half = img_rgba.crop((0, 0, width, mid_point))
            mirrored_top = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            result_img.paste(top_half, (0, 0), top_half)
            result_img.paste(mirrored_top, (0, mid_point), mirrored_top)
        elif direction == "bottom":
            mid_point = height // 2
            bottom_half = img_rgba.crop((0, mid_point, width, height))
            mirrored_bottom = bottom_half.transpose(Image.FLIP_TOP_BOTTOM)
            result_img.paste(bottom_half, (0, mid_point), bottom_half)
            result_img.paste(mirrored_bottom, (0, 0), mirrored_bottom)
        else:
            logger.warning(f"不支持的对称方向: {direction}，使用原图")
            final_result = img.copy()
            return final_result
        
        if img.mode != 'RGBA':
            if img.mode == 'P':
                background = Image.new('RGB', result_img.size, (255, 255, 255))
                background.paste(result_img, mask=result_img.split()[3])
                final_result = background.convert(img.mode)
                return final_result
            else:
                final_result = result_img.convert(img.mode)
                return final_result
        
        final_result = result_img
        return final_result
    except Exception as e:
        logger.exception(f"处理图像帧对称变换失败: {type(e).__name__}: {e}")
        return img.copy()


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
    
    for frame_num, frame in enumerate(ImageSequence.Iterator(img)):
        processed_frame = _process_single_frame(frame, direction)
        frames.append(processed_frame)
        durations.append(frame.info.get('duration', 100))
        if frame_num == 0:
            frame.close()
    
    return frames, durations


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
    """从字节数据处理图像对称变换
    
    Args:
        img_bytes: 输入图像字节数据
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
        image_type: 图像类型，如果为None则自动识别
    
    Returns:
        处理后图像的字节数据，如果处理失败返回None
    """
    if not img_bytes:
        logger.error("输入图像字节数据为空")
        return None
    
    if not direction:
        logger.error("对称方向参数为空")
        return None
    try:
        logger.debug(f"开始图像处理，方向: {direction}")
        
        # 创建BytesIO对象
        img_io = io.BytesIO(img_bytes)
        
        # 将字节数据转换为图像对象
        try:
            img = SymmetryUtils.bytes_to_image(img_bytes)
            if img is None:
                logger.error("无法将字节数据转换为图像")
                return None
        except Exception:
            logger.exception("创建图像对象失败")
            return None
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            try:
                frames, durations = _process_gif_frames(img, direction)
                output_stream = _save_gif_frames_to_bytes(frames, durations, img)
                result = output_stream.getvalue()
                return result
            except Exception:
                logger.exception("处理GIF动画失败")
                return None
        else:
            try:
                result_img = _process_single_frame(img, direction)
                result = SymmetryUtils.image_to_bytes(result_img, image_type)
                result_img.close()
                return result
            except Exception:
                logger.exception("处理静态图像失败")
                return None
    except Exception:
        logger.exception("从字节数据处理图像对称变换失败")
        return None
    finally:
        try:
            if 'img_io' in locals():
                img_io.close()
        except Exception:
            pass
        try:
            if 'img' in locals():
                img.close()
        except Exception:
            pass


def symmetric_left(img_bytes: bytes, image_type: Optional[str] = None) -> Optional[bytes]:
    """图像左侧对称处理
    
    Args:
        img_bytes: 输入图像字节数据
        image_type: 图像类型
    
    Returns:
        处理后的图像字节数据
    """
    logger.debug("处理图像左侧对称")
    return _process_image_symmetric_from_bytes(img_bytes, "left", image_type)


def symmetric_right(img_bytes: bytes, image_type: Optional[str] = None) -> Optional[bytes]:
    """图像右侧对称处理
    
    Args:
        img_bytes: 输入图像字节数据
        image_type: 图像类型
    
    Returns:
        处理后的图像字节数据
    """
    logger.debug("处理图像右侧对称")
    return _process_image_symmetric_from_bytes(img_bytes, "right", image_type)


def symmetric_top(img_bytes: bytes, image_type: Optional[str] = None) -> Optional[bytes]:
    """图像顶部对称处理
    
    Args:
        img_bytes: 输入图像字节数据
        image_type: 图像类型
    
    Returns:
        处理后的图像字节数据
    """
    logger.debug("处理图像顶部对称")
    return _process_image_symmetric_from_bytes(img_bytes, "top", image_type)


def symmetric_bottom(img_bytes: bytes, image_type: Optional[str] = None) -> Optional[bytes]:
    """图像底部对称处理
    
    Args:
        img_bytes: 输入图像字节数据
        image_type: 图像类型
    
    Returns:
        处理后的图像字节数据
    """
    logger.debug("处理图像底部对称")
    return _process_image_symmetric_from_bytes(img_bytes, "bottom", image_type)