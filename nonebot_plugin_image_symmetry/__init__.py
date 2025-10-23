import io
import os
import aiohttp
import hashlib
from PIL import Image
from nonebot import get_driver, on_command, on_message
from nonebot.adapters import Event
from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot_plugin_localstore import get_cache_dir

# 配置项
driver = get_driver()

# 定义插件名称和版本
__plugin_name__ = "图像对称处理"
__plugin_version__ = "0.1.0"
__plugin_description__ = "提供图像左右对称变换功能"

# 图片对称处理函数
def process_image_symmetric(image_path: str) -> bytes:
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
        logger.error(f"图像处理失败: {e}")
        return None

# 检查消息是否同时包含图片和特定指令
def has_image_and_command(event: Event) -> bool:
    """检查消息是否同时包含图片和特定指令（对称左或对称）"""
    if isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
        # 检查是否包含图片
        has_image_flag = False
        for msg_seg in event.message:
            if msg_seg.type == 'image':
                has_image_flag = True
                break
        
        # 检查是否包含指定文本指令
        plain_text = event.get_plaintext().strip()
        has_command_flag = plain_text in ["对称左", "对称"]
        
        return has_image_flag and has_command_flag
    return False

# 检查是否是对图片消息的回复且内容为特定指令
def is_reply_to_image_and_contains_command(event: Event) -> bool:
    """检查是否是对图片消息的回复且内容为特定指令（对称左或对称）"""
    if isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
        # 检查是否有回复
        if event.reply:
            # 检查回复的消息是否包含图片
            for msg_seg in event.reply.message:
                if msg_seg.type == 'image':
                    # 检查当前消息内容是否为指定指令
                    plain_text = event.get_plaintext().strip()
                    return plain_text in ["对称左", "对称"]
    return False

# 图像对称命令
image_symmetry = on_command("对称左", aliases={"对称"}, priority=50)

# 图像对称消息处理器 - 仅在同时包含图片和指令时触发
image_symmetry_handler = on_message(rule=Rule(has_image_and_command), priority=50)

# 回复处理处理器 - 对图片消息回复特定指令时触发
reply_handler = on_message(rule=Rule(is_reply_to_image_and_contains_command), priority=40)

# 异步下载图片
async def download_image(url: str) -> str:
    """异步下载图片并返回临时文件路径，使用 nonebot-plugin-localstore 的 cache 目录"""
    try:
        # 获取插件的缓存目录
        cache_dir = get_cache_dir(plugin_name="nonebot_plugin_image_symmetry")
        os.makedirs(cache_dir, exist_ok=True)
        
        # 生成唯一的文件名（基于URL的哈希值）
        filename = hashlib.md5(url.encode()).hexdigest() + '.jpg'
        file_path = os.path.join(cache_dir, filename)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())
                    return file_path
    except Exception as e:
        logger.error(f"图片下载失败: {e}")
    return None

# 处理对称命令
@image_symmetry.handle()
async def handle_symmetry_command(state: T_State):
    """处理对称命令"""
    await image_symmetry.send("请同时发送需要处理的图片和指令'对称左'（或'对称'）")

# 处理直接发送的图片
@image_symmetry_handler.handle()
async def handle_image(event: Event, state: T_State):
    """处理图片消息"""
    if isinstance(event, (GroupMessageEvent, PrivateMessageEvent)):
        for msg_seg in event.message:
            if msg_seg.type == 'image':
                # 获取图片URL
                image_url = msg_seg.data.get('url')
                if image_url:
                    # 下载图片
                    temp_path = await download_image(image_url)
                    if temp_path:
                        try:
                            # 处理图片
                            processed_image = process_image_symmetric(temp_path)
                            if processed_image:
                                # 发送处理后的图片
                                await image_symmetry_handler.send(
                                    Message([MessageSegment.image(processed_image)])
                                )
                            else:
                                await image_symmetry_handler.send("图片处理失败")
                        finally:
                            # 清理临时文件
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                    else:
                        await image_symmetry_handler.send("图片下载失败")
                return

# 处理对图片的回复"对称"
@reply_handler.handle()
async def handle_reply_symmetry(event: Event, state: T_State):
    """处理对图片消息的回复"""
    if isinstance(event, (GroupMessageEvent, PrivateMessageEvent)) and event.reply:
        for msg_seg in event.reply.message:
            if msg_seg.type == 'image':
                # 获取图片URL
                image_url = msg_seg.data.get('url')
                if image_url:
                    # 下载图片
                    temp_path = await download_image(image_url)
                    if temp_path:
                        try:
                            # 处理图片
                            processed_image = process_image_symmetric(temp_path)
                            if processed_image:
                                # 发送处理后的图片
                                await reply_handler.send(
                                    Message([MessageSegment.image(processed_image)])
                                )
                            else:
                                await reply_handler.send("图片处理失败")
                        finally:
                            # 清理临时文件
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                    else:
                        await reply_handler.send("图片下载失败")
                return

# 插件初始化
@driver.on_startup
def startup():
    """插件启动时执行"""
    logger.info(f"插件 {__plugin_name__} v{__plugin_version__} 已加载")

# 插件启动时初始化缓存目录
@driver.on_startup
def initialize_cache():
    """初始化缓存目录"""
    cache_dir = get_cache_dir(plugin_name="nonebot_plugin_image_symmetry")
    os.makedirs(cache_dir, exist_ok=True)
    logger.info(f"图像缓存目录已初始化: {cache_dir}")