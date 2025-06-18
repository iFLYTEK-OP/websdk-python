# xfyunsdkspark

xfyunsdkspark是讯飞开放平台星火大模型相关 API的Python SDK，提供[智能PPT](https://www.xfyun.cn/doc/spark/PPTv2.html)、[超拟人合成](https://www.xfyun.cn/doc/spark/super%20smart-tts.html)、[简历生成](https://www.xfyun.cn/doc/spark/resume.html)、[大模型语音识别](https://www.xfyun.cn/doc/spark/spark_zh_iat.html)、[一句话复刻](https://www.xfyun.cn/doc/spark/reproduction.html#%E9%9F%B3%E9%A2%91%E5%90%88%E6%88%90%E6%8E%A5%E5%8F%A3)、[一句话训练](https://www.xfyun.cn/doc/spark/reproduction.html#%E9%9F%B3%E8%89%B2%E8%AE%AD%E7%BB%83%E6%8E%A5%E5%8F%A3)等功能的客户端实现。

 如需**大模型对话功能**以及**生态支持**详情等请访问[讯飞星火大模型接入库](https://github.com/iflytek/spark-ai-python)

## 功能特点

- **智能PPT**：通过用户提示和模板生成PPT
- **超拟人合成**：通过文本内容生成不通角色的超拟人音频
- **简历生成**：根据用户提示生成简历
- **大模型语音识别**：支持方言、普通话、多语种等大模型智能语音识别
- **一句话复刻**：通过一句话训练复刻的用户声纹, 生成语音

## 安装方法

```bash
pip install xfyunsdkspark
```

## 依赖说明

- xfyunsdkcore>=0.1.0: 核心SDK依赖
- python-dotenv: 环境变量管理

## 快速开始

### 超拟人合成

```python
from xfyunsdkspark.oral_client import OralClient

# 初始化客户端
client = OralClient(
    app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
    api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
    api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
    encoding="raw",
    sample_rate=16000
)

for chunk in client.stream(text):
    if chunk.get("audio") and chunk["audio"]["audio"]:
        audio_chunk = base64.b64decode(chunk["audio"]["audio"])
        audio_bytes.extend(audio_chunk)
        if chunk.get("pybuf") and chunk["pybuf"].get("text"):
            pybuf_chunk = base64.b64decode(chunk["pybuf"]["text"]).decode("utf-8")
            logger.info(f"收到音素信息，{pybuf_chunk}")
            pybuf_list.append(pybuf_chunk)
        else:
            logger.info(f"收到一块音频，大小 {len(audio_chunk)} 字节")
logger.info(f"音频总大小: {len(audio_bytes)} 字节")
```

更多示例见[demo](https://github.com/iFLYTEK-OP/websdk-python-demo)

## 核心客户端

### AIPPTClient

根据用户提示和提供的200+模板生成PPT

### OralClient

流式的方式输入文本，并流式获取文本合成的音频流

### ResumeGenClient

简历智能生成，定制化需求：无论是面向校园招聘还是社会招聘，只需输入个人信息与求职需求，即刻量身打造专业简历，一键生成1~3份完整简历模板加内容

### SparkIatClient

中英识别大模型识别能力，将短音频(≤60秒)精准识别成文字，实时返回文字结果，真实还原语音内容

方言大模型，支持普通话，简单英语和202种方言全免切，无需显示指定语种

大模型多语种语音识别能力，将多语种短音频(≤60秒)精准识别成文字，实时返回文字结果，真实还原语音内容

### VoiceTrainClient

训练音频准备（通过/task/traintext 查询出来录音文本列表，根据选择的文本进行录音）**注意：要求录音音频和文本保持一致，否则会导致音频检测失败。**

创建训练任务（通过/task/add 创建训练任务）

向训练任务添加音频（url链接） （通过 /audio/v1/add 给训练任务添加准备好的训练音频）

提交训练任务 （通过/task/submit 方法提交已经添加音频的训练任务）

向训练任务添加音频（本地文件）并提交训练任务 （通过 /task/submitWithAudio 给训练任务添加准备好的训练音频）

查询训练任务状态 （通过/task/result 查询训练任务状态，训练成功后即可进入合成阶段 

### VoiceCloneClient

上传文本通过训练出的音色资源进行合成 , **支持合成中、英、日、韩、俄五种语言**


## 许可证

请参见LICENSE文件