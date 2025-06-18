from setuptools import setup, find_packages

setup(
    name="xfyunsdkocr",
    version="0.1.0",
    description="a sdk ocr for xfyun",
    author="zyding6",
    author_email="zyding6@iflytek.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["xfyunsdkocr", "xfyunsdkocr.*"]),
    python_requires=">=3.7.1",
    install_requires=[
        "xfyunsdkcore>=0.1.0",
        "python-dotenv"
    ],
)
