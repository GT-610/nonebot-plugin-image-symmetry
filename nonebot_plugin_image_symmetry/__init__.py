from nonebot import require, get_driver
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.utils import run_sync

# 引入命令处理和本地存储相关插件
require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")
from nonebot_plugin_alconna import (
    AlcMatches,
    Alconna,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension
from nonebot_plugin_alconna.uniseg.tools import image_fetch

# 导入当前插件的模块
from .command import Command, commands
from .utils import SymmetryUtils

# 定义插件元数据
__plugin_meta__ = PluginMetadata(
    name="图像对称处理",
    description="提供图像上下左右四个方向的对称变换功能",
    usage="发送'对称左'/'对称右'/'对称上'/'对称下'或简写'对称'（默认为左对称）加上图片，或者回复图片消息加上对应命令",
    type="application",
    homepage="https://github.com/GT-610/nonebot-plugin-image-symmetry",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

# 获取驱动实例，用于插件生命周期管理
driver = get_driver()


def create_matcher(command: Command):
    """为指定命令创建命令匹配器和处理逻辑
    
    Args:
        command: 命令对象，包含关键字和处理函数
    """
    # 主命令
    main_keyword = command.keywords[0]
    aliases = command.keywords[1:] if len(command.keywords) > 1 else []
    
    # 创建Alconna命令并添加参数
    alc = Alconna(main_keyword, command.args)
    # 添加ReplyMergeExtension以支持回复消息处理
    matcher = on_alconna(
        alc,
        aliases=aliases,
        use_cmd_start=True,
        block=True,
        extensions=[ReplyMergeExtension()]
    )
    
    # 注册命令处理函数
    @matcher.handle()
    async def handle_function(bot: Bot, event: Event, state: T_State, matches: AlcMatches):
        try:
            # 调试输出：记录识别到的命令和消息内容
            logger.debug(f"识别到命令: {main_keyword}")
            logger.debug(f"完整消息内容: {event.get_plaintext()}")
            
            img_bytes = None
            image_info = None
            
            # 从命令参数中获取图片
            if hasattr(matches, 'img') and matches.img:
                img = matches.img
                image_info = f"命令参数图片 - URL: {getattr(img, 'url', 'N/A')}"
                logger.debug(f"获取图片: {image_info}")
                
                # 下载图片字节数据
                img_bytes = await image_fetch(event, bot, state, img)
                if not img_bytes:
                    logger.error("图片下载失败: 返回空数据")
                    await matcher.finish("图片下载失败，请重试")
                    return
                
                logger.debug(f"成功下载图片，大小: {len(img_bytes)} 字节")
                
                # 计算图片哈希值用于标识
                import hashlib
                image_hash = hashlib.md5(img_bytes).hexdigest()
                logger.debug(f"获取图片成功，哈希值: {image_hash}")
                
                # 将字节数据保存为临时文件
                temp_path, image_type = SymmetryUtils.bytes_to_temp_file(img_bytes)
                if not temp_path:
                    logger.error("保存图片失败")
                    await matcher.finish("保存图片失败，请重试")
                    return
                
                logger.debug(f"图片已保存至: {temp_path}")
                
                # 映射命令到对应的对称方向
                direction_map = {
                    "对称左": "left",
                    "对称": "left",
                    "对称右": "right",
                    "对称上": "top",
                    "对称下": "bottom"
                }
                direction = direction_map.get(main_keyword, "unknown")
                
                # 异步执行图像处理
                logger.debug(f"开始处理图片，方向: {direction}")
                processed_bytes = await run_sync(command.func)(temp_path, image_type)
                
                if not processed_bytes:
                    logger.error("图像处理失败，返回空数据")
                    await matcher.finish("图像处理失败，请重试")
                
                # 保存处理后的图片并管理缓存
                output_path = SymmetryUtils.save_processed_image(image_hash, direction, processed_bytes, image_type)
                if not output_path:
                    logger.error("保存处理后图片失败")
                    await matcher.finish("保存处理后图片失败，请重试")
                    return
                
                logger.debug(f"处理后图片已保存至: {output_path}")
                logger.debug(f"处理后图片大小: {len(processed_bytes)} 字节")
                
                # 发送处理后的图片
                logger.debug(f"准备发送处理后的图片: {output_path}")
                await UniMessage.image(path=output_path).send()
                return
            
        except Exception as e:
            # 捕获所有异常并记录错误日志
            logger.error(f"处理命令时发生错误: {e}")
            raise

def create_matchers():
    """为所有定义的命令创建对应的命令匹配器"""
    for command in commands:
        create_matcher(command)

def help_cmd():
    """创建插件帮助命令和处理逻辑"""
    # 创建帮助命令匹配器
    help_alc = Alconna("对称帮助")
    help_matcher = on_alconna(help_alc, use_cmd_start=True)
    
    @help_matcher.handle()
    async def handle_help():
        # 帮助文本内容，说明插件使用方法和支持的命令
        help_text = "图像对称处理插件使用说明（记得加前缀）：\n1. 直接发送：命令 + 图片\n2. 回复处理：回复图片消息 + 命令\n\n支持的命令：\n- 对称/对称左：将图片左半部分镜像到右半部分\n- 对称右：将图片右半部分镜像到左半部分\n- 对称上：将图片上半部分镜像到下半部分\n- 对称下：将图片下半部分镜像到上半部分\n\n例如：发送'对称左'加上一张图片，或回复一张图片说'对称上'"
        await UniMessage.text(help_text).send()

# 在插件加载时创建所有命令匹配器和帮助命令
create_matchers()
help_cmd()

# 插件启动事件处理
@driver.on_startup
async def _startup():
    """插件启动时执行初始化操作"""
    # 初始化插件所需的目录结构
    SymmetryUtils.initialize_directories()
    logger.info("图像对称处理插件已启动")