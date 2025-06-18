from setuptools import setup, find_packages

setup(
    name="xfyunsdkcore",
    version="0.1.0",
    description="a sdk core for xfyun",
    author="zyding6",
    author_email="zyding6@iflytek.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["xfyunsdkcore", "xfyunsdkcore.*"]),
    python_requires=">=3.7.1",
    install_requires=[
        "httpx",  # httpx 0.23.x 是最后一个支持 Python 3.7 的版本
        "websocket-client<2.0.0"  # 1.5.0 开始要求 Python 3.8+
    ],
)
