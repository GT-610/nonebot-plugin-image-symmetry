import io
from typing import Optional
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

def process_image_symmetric_left(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将左半部分镜像覆盖到右半部分"""
    try:
        img = Image.open(image_path)
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            # 处理GIF动画
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(img):
                # 处理每一帧，不再需要预先转换为RGBA，_process_single_frame内部会处理
                processed_frame = _process_single_frame(frame, "left")
                frames.append(processed_frame)
                # 获取帧延迟
                if 'duration' in frame.info:
                    durations.append(frame.info['duration'])
                else:
                    durations.append(100)  # 默认延迟
            
            # 保存处理后的GIF
            img_byte_arr = io.BytesIO()
            
            # 确保所有帧都是相同的模式（RGBA）
            processed_frames = []
            for frame in frames:
                # 确保所有帧都是RGBA模式
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                processed_frames.append(frame)
            
            # 保存GIF时不使用固定的transparency=0，让PIL自动处理透明色
            # disposal设为2表示处理完当前帧后恢复到背景色
            processed_frames[0].save(
                img_byte_arr,
                format='GIF',
                append_images=processed_frames[1:],
                save_all=True,
                duration=durations,
                loop=0,
                disposal=2,
                optimize=False,
                # 移除固定的transparency参数，让PIL自动检测
                **({'transparency': None} if hasattr(img, 'info') and 'transparency' in img.info else {})
            )
            return img_byte_arr.getvalue()
        else:
            # 处理静态图片
            result_img = _process_single_frame(img, "left")
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称左处理失败: {e}")
        return None


def process_image_symmetric_right(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将右半部分镜像覆盖到左半部分"""
    try:
        img = Image.open(image_path)
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            # 处理GIF动画
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(img):
                # 处理每一帧，不再需要预先转换为RGBA，_process_single_frame内部会处理
                processed_frame = _process_single_frame(frame, "right")
                frames.append(processed_frame)
                # 获取帧延迟
                if 'duration' in frame.info:
                    durations.append(frame.info['duration'])
                else:
                    durations.append(100)  # 默认延迟
            
            # 保存处理后的GIF
            img_byte_arr = io.BytesIO()
            
            # 确保所有帧都是相同的模式（RGBA）
            processed_frames = []
            for frame in frames:
                # 确保所有帧都是RGBA模式
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                processed_frames.append(frame)
            
            # 保存GIF时不使用固定的transparency=0，让PIL自动处理透明色
            # disposal设为2表示处理完当前帧后恢复到背景色
            processed_frames[0].save(
                img_byte_arr,
                format='GIF',
                append_images=processed_frames[1:],
                save_all=True,
                duration=durations,
                loop=0,
                disposal=2,
                optimize=False,
                # 移除固定的transparency参数，让PIL自动检测
                **({'transparency': None} if hasattr(img, 'info') and 'transparency' in img.info else {})
            )
            return img_byte_arr.getvalue()
        else:
            # 处理静态图片
            result_img = _process_single_frame(img, "right")
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称右处理失败: {e}")
        return None


def process_image_symmetric_top(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将上半部分镜像覆盖到下半部分"""
    try:
        img = Image.open(image_path)
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            # 处理GIF动画
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(img):
                # 处理每一帧，不再需要预先转换为RGBA，_process_single_frame内部会处理
                processed_frame = _process_single_frame(frame, "top")
                frames.append(processed_frame)
                # 获取帧延迟
                if 'duration' in frame.info:
                    durations.append(frame.info['duration'])
                else:
                    durations.append(100)  # 默认延迟
            
            # 保存处理后的GIF
            img_byte_arr = io.BytesIO()
            
            # 确保所有帧都是相同的模式（RGBA）
            processed_frames = []
            for frame in frames:
                # 确保所有帧都是RGBA模式
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                processed_frames.append(frame)
            
            # 保存GIF时不使用固定的transparency=0，让PIL自动处理透明色
            # disposal设为2表示处理完当前帧后恢复到背景色
            processed_frames[0].save(
                img_byte_arr,
                format='GIF',
                append_images=processed_frames[1:],
                save_all=True,
                duration=durations,
                loop=0,
                disposal=2,
                optimize=False,
                # 移除固定的transparency参数，让PIL自动检测
                **({'transparency': None} if hasattr(img, 'info') and 'transparency' in img.info else {})
            )
            return img_byte_arr.getvalue()
        else:
            # 处理静态图片
            result_img = _process_single_frame(img, "top")
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称上处理失败: {e}")
        return None


def process_image_symmetric_bottom(image_path: str, image_type: str = None) -> Optional[bytes]:
    """处理图片，将下半部分镜像覆盖到上半部分"""
    try:
        img = Image.open(image_path)
        
        # 检查是否为GIF且为动画
        is_gif = image_type and image_type.startswith('gif') and hasattr(img, 'is_animated') and img.is_animated
        
        if is_gif:
            logger.debug(f"处理GIF动画，帧数: {img.n_frames}")
            # 处理GIF动画
            frames = []
            durations = []
            
            for frame in ImageSequence.Iterator(img):
                # 处理每一帧，不再需要预先转换为RGBA，_process_single_frame内部会处理
                processed_frame = _process_single_frame(frame, "bottom")
                frames.append(processed_frame)
                # 获取帧延迟
                if 'duration' in frame.info:
                    durations.append(frame.info['duration'])
                else:
                    durations.append(100)  # 默认延迟
            
            # 保存处理后的GIF
            img_byte_arr = io.BytesIO()
            
            # 确保所有帧都是相同的模式（RGBA）
            processed_frames = []
            for frame in frames:
                # 确保所有帧都是RGBA模式
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                processed_frames.append(frame)
            
            # 保存GIF时不使用固定的transparency=0，让PIL自动处理透明色
            # disposal设为2表示处理完当前帧后恢复到背景色
            processed_frames[0].save(
                img_byte_arr,
                format='GIF',
                append_images=processed_frames[1:],
                save_all=True,
                duration=durations,
                loop=0,
                disposal=2,
                optimize=False,
                # 移除固定的transparency参数，让PIL自动检测
                **({'transparency': None} if hasattr(img, 'info') and 'transparency' in img.info else {})
            )
            return img_byte_arr.getvalue()
        else:
            # 处理静态图片
            result_img = _process_single_frame(img, "bottom")
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称下处理失败: {e}")
        return None