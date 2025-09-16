# xfyunsdkspeech

xfyunsdkspeech是讯飞开放平台语音转写相关 API的Python SDK，提供[语音听写](https://www.xfyun.cn/doc/asr/voicedictation/API.html)、[性别年龄识别](https://www.xfyun.cn/doc/voiceservice/sound-feature-recg/API.html)、[语音评测](https://www.xfyun.cn/doc/Ise/IseAPI.html)、[语音转写](https://www.xfyun.cn/doc/asr/ifasr_new/API.html)、[歌曲识别](https://www.xfyun.cn/doc/voiceservice/song-recognition/API.html)、[实时语音转写](https://www.xfyun.cn/doc/asr/rtasr/API.html)、[语音合成](https://www.xfyun.cn/doc/tts/online_tts/API.html)等功能的客户端实现。

## 功能特点

- **语音听写**：通过音频信息识别成文字
- **性别年龄识别**：通过声音信息识别用户性别年龄等信息
- **语音评测**：通过智能语音技术自动对发音水平进行评价、发音错误、缺陷定位和问题分析的能力
- **歌曲识别**：检测歌曲, 识别歌曲名称
- **语音转写**：将音频转换成文本数据
- **实时语音转写**：将连续的音频流内容，实时识别返回对应的文字流内容
- **语音合成**：通过文本数据合成音频流数据

## 安装方法

```bash
pip install xfyunsdkspeech
```

## 依赖说明

- xfyunsdkcore>=0.2.0: 核心SDK依赖
- python-dotenv: 环境变量管理

## 快速开始

### 人脸检测示例

```python
# 初始化客户端
client = RtasrClient(
    app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
    api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
)

file_path = "D:\\iflytek\\project\\cloudPlatform\\demo\\websdk-java-demo\\src\main\\resources\\audio\\rtasr.pcm"

f = open(file_path, 'rb')
for chunk in client.stream(f):
    logger.info(f"返回结果: {chunk}")
```



更多示例见[demo](https://github.com/iFLYTEK-OP/websdk-python-demo)

## 核心客户端

### IatClient

语音听写流式接口，用于1分钟内的即时语音转文字技术，支持实时返回识别结果，达到一边上传音频一边获得识别文本的效果

### IgrClient

性别年龄识别，即机器对说话者的年龄大小以及性别属性进行分析，可以通过收到的音频数据判定发音人的性别（男，女）及年龄范围（小孩，中年，老人）

### IseClient

通过智能语音技术自动对发音水平进行评价、发音错误、缺陷定位和问题分析的能力接口

### LFasrClient

基于深度全序列卷积神经网络，将长段音频（**5小时以内**）数据转换成文本数据

### QbhClient

歌曲识别技术分为歌曲原声识别以及哼唱识别。歌曲原声识别通过听筒收集音乐播放信息，生成音频指纹，在曲库中识别到对应的歌曲。 哼唱识别通过用户对着话筒哼唱小段歌曲，系统自动识别并检索出所哼唱的歌曲

### RtasrClient

将连续的音频流内容，实时识别返回对应的文字流内容

### TTSClient

语音合成流式接口将文字信息转化为声音信息，同时提供了众多极具特色的发音人（音库）供您选择


## 许可证

请参见LICENSE文件