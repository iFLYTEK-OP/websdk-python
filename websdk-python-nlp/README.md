# xfyunsdknlp

xfyunsdknlp是讯飞开放平台自然语言处理相关API的Python SDK，提供[视频](https://www.xfyun.cn/doc/nlp/VideoModeration/API.html)/[文本](https://www.xfyun.cn/doc/nlp/TextModeration/API.html)/[音频](https://www.xfyun.cn/doc/nlp/AudioModeration/API.html)/[图片](https://www.xfyun.cn/doc/nlp/ImageModeration/API.html)合规、[语义依存分析](https://www.xfyun.cn/doc/nlp/semanticDependence/API.html)、[情感分析](https://www.xfyun.cn/doc/nlp/emotion-analysis/API_v1.html)、[同声传译](https://www.xfyun.cn/doc/nlp/simultaneous-interpretation/API.html)、[文本纠错](https://www.xfyun.cn/doc/nlp/textCorrection/API.html)、[公文校对](https://www.xfyun.cn/doc/nlp/textCorrectionOfficial/API.html)、[文本改写](https://www.xfyun.cn/doc/nlp/textRewriting/API.html)、[机械翻译](https://www.xfyun.cn/doc/nlp/xftrans/API.html)、[词库](https://www.xfyun.cn/doc/nlp/TextModeration/API.html#%E5%90%88%E8%A7%84%E9%BB%91%E7%99%BD%E5%90%8D%E5%8D%95)等功能的客户端实现。

## 功能特点

- **视频/文本/音频/图片合规**：精准高效识别各类场景中违禁、涉政、色情、未成年违规、暴恐、广告、Logo等风险内容
- **语义依存分析LTP**：提供高效精准的 **中文（简体）** 自然语言处理服务
- **情感分析**：提供针对 **中文（简体）** 文本的情感分析服务
- **同声传译**：将音频流实时翻译为不同语种的文本，并输对应的音频内容
- **文本纠错**：对文本进行校对，校对包括拼写、语法、搭配、实体纠错、标点、领导人职称、政治用语及数字纠错等
- **公文校对**：对文本内容进行文字标点差错、知识性差错、内容导向风险识别
- **文本改写**：改变语句顺序或使用其他近义词语进行替换等方式来改写中文句子或段落。
- **机械翻译**：将源语种文字转化为目标语种文字
- **词库**：自定义合规规则和敏感词

## 安装方法

```bash
pip install xfyunsdknlp
```

## 依赖说明

- xfyunsdkcore>=0.1.0: 核心SDK依赖
- python-dotenv: 环境变量管理

## 快速开始

### 同声传译

```python
from xfyunsdknlp.sim_interp_client import SimInterpClient

# 读取图片并转换为base64
file_path = os.path.join(os.path.dirname(__file__), 'resources', 'original.pcm')
f = open(file_path, 'rb')

 # 初始化客户端
        client = SimInterpClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            encoding="lame"
        )

# 发送请求
for chunk in client.stream(f):
	logger.info(f"返回结果: {chunk}")
```

更多示例见[demo](https://github.com/iFLYTEK-OP/websdk-python-demo)

## 核心客户端

### AudioModerationClient

检测音频内容是否合规

### ImageModerationClient

检测图片内容是否合规

### VideoModerationClient

检测视频内容是否合规

### TextModerationClient

检测文本内容是否合规

### LTPClient

提供高效精准的 **中文（简体）** 自然语言处理服务

### SaClient

分析文本表的情感。

### SimInterpClient

将音频流实时翻译为不同语种的文本，并输对应的音频内容。

### TextCheckClient

对文本进行校对，校对包括拼写、语法、搭配、实体纠错、标点、领导人职称、政治用语及数字纠错等

### TextProofClient

对文本内容进行文字标点差错、知识性差错、内容导向风险识别

### TextRewriteClient

改变语句顺序或使用其他近义词语进行替换等方式来改写中文句子或段落。

### TranslateClient

将源语种文字转化为目标语种文字

### WordLibClient

自定义合规规则和敏感词


## 许可证

请参见LICENSE文件