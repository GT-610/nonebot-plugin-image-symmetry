<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-image-symmetry

_✨ NoneBot 图像对称处理插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/yourusername/nonebot-plugin-image-symmetry.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-image-symmetry">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-image-symmetry.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

一个 NoneBot 2 插件，用于将图片的左半部分镜像翻转后覆盖到右半部分，实现左到右的对称处理。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-image-symmetry

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-image-symmetry
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-image-symmetry
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-image-symmetry
</details>
<details>
<summary>conda</summary>

    conda install -c conda-forge nonebot-plugin-image-symmetry
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_image_symmetry"]

</details>

## ⚙️ 配置

插件不需要额外配置即可使用。

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 对称左 | 群员 | 否 | 群聊/私聊 | 将图片左半部分镜像到右半部分 |
| 对称 | 群员 | 否 | 群聊/私聊 | 对称左的别名 |
| 镜像 | 群员 | 否 | 群聊/私聊 | 对称左的别名 |
| 镜像处理 | 群员 | 否 | 群聊/私聊 | 对称左的别名 |

### 使用方法
#### 方法一：同时发送图片和指令
1. 在聊天中同时发送一张图片和文本指令：`对称左`、`对称`、`镜像` 或 `镜像处理`
2. 插件将自动处理图片并返回结果

#### 方法二：对图片消息回复指令
1. 找到一条包含图片的消息
2. 回复该消息并输入指令：`对称左`、`对称`、`镜像` 或 `镜像处理`
3. 插件将处理回复的图片并返回结果

## 📝 许可证

本项目采用 Apache License 2.0 许可证。详见 LICENSE 文件。
