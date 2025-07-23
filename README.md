# 讯飞开放平台AI能力-PYTHONSDK

[![Build Status](https://www.travis-ci.com/iFLYTEK-OP/websdk-java.svg?branch=feature-ci)](https://www.travis-ci.com/iFLYTEK-OP/websdk-java)[![codecov](https://codecov.io/gh/iFLYTEK-OP/websdk-java/branch/feature-ci/graph/badge.svg?token=KQRe0Igv9b)](https://codecov.io/gh/iFLYTEK-OP/websdk-java)

提供各种讯飞开放平台能力的PYTHONSDK。



## 安装

**项目仅支持 Python3.7+**

如果你不需要源码，只需要通过 `pip `快速安装

```sh
pip install --upgrade package_name
```

国内使用:

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name
```

### Upgrade

如果清华源版本不可用,请使用一下命令升级到最新版本:

```sh
pip install -i  https://repo.model.xfyun.cn/api/packages/administrator/pypi/simple  package_name --upgrade
```

Install from source with:

```sh
pip install -e .
```

## 星火大模型相关

星火大模型相关**会话能力**请访问以下项目地址

- Github: https://github.com/iflytek/spark-ai-python

以下为星火大模型**拓展能力**

```sh
pip install --upgrade xfyunsdkspark
```

文档地址:   [SPARK-API](https://github.com/iFLYTEK-OP/websdk-python/blob/master/websdk-python-spark/README.md)

## 语音相关能力
```xml
pip install --upgrade xfyunsdkspeech
```
文档地址:   [SPEECH-API](https://github.com/iFLYTEK-OP/websdk-python/blob/master/websdk-python-speech/README.md)

## 面部识别相关能力

```xml
pip install --upgrade xfyunsdkface
```

文档地址:   [FACE-API](https://github.com/iFLYTEK-OP/websdk-python/blob/master/websdk-python-face/README.md)

## 自然语言相关能力

```xml
pip install --upgrade xfyunsdknlp
```

文档地址:   [NLP-API](https://github.com/iFLYTEK-OP/websdk-python/blob/master/websdk-python-nlp/README.md)

## OCR相关能力

```xml
pip install --upgrade xfyunsdkocr
```

文档地址:   [OCR-API](https://github.com/iFLYTEK-OP/websdk-python/blob/master/websdk-python-ocr/README.md)