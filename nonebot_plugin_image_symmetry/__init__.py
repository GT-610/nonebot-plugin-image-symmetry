import os
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
                
                # 下载图片
                # 使用image_fetch获取图片字节数据
                img_bytes = await image_fetch(event, bot, state, img)
                if not img_bytes:
                    logger.error("图片下载失败: 返回空数据")
                    await matcher.finish("图片下载失败，请重试")
                    return
                
                logger.info(f"成功下载图片，大小: {len(img_bytes)} 字节")
                
                # 使用工具类处理图片
                temp_file_path = SymmetryUtils.bytes_to_temp_file(img_bytes)
                if not temp_file_path:
                    logger.error("保存图片失败")
                    await matcher.finish("保存图片失败，请重试")
                    return
                
                logger.info(f"图片已保存至: {temp_file_path}")
                
                # 获取图片的唯一标识符（基于内容的哈希值）
                # 注意：bytes_to_temp_file现在直接使用哈希值作为文件名
                image_hash = os.path.basename(temp_file_path).split('.')[0]
                logger.info(f"图片唯一标识符: {image_hash}")
                
                # 获取命令对应的处理函数和方向标识符
                direction_map = {
                    "对称左": "left",
                    "对称": "left",
                    "对称右": "right",
                    "对称上": "top",
                    "对称下": "bottom"
                }
                direction = direction_map.get(main_keyword, "unknown")
                
                # 执行图像处理
                logger.info(f"开始处理图片，方向: {direction}")
                processed_bytes = await run_sync(command.func)(img_bytes)
                
                if not processed_bytes:
                    logger.error("图像处理失败，返回空数据")
                    await matcher.finish("图像处理失败，请重试")
                    return
                
                # 保存处理后的图片到after目录
                after_dir = SymmetryUtils.get_after_cache_dir()
                output_filename = f"{image_hash}_{direction}.jpg"
                output_path = os.path.join(after_dir, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(processed_bytes)
                
                logger.info(f"处理后图片已保存至: {output_path}")
                logger.info(f"处理后图片大小: {len(processed_bytes)} 字节")
                
                # 发送处理后的图片
                logger.info(f"准备发送处理后的图片: {output_path}")
                
                # 构建发送消息
                message = UniMessage()
                message += UniMessage.text(f"🔹 图像处理完成！\n\n")
                message += UniMessage.image(path=output_path)
                message += UniMessage.text(f"\n📝 处理详情：\n- 命令: {main_keyword}\n- 方向: {direction}\n- 图片标识: {image_hash}")
                
                # 发送消息
                await message.send()
                await matcher.finish()
                return
            
            # 根据测试，当没有图片时命令不会触发，所以只保留通用异常处理
        except Exception as e:
            logger.error(f"处理命令时发生错误: {e}")
            # 移除异常处理，让错误正常传播
            raise

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
    # 初始化目录结构（包括before和after子目录）
    SymmetryUtils.initialize_directories()
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