import io
from typing import Optional, List, Tuple
from PIL import Image, ImageSequence
from nonebot.log import logger


def _process_single_frame(img: Image.Image, direction: str) -> Image.Image:
    """处理单帧图像，执行指定方向的对称变换，正确处理透明度和图像模式
    
    Args:
        img: 需要处理的PIL图像对象
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
    
    Returns:
        处理后的PIL图像对象
    """
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


def _save_processed_gif(frames: List[Image.Image], durations: List[int], original_img: Image.Image) -> io.BytesIO:
    """保存处理后的GIF动画，确保透明度正确处理和动画效果
    
    Args:
        frames: 处理后的帧列表
        durations: 每帧的延迟时间列表（毫秒）
        original_img: 原始GIF图像对象，用于获取透明度信息
    
    Returns:
        包含GIF动画字节数据的BytesIO对象
    """
    img_byte_arr = io.BytesIO()
    
    # 确保所有帧都是相同的模式（RGBA）以保证透明度一致性
    processed_frames = []
    for frame in frames:
        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')
        processed_frames.append(frame)
    
    # 准备GIF保存参数
    gif_params = {
        'format': 'GIF',
        'append_images': processed_frames[1:],  # 除第一帧外的所有帧作为追加图像
        'save_all': True,  # 保存所有帧
        'duration': durations,  # 每帧的延迟时间
        'loop': 0,  # 0表示无限循环
        'disposal': 2,  # 帧处置方法，2表示恢复背景
        'optimize': False  # 不优化，确保最佳兼容性
    }
    
    # 只在原始图像有透明色信息时添加transparency参数
    if hasattr(original_img, 'info') and 'transparency' in original_img.info:
        gif_params['transparency'] = original_img.info['transparency']
    
    # 保存GIF动画
    processed_frames[0].save(img_byte_arr, **gif_params)
    return img_byte_arr


def _process_image_symmetric(image_path: str, direction: str, image_type: str = None) -> Optional[bytes]:
    """通用图像对称处理函数，根据图像类型（静态或GIF动画）进行不同处理
    
    Args:
        image_path: 图像文件路径
        direction: 对称方向，可选值为'left'、'right'、'top'、'bottom'
        image_type: 图像类型，可选参数，用于判断是否为GIF
    
    Returns:
        处理后的图像字节数据，如果处理失败返回None
    """
    try:
        # 打开图像文件
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
        logger.debug(f"{direction}方向对称处理失败: {e}")
        return None


def process_image_symmetric_left(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将左半部分镜像覆盖到右半部分
    
    Args:
        image_path: 图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节数据，如果处理失败返回None
    """
    return _process_image_symmetric(image_path, "left", image_type)


def process_image_symmetric_right(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将右半部分镜像覆盖到左半部分
    
    Args:
        image_path: 图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节数据，如果处理失败返回None
    """
    return _process_image_symmetric(image_path, "right", image_type)


def process_image_symmetric_top(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将上半部分镜像覆盖到下半部分
    
    Args:
        image_path: 图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节数据，如果处理失败返回None
    """
    return _process_image_symmetric(image_path, "top", image_type)


def process_image_symmetric_bottom(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将下半部分镜像覆盖到上半部分
    
    Args:
        image_path: 图像文件路径
        image_type: 图像类型，可选参数
    
    Returns:
        处理后的图像字节数据，如果处理失败返回None
    """
    return _process_image_symmetric(image_path, "bottom", image_type)