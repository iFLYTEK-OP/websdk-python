# xfyunsdkcore

xfyunsdkcore是讯飞开放平台Web API的核心Python SDK，提供HTTP客户端、签名生成和通用工具类，为其他业务模块提供基础支持。

## 功能特点

- **HTTP客户端**：支持同步/异步请求，内置重试机制
- **签名工具**：提供多种签名算法实现，支持不同API认证需求
- **通用工具**：包含字符串处理、JSON转换和加密工具类

## 安装方法

```bash
pip install xfyunsdkcore
```

## 依赖说明

- httpx: HTTP客户端库
- websocket-client<2.0.0: WebSocket支持

## 快速开始

### HTTP客户端使用

```python
from xfyunsdkcore.http_client import HttpClient

# 初始化客户端
client = HttpClient(
    host_url="https://api.xfyun.cn",
    app_id="your_app_id",
    api_key="your_api_key",
    api_secret="your_api_secret",
    timeout=30,
    enable_retry=True
)

# 发送GET请求
response = client.get("/v1/service")
print(response.json())

# 发送POST请求
response = client.post("/v1/service", json={"key": "value"})
print(response.json())
```

### 异步请求示例

```python
import asyncio
from xfyunsdkcore.http_client import HttpClient

async def main():
    client = HttpClient(host_url="https://api.xfyun.cn")
    response = await client.async_get("/v1/service")
    print(response.json())

asyncio.run(main())
```

### 签名生成

```python
from xfyunsdkcore.signature import Signature

# 创建签名URL
api_url = "wss://ws-api.xfyun.cn/v1/iat"
signed_url = Signature.create_signed_url(
    api_url=api_url,
    api_key="your_api_key",
    api_secret="your_api_secret"
)
print(signed_url)
```

## 核心模块

### HttpClient

提供HTTP请求的核心功能，支持：
- 同步/异步请求
- 超时控制
- 重试机制
- 文件上传

### Signature

提供多种签名实现：
- `create_signed_url`: WebSocket签名URL生成
- `get_signature_header`: 请求头签名生成
- `get_digest_header`: 摘要认证头生成

### 工具类

- **StringUtils**: 字符串处理工具
- **JsonUtils**: JSON序列化/反序列化
- **CryptTools**: 加密工具，支持HMAC和MD5

## 许可证

请参见LICENSE文件