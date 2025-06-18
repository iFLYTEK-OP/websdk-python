# xfyunsdkface

xfyunsdkface是讯飞开放平台人脸相关API的Python SDK，提供[人脸检测](https://www.xfyun.cn/doc/face/xf-face-detect/API.html)、[人脸比对](https://www.xfyun.cn/doc/face/xffaceComparisonRecg/API.html)、[静默活体检测](https://www.xfyun.cn/doc/face/xf-silent-in-vivo-detection/API.html)、[配合式活体检测](https://www.xfyun.cn/doc/face/xf-cooperation-living-body-detection/API.html)、[人脸特征分析](https://www.xfyun.cn/doc/face/face-feature-analysis/ageAPI.html)、[人脸水印照比对](https://www.xfyun.cn/doc/face/faceWaterPhotoComparisonRecg/API.html)等功能的客户端实现。

## 功能特点

- **人脸检测**：检测人脸并返回特征点和属性信息
- **人脸比对**：比对两张人脸的相似度
- **静默活体检测**：判断人脸是否为活体
- **人脸状态分析**：分析人脸状态信息
- **人脸验证**：验证人脸与身份信息是否匹配

## 安装方法

```bash
pip install xfyunsdkface
```

## 依赖说明

- xfyunsdkcore>=0.1.0: 核心SDK依赖
- python-dotenv: 环境变量管理

## 快速开始

### 人脸检测示例

```python
from xfyunsdkface.face_detect_client import FaceDetectClient
import base64

# 读取图片并转换为base64
with open("face.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# 初始化客户端
client = FaceDetectClient(
    app_id="your_app_id",
    api_key="your_api_key",
    api_secret="your_api_secret",
    detect_points="1",  # 检测特征点
    detect_property="1"  # 检测人脸属性
)

# 发送请求
result = client.send(image_base64, "jpg")
print(result)
```

### 人脸比对示例

```python
from xfyunsdkface.face_compare_client import FaceCompareClient
import base64

# 读取两张人脸图片
with open("face1.jpg", "rb") as f:
    face1 = base64.b64encode(f.read()).decode("utf-8")
with open("face2.jpg", "rb") as f:
    face2 = base64.b64encode(f.read()).decode("utf-8")

# 初始化客户端
client = FaceCompareClient(
    app_id="your_app_id",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 发送请求
result = client.send(face1, "jpg", face2, "jpg")
print(result)
```

### 静默活体检测示例

```python
from xfyunsdkface.anti_spoof_client import AntiSpoofClient
import base64

# 读取图片
with open("face.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# 初始化客户端
client = AntiSpoofClient(
    app_id="your_app_id",
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# 发送请求
result = client.send(image_base64, "jpg")
print(result)
```

更多示例见[demo](https://github.com/iFLYTEK-OP/websdk-python-demo)

## 核心客户端

### FaceDetectClient

人脸检测客户端，支持检测人脸位置、特征点和属性信息。

**参数**:
- `detect_points`: 是否检测特征点 (0: 不检测, 1: 检测)
- `detect_property`: 是否检测人脸属性 (0: 不检测, 1: 检测)

### FaceCompareClient

人脸比对客户端，用于计算两张人脸的相似度。

### AntiSpoofClient

静默活体检测客户端，判断输入人脸是否为活体。

### FaceStatusClient

人脸状态分析客户端，分析人脸的状态信息。

### FaceVerifyClient

人脸验证客户端，验证人脸与身份信息是否匹配。


### SilentDetectClient

判断是否为真人活体，该接口用于对一段短视频进行静默活体检测，判断视频中人脸是否为活体。


### TupApiClient

可以检测图像中的人脸并进行一系列人脸相关的特征分析，当前支持识别出包括性别、颜值、年龄、表情多维度人脸信息。

### WatermarkVerifyClient

人脸照片和一个人脸水印照片进行比对，来判断是否为同一个人


## 许可证

请参见LICENSE文件