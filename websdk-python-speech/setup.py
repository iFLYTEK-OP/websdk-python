from setuptools import setup, find_packages

setup(
    name="xfyunsdkspeech",
    version="0.0.3",
    description="a sdk speech for xfyun",
    author="zyding6",
    author_email="zyding6@iflytek.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["xfyunsdkspeech", "xfyunsdkspeech.*"]),
    python_requires=">=3.7.1",
    install_requires=[
        "xfyunsdkcore>=0.0.3",
        "python-dotenv"
    ],
    extras_require={
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov"
        ]
    },
)
