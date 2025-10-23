from setuptools import setup, find_packages

setup(
    name="nonebot-plugin-image-symmetry",
    version="0.1.0",
    description="NoneBot 2 图像对称处理插件",
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/nonebot-plugin-image-symmetry",
    packages=find_packages(),
    install_requires=[
        "nonebot2>=2.0.0-beta.1",
        "nonebot-adapter-onebot>=2.0.0-beta.1",
        "Pillow>=9.0.0",
        "aiohttp>=3.8.0",
        "nonebot-plugin-localstore>=0.3.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)