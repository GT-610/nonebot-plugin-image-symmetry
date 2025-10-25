<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/refs/heads/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/refs/heads/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-image-symmetry

_✨ NoneBot 图像对称处理插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/GT-610/nonebot-plugin-image-symmetry.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-image-symmetry">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-image-symmetry.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://v2.nonebot.dev/">
    <img src="https://img.shields.io/badge/NoneBot-v2-green.svg" alt="NoneBot2">
</a>

</div>

## 📖 介绍

一个 NoneBot 2 插件，提供图像的四个方向对称变换功能：
- 对称左：将图片左半部分镜像翻转后覆盖到右半部分
- 对称右：将图片右半部分镜像翻转后覆盖到左半部分
- 对称上：将图片上半部分镜像翻转后覆盖到下半部分
- 对称下：将图片下半部分镜像翻转后覆盖到上半部分

## 💿 安装

此插件需要 `httpx` 驱动器下载图片，请在 `DRIVER` 变量中添加 `~httpx`。

驱动器安装和配置参考 [NoneBot 选择驱动器](https://nonebot.dev/docs/advanced/driver)。


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

### 环境变量配置

插件支持通过环境变量自定义最大缓存图片数量：

| 环境变量 | 类型 | 默认值 | 范围 | 说明 |
| :------- | :--- | :----- | :--- | :--- |
| `IMAGE_SYMMETRY_MAX_CACHE` | 整数 | 100 | [5, 9999] | 控制before和after两个目录中图片的总缓存数量上限 |

> 注意：如果设置的值超出有效范围或无效，插件将自动使用默认值100，并记录警告日志。

### 示例

在你的环境配置文件（如`.env`）中添加：
```
IMAGE_SYMMETRY_MAX_CACHE=200
```

## 🎉 使用
注意：下列命令需要加命令前缀。命令前缀为你的 NoneBot2 环境配置中， `COMMAND_START` 变量的值。

### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| 对称左 | 群员 | 否 | 群聊/私聊 | 将图片左半部分镜像到右半部分 |
| 对称右 | 群员 | 否 | 群聊/私聊 | 将图片右半部分镜像到左半部分 |
| 对称上 | 群员 | 否 | 群聊/私聊 | 将图片上半部分镜像到下半部分 |
| 对称下 | 群员 | 否 | 群聊/私聊 | 将图片下半部分镜像到上半部分 |
| 对称 | 群员 | 否 | 群聊/私聊 | 对称左的别名 |
| 对称帮助 | 群员 | 否 | 群聊/私聊 | 显示对称插件的帮助信息 |

### 使用方法
#### 方法一：同时发送图片和指令
1. 在聊天中同时发送一张图片和文本指令：`对称左`、`对称右`、`对称上` 或 `对称下`
2. 插件将根据指定的指令自动处理图片并返回结果

#### 方法二：对图片消息回复指令
1. 找到一条包含图片的消息
2. 回复该消息并输入指令：`对称左`、`对称右`、`对称上` 或 `对称下`
3. 插件将根据指定的指令处理回复的图片并返回结果

**注意**：`对称` 是 `对称左` 的别名，使用 `对称` 指令将执行与 `对称左` 相同的操作

## 📝 许可证

本项目采用 Apache License 2.0 许可证。详见 [LICENSE](LICENSE) 文件。
