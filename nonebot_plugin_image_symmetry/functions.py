import io
from typing import Optional, List, Tuple
from PIL import Image, ImageSequence
from nonebot.log import logger


def _process_single_frame(img: Image.Image, direction: str) -> Image.Image:
    """处理单帧图像，正确处理透明度和图像模式"""
    # 统一转换为RGBA模式以正确处理透明度
    img_rgba = img.convert('RGBA')
    
    # 获取图片尺寸
    width, height = img_rgba.size
    
    # 创建透明背景的新图像
    result_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    if direction == "left":
        # 计算中间线
        mid_point = width // 2
        
        # 裁剪左半部分
        left_half = img_rgba.crop((0, 0, mid_point, height))
        
        # 水平翻转左半部分
        mirrored_left = left_half.transpose(Image.FLIP_LEFT_RIGHT)
        
        # 粘贴左半部分，对于RGBA图像，使用其alpha通道作为遮罩
        result_img.paste(left_half, (0, 0), left_half)
        
        # 粘贴镜像后的左半部分到右半部分，并使用其alpha通道作为遮罩
        result_img.paste(mirrored_left, (mid_point, 0), mirrored_left)
    elif direction == "right":
        # 计算中间线
        mid_point = width // 2
        
        # 裁剪右半部分
        right_half = img_rgba.crop((mid_point, 0, width, height))
        
        # 水平翻转右半部分
        mirrored_right = right_half.transpose(Image.FLIP_LEFT_RIGHT)
        
        # 粘贴右半部分，使用其alpha通道作为遮罩
        result_img.paste(right_half, (mid_point, 0), right_half)
        
        # 粘贴镜像后的右半部分到左半部分，使用其alpha通道作为遮罩
        result_img.paste(mirrored_right, (0, 0), mirrored_right)
    elif direction == "top":
        # 计算中间线
        mid_point = height // 2
        
        # 裁剪上半部分
        top_half = img_rgba.crop((0, 0, width, mid_point))
        
        # 垂直翻转上半部分
        mirrored_top = top_half.transpose(Image.FLIP_TOP_BOTTOM)
        
        # 粘贴上半部分，使用其alpha通道作为遮罩
        result_img.paste(top_half, (0, 0), top_half)
        
        # 粘贴镜像后的上半部分到下半部分，使用其alpha通道作为遮罩
        result_img.paste(mirrored_top, (0, mid_point), mirrored_top)
    elif direction == "bottom":
        # 计算中间线
        mid_point = height // 2
        
        # 裁剪下半部分
        bottom_half = img_rgba.crop((0, mid_point, width, height))
        
        # 垂直翻转下半部分
        mirrored_bottom = bottom_half.transpose(Image.FLIP_TOP_BOTTOM)
        
        # 粘贴下半部分，使用其alpha通道作为遮罩
        result_img.paste(bottom_half, (0, mid_point), bottom_half)
        
        # 粘贴镜像后的下半部分到上半部分，使用其alpha通道作为遮罩
        result_img.paste(mirrored_bottom, (0, 0), mirrored_bottom)
    
    # 如果原图不是RGBA模式，转换回原图模式
    if img.mode != 'RGBA':
        # 对于P模式或其他模式，使用白色背景
        if img.mode == 'P':
            # 创建白色背景
            background = Image.new('RGB', result_img.size, (255, 255, 255))
            # 粘贴RGBA图像到白色背景上
            background.paste(result_img, mask=result_img.split()[3])  # 使用alpha通道作为遮罩
            return background.convert(img.mode)
        else:
            # 其他模式直接转换
            return result_img.convert(img.mode)
    
    return result_img


def _process_gif_frames(img: Image.Image, direction: str) -> Tuple[List[Image.Image], List[int]]:
    """处理GIF动画的所有帧并提取延迟信息"""
    frames = []
    durations = []
    
    for frame in ImageSequence.Iterator(img):
        # 处理每一帧
        processed_frame = _process_single_frame(frame, direction)
        frames.append(processed_frame)
        # 获取帧延迟
        durations.append(frame.info.get('duration', 100))  # 使用默认值100ms
    
    return frames, durations


def _save_processed_gif(frames: List[Image.Image], durations: List[int], original_img: Image.Image) -> io.BytesIO:
    """保存处理后的GIF动画，确保透明度正确处理"""
    img_byte_arr = io.BytesIO()
    
    # 确保所有帧都是相同的模式（RGBA）
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
        # 不再强制设置transparency=None，让PIL根据原始信息处理
        gif_params['transparency'] = original_img.info['transparency']
    
    # 保存GIF
    processed_frames[0].save(img_byte_arr, **gif_params)
    return img_byte_arr


def _process_image_symmetric(image_path: str, direction: str, image_type: str = None) -> Optional[bytes]:
    """通用图像对称处理函数"""
    try:
        img = Image.open(image_path)
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            # 处理GIF动画的所有帧
            frames, durations = _process_gif_frames(img, direction)
            
            # 保存处理后的GIF
            img_byte_arr = _save_processed_gif(frames, durations, img)
            return img_byte_arr.getvalue()
        else:
            # 处理静态图片
            result_img = _process_single_frame(img, direction)
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            
            # 获取原始图片格式，保持格式一致性
            original_format = img.format if img.format else 'PNG'
            
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
                result_img.save(img_byte_arr, format=original_format, exif=exif)
            else:
                result_img.save(img_byte_arr, format=original_format)
                
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称{direction}处理失败: {e}")
        return None


def process_image_symmetric_left(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将左半部分镜像覆盖到右半部分"""
    return _process_image_symmetric(image_path, "left", image_type)


def process_image_symmetric_right(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将右半部分镜像覆盖到左半部分"""
    return _process_image_symmetric(image_path, "right", image_type)


def process_image_symmetric_top(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将上半部分镜像覆盖到下半部分"""
    return _process_image_symmetric(image_path, "top", image_type)


def process_image_symmetric_bottom(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将下半部分镜像覆盖到上半部分"""
    return _process_image_symmetric(image_path, "bottom", image_type)