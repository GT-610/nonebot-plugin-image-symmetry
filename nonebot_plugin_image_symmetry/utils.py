import io
from typing import Optional

from nonebot.log import logger
from PIL import Image


class SymmetryUtils:
    """对称处理工具类，提供图像处理相关的工具方法"""
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
                format_type = img.format.lower() if img.format else None
                if format_type == "gif" and getattr(img, "is_animated", False):
                    return "gif_animated"
                return format_type
        except Exception:
            logger.exception("PIL识别图像格式失败")
            return "unknown"

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
            return Image.open(img_stream)
        except Exception as e:
            logger.error(f"字节数据转换为图像失败: {e}")
            return None

    @staticmethod
    def image_to_bytes(img: Image.Image, image_type: Optional[str] = None) -> bytes:
        """将PIL图像对象转换为字节数据
        Args:
            img: PIL图像对象
            image_type: 图像类型，如果为None则使用图像原始格式
        Returns:
            bytes: 图像字节数据，如果转换失败则返回None
        """
        try:
            img_stream = io.BytesIO()

            image_format = image_type.upper() if image_type else img.format or "PNG"

            if image_format == "JPEG" and img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            exif = img.info.get("exif")
            if exif:
                img.save(img_stream, format=image_format, exif=exif)
            else:
                img.save(img_stream, format=image_format)

            return img_stream.getvalue()
        except Exception:
            logger.exception("图像转换为字节数据失败")
            return None
