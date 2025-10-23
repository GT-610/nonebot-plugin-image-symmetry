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

一个 NoneBot 2 插件，用于对图片进行水平、垂直和中心对称变换处理。

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
| 镜像 | 群员 | 否 | 群聊/私聊 | 开始图像对称处理 |
| 对称 | 群员 | 否 | 群聊/私聊 | 开始图像对称处理 |
| 镜像处理 | 群员 | 否 | 群聊/私聊 | 开始图像对称处理 |

### 使用方法
1. 在聊天中发送命令：`镜像`、`对称` 或 `镜像处理`
2. 按照提示发送需要处理的图片并说明对称类型（水平/垂直/中心）
3. 插件将返回处理后的图片

## 📝 许可证

本项目采用 Apache License 2.0 许可证。详见 LICENSE 文件。
