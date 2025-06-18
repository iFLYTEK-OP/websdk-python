# 讯飞开放平台AI能力-PYTHONSDK

[![Build Status](https://www.travis-ci.com/iFLYTEK-OP/websdk-java.svg?branch=feature-ci)](https://www.travis-ci.com/iFLYTEK-OP/websdk-java)[![codecov](https://codecov.io/gh/iFLYTEK-OP/websdk-java/branch/feature-ci/graph/badge.svg?token=KQRe0Igv9b)](https://codecov.io/gh/iFLYTEK-OP/websdk-java)

提供各种讯飞开放平台能力的PYTHONSDK。



## 安装

**项目仅支持 Python3.8+**

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

[1、智能PPT(新)-API](https://github.com/iFLYTEK-OP/websdk-java/blob/master/doc/spark/aipptv2.md)

[2、超拟人合成-API](https://github.com/iFLYTEK-OP/websdk-java/blob/master/doc/spark/oralapi.md)

[3、简历生成-API](https://github.com/iFLYTEK-OP/websdk-java/blob/master/doc/spark/resumegenapi.md)

[4、大模型语音听写-API](https://github.com/iFLYTEK-OP/websdk-java/blob/master/doc/spark/sparkiatapi.md)

[5、一句话复刻-API](https://github.com/iFLYTEK-OP/websdk-java/blob/master/doc/spark/voiceclone.md)

## 语音相关能力
```xml
pip install --upgrade xfyunsdkspeech
```
以下为项目地址

[1、非实时语音转写文档](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/LFASR.md)

[2、实时语音转写文档](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/RTASR.md)

[3、在线语音合成文档](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/TTS.md)

[4、语音听写文档](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/IAT.md)

[5、语音评测文档](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/ISE.md)

[6、语音评测（普通版）](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/ISE_HTTP.md)

[7、性别年龄识别](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/IGR.md)

[8、歌曲识别](https://github.com/iFLYTEK-OP/websdk-java-speech/blob/master/doc/speech/QBH.md)