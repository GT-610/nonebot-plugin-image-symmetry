import io
from typing import Optional
from PIL import Image
from nonebot.log import logger


def process_image_symmetric_left(image_path: str) -> Optional[bytes]:
    """处理图片，将左半部分镜像覆盖到右半部分"""
    try:
        with Image.open(image_path) as img:
            # 获取图片尺寸
            width, height = img.size
            
            # 计算中间线
            mid_point = width // 2
            
            # 裁剪左半部分
            left_half = img.crop((0, 0, mid_point, height))
            
            # 水平翻转左半部分
            mirrored_left = left_half.transpose(Image.FLIP_LEFT_RIGHT)
            
            # 创建新图片（与原图片相同大小）
            result_img = Image.new('RGB', (width, height))
            
            # 粘贴左半部分
            result_img.paste(img, (0, 0))
            
            # 粘贴镜像后的左半部分到右半部分
            result_img.paste(mirrored_left, (mid_point, 0))
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称左处理失败: {e}")
        return None


def process_image_symmetric_right(image_path: str) -> Optional[bytes]:
    """处理图片，将右半部分镜像覆盖到左半部分"""
    try:
        with Image.open(image_path) as img:
            # 获取图片尺寸
            width, height = img.size
            
            # 计算中间线
            mid_point = width // 2
            
            # 裁剪右半部分
            right_half = img.crop((mid_point, 0, width, height))
            
            # 水平翻转右半部分
            mirrored_right = right_half.transpose(Image.FLIP_LEFT_RIGHT)
            
            # 创建新图片（与原图片相同大小）
            result_img = Image.new('RGB', (width, height))
            
            # 粘贴右半部分
            result_img.paste(img, (0, 0))
            
            # 粘贴镜像后的右半部分到左半部分
            result_img.paste(mirrored_right, (0, 0))
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称右处理失败: {e}")
        return None


def process_image_symmetric_top(image_path: str) -> Optional[bytes]:

    """处理图片，将上半部分镜像覆盖到下半部分"""
    try:
        with Image.open(image_path) as img:
            # 获取图片尺寸
            width, height = img.size
            
            # 计算中间线
            mid_point = height // 2
            
            # 裁剪上半部分
            top_half = img.crop((0, 0, width, mid_point))
            
            # 垂直翻转上半部分
            mirrored_top = top_half.transpose(Image.FLIP_TOP_BOTTOM)
            
            # 创建新图片（与原图片相同大小）
            result_img = Image.new('RGB', (width, height))
            
            # 粘贴上半部分
            result_img.paste(img, (0, 0))
            
            # 粘贴镜像后的上半部分到下半部分
            result_img.paste(mirrored_top, (0, mid_point))
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称上处理失败: {e}")
        return None


def process_image_symmetric_bottom(image_path: str) -> Optional[bytes]:
    """处理图片，将下半部分镜像覆盖到上半部分"""
    try:
        with Image.open(image_path) as img:
            # 获取图片尺寸
            width, height = img.size
            
            # 计算中间线
            mid_point = height // 2
            
            # 裁剪下半部分
            bottom_half = img.crop((0, mid_point, width, height))
            
            # 垂直翻转下半部分
            mirrored_bottom = bottom_half.transpose(Image.FLIP_TOP_BOTTOM)
            
            # 创建新图片（与原图片相同大小）
            result_img = Image.new('RGB', (width, height))
            
            # 粘贴下半部分
            result_img.paste(img, (0, 0))
            
            # 粘贴镜像后的下半部分到上半部分
            result_img.paste(mirrored_bottom, (0, 0))
            
            # 保存结果到字节流
            img_byte_arr = io.BytesIO()
            result_img.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception as e:
        logger.debug(f"对称下处理失败: {e}")
        return None