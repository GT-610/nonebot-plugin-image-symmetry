from nonebot import require, get_driver
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.utils import run_sync

# 引入 nonebot_plugin_alconna 相关组件
require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import (
    AlcMatches,
    Alconna,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension
from nonebot_plugin_alconna.uniseg.tools import image_fetch

# 导入其他模块
from .command import Command, commands
from .config import Config, symmetry_config
from .utils import SymmetryUtils

# 定义插件元数据
__plugin_meta__ = PluginMetadata(
    name="图像对称处理",
    description="提供图像上下左右四个方向的对称变换功能",
    usage="发送‘对称左’/‘对称右’/‘对称上’/‘对称下’或简写‘对称’（默认为左对称）加上图片，或者回复图片消息加上对应命令",
    type="application",
    homepage="https://github.com/GT-610/nonebot-plugin-image-symmetry",
    config=Config,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

# 获取驱动实例
driver = get_driver()


# 创建命令匹配器
def create_matcher(command: Command):
    """创建命令匹配器"""
    # 主命令
    main_keyword = command.keywords[0]
    aliases = command.keywords[1:] if len(command.keywords) > 1 else []
    
    # 创建命令并添加参数
    alc = Alconna(main_keyword, command.args)
    # 添加 ReplyMergeExtension 以支持回复消息
    matcher = on_alconna(
        alc,
        aliases=aliases,
        use_cmd_start=True,
        block=True,
        extensions=[ReplyMergeExtension()]
    )
    
    # 注册处理函数
    @matcher.handle()
    async def handle_function(bot: Bot, event: Event, state: T_State, matches: AlcMatches):
        try:
            # 调试输出：打印识别到的命令
            logger.info(f"识别到命令: {main_keyword}")
            logger.info(f"完整消息内容: {event.get_plaintext()}")
            
            img_bytes = None
            image_info = None
            
            # 从命令参数中获取图片 (通过 matches)
            if hasattr(matches, 'img') and matches.img:
                img = matches.img
                image_info = f"命令参数图片 - URL: {getattr(img, 'url', 'N/A')}"
                logger.info(f"从命令参数获取图片: {image_info}")
                
                # 暂时搁置实际的图像处理，仅输出调试信息
                await matcher.finish(f"命令捕获成功！\n识别到的指令: {main_keyword}\n图片信息: {image_info}")
                return
            
            # 根据测试，当没有图片时命令不会触发，所以只保留通用异常处理
        except Exception as e:
            logger.error(f"处理命令时发生错误: {e}")
            await matcher.finish(f"处理失败: {str(e)}")

# 创建所有命令的匹配器
def create_matchers():
    """创建所有命令的匹配器"""
    for command in commands:
        create_matcher(command)

# 创建帮助命令
def help_cmd():
    """创建帮助命令"""
    # 创建帮助命令
    help_alc = Alconna("对称帮助")
    help_matcher = on_alconna(help_alc, use_cmd_start=True)
    
    @help_matcher.handle()
    async def handle_help():
        help_text = "图像对称处理插件使用说明：\n1. 直接发送：命令 + 图片\n2. 回复处理：回复图片消息 + 命令\n\n支持的命令：\n- 对称/对称左：将图片左半部分镜像到右半部分\n- 对称右：将图片右半部分镜像到左半部分\n- 对称上：将图片上半部分镜像到下半部分\n- 对称下：将图片下半部分镜像到上半部分\n\n例如：发送\"对称左\"加上一张图片，或回复一张图片说\"对称上\""
        await UniMessage.text(help_text).send()

# 初始化插件
@driver.on_startup
async def _startup():
    """插件启动时的初始化操作"""
    # 初始化缓存目录
    SymmetryUtils.get_cache_dir()
    # 创建命令匹配器
    create_matchers()
    # 创建帮助命令
    help_cmd()
    logger.info("图像对称处理插件已启动")

# 导出供其他插件使用的功能
export = {
    "commands": commands,
    "create_matcher": create_matcher,
    "create_matchers": create_matchers
}

# 插件初始化完成