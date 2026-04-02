import hashlib

from nonebot import get_driver, require
from nonebot.adapters import Bot, Event
from nonebot.exception import FinishedException
from nonebot.log import logger
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.typing import T_State
from nonebot.utils import run_sync

# 引入命令处理插件
require("nonebot_plugin_alconna")
from arclet.alconna import Alconna, CommandMeta
from nonebot_plugin_alconna import (
    AlcMatches,
    Image,
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
    name="图像对称",
    description="提供图像上下左右四个方向的对称变换功能",
    usage="发送'对称左'/'对称右'/'对称上'/'对称下'或简写'对称'（默认为左对称）加上图片，或者回复图片消息加上对应命令",
    type="application",
    homepage="https://github.com/GT-610/nonebot-plugin-image-symmetry",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

# 获取驱动实例，用于插件生命周期管理
driver = get_driver()

# 命令到对称方向的映射
DIRECTION_MAP = {
    "对称左": "left",
    "对称": "left",
    "对称右": "right",
    "对称上": "top",
    "对称下": "bottom"
}


def create_matcher(command: Command):
    """为指定命令创建命令匹配器和处理逻辑
    
    Args:
        command: 命令对象，包含关键字和处理函数
    """
    # 主命令
    main_keyword = command.keywords[0]
    aliases = command.keywords[1:] if len(command.keywords) > 1 else []

    # 创建Alconna命令并添加参数
    alc = Alconna(main_keyword, meta=CommandMeta(strict=False))
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
    async def handle_function(
        bot: Bot,
        event: Event,
        state: T_State,
        matches: AlcMatches,
    ) -> None:
        try:
            logger.debug(f"识别到命令: {main_keyword}")
            logger.debug(f"完整消息内容: {event.get_plaintext()}")
            logger.debug(f"matches内容: {matches}")

            extra = getattr(matches, "$extra", [])
            images = [seg for seg in extra if isinstance(seg, Image)]

            if len(images) > 1:
                await matcher.finish("不支持对称多张图片，请只发送一张图片")
                return

            if len(images) == 0:
                await matcher.finish("未检测到图片，请发送包含图片的消息")
                return

            img_obj = images[0]
            logger.info(f"开始处理图片: URL: {getattr(img_obj, 'url', 'N/A')}")

            try:
                img_bytes = await image_fetch(event, bot, state, img_obj)
                if not img_bytes:
                    logger.error("图片下载失败: 返回空数据")
                    await matcher.finish("图片下载失败，请重试")
                    return

                logger.debug(f"成功下载图片，大小: {len(img_bytes)} 字节")
            except Exception as e:
                logger.error(f"下载图片异常: {type(e).__name__}: {e}")
                await matcher.finish(f"图片处理异常: {e!s}")
                return

            image_type = SymmetryUtils.identify_image_type(img_bytes)
            logger.debug(f"检测到图片类型: {image_type}")

            direction = DIRECTION_MAP.get(main_keyword, "unknown")
            logger.debug(f"处理图片，方向: {direction}")

            processed_data = await run_sync(command.func)(
                img_bytes=img_bytes,
                image_type=image_type
            )

            if not processed_data:
                logger.error("图像处理失败，返回空数据")
                await matcher.finish("图像处理失败，请重试")
                return

            logger.debug(f"处理后图片大小: {len(processed_data)} 字节")
            await UniMessage.image(raw=processed_data).send()

        except FinishedException:
            raise
        except Exception as e:
            logger.error(f"处理命令时发生错误: {type(e).__name__}: {e}")
            await matcher.finish(f"处理失败：{e!s}")

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
        help_text = (
            "图像对称处理插件使用说明（记得加前缀）：\n"
            "1. 直接发送：命令 + 图片\n"
            "2. 回复处理：回复图片消息 + 命令\n\n"
            "支持的命令：\n"
            "- 对称/对称左：将图片左半部分镜像到右半部分\n"
            "- 对称右：将图片右半部分镜像到左半部分\n"
            "- 对称上：将图片上半部分镜像到下半部分\n"
            "- 对称下：将图片下半部分镜像到上半部分\n\n"
            "例如：发送'对称左'加上一张图片，或回复一张图片说'对称上'\n\n"
            "插件源代码：https://github.com/GT-610/nonebot-plugin-image-symmetry"
        )
        await UniMessage.text(help_text).send()

# 在插件加载时创建所有命令匹配器和帮助命令
create_matchers()
help_cmd()

# 插件启动事件处理
@driver.on_startup
async def _startup():
    """插件启动时执行初始化操作"""
    logger.info("图像对称处理插件已启动")
