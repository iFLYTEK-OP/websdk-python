from setuptools import setup, find_packages

setup(
    name="xfyunsdkspark",
    version="0.0.2",
    description="a sdk spark for xfyun",
    author="zyding6",
    author_email="zyding6@iflytek.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["xfyunsdkspark", "xfyunsdkspark.*"]),
    python_requires=">=3.7.1",
    install_requires=[
        "xfyunsdkcore>=0.0.2",
        "python-dotenv"
    ],
)
