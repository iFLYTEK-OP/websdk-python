# xfyunsdkocr

xfyunsdkocr是讯飞开放平台图像识别相关API的Python SDK，提供[银行卡识别intsig](https://www.xfyun.cn/doc/words/bankCardRecg/API.html)、[名片识别intsig](https://www.xfyun.cn/doc/words/businessCardRecg/API.html)、[指尖文字识别](https://www.xfyun.cn/doc/words/finger-word-discern/API.html)、[印刷文字识别](https://www.xfyun.cn/doc/words/multi_print_recognition/API.html)、[手写文字识别](https://www.xfyun.cn/doc/words/wordRecg/API.html)、[营业执照识别intsig](https://www.xfyun.cn/doc/words/businessLicenseRecg/API.html)、[出租车发票识别](https://www.xfyun.cn/doc/words/taxi_ticket/newAPI.html)、[火车票识别](https://www.xfyun.cn/doc/words/train_ticket/API.html)、[增值税发票识别intsig](https://www.xfyun.cn/doc/words/VAT-invoice-recg/API.html)、[身份证识别intsig](https://www.xfyun.cn/doc/words/idCardRecg/API.html)、[印刷文字识别intsig](https://www.xfyun.cn/doc/words/printed-word-recognition/API.html)、[通用文字识别intsig](https://www.xfyun.cn/doc/words/universal-character-recognition/API.html)、[票据卡证识别](https://www.xfyun.cn/doc/words/TicketIdentification/API.html)、[公式识别](https://www.xfyun.cn/doc/words/formula-discern/API.html)、[拍照速算识别](https://www.xfyun.cn/doc/words/photo-calculate-recg/API.html)、[驾驶证识别](https://www.xfyun.cn/doc/words/DriversLicenseRecg/API.html)、[车牌识别](https://www.xfyun.cn/doc/words/vehicleLicensePlateRecg/API.html)、[行驶证识别](https://www.xfyun.cn/doc/words/vehicleRecg/API.html)、[图片还原文档](https://www.xfyun.cn/doc/words/picture-document-reconstruction/API.html)、[场景识别](https://www.xfyun.cn/doc/image/scene-recg/API.html)、[物体识别](https://www.xfyun.cn/doc/image/object-recg/API.html)、[场所识别](https://www.xfyun.cn/doc/image/place-recg/API.html)等功能的客户端实现。

## 功能特点

- **银行卡识别**：识别银行卡信息
- **名片识别**：识别名片信息
- **指尖文字识别**：图片中用户手指出的内容识别
- **文字识别**：印刷文字识别和手写文字识别
- **通用文字识别**：营业执照识别、出租车发票识别、火车票识别、增值税发票识别、身份证识别、多语种文字识别、通用文字识别
- **通用文字识别Intsig**：身份证识别、营业执照识别、增值税发票识别、印刷文字识别（多语种）、通用文本识别（多语种）
- **票据卡证识别**：国内通用票证识别sinosecu、票据卡证识别
- **数学识别**：拍照速算识别、公式识别
- **车相关识别**：行驶证识别、驾驶证识别、车牌识别
- **图片还原文档**：识别图片 , 还原成文档
- **场地识别**：场景识别、物体识别、场所识别

## 安装方法

```bash
pip install xfyunsdkocr
```

## 依赖说明

- xfyunsdkcore>=0.1.0: 核心SDK依赖
- python-dotenv: 环境变量管理

## 快速开始

### 同声传译

```python
from xfyunsdkocr.pd_rec_client import PDRecClient

        # 获取识别文件路径
        file_path = os.path.join(os.path.dirname(__file__), 'resources', 'pdrec.jpg')
        with open(file_path, "rb") as file:
            encoded_string = base64.b64encode(file.read())

    # 初始化客户端
    client = PDRecClient(
        app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
        api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
        api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
    )

# 发送请求
        resp = client.generate(encoded_string.decode("utf-8"), "1", "jpg")
        # 保存文件
        save_byte_to_file(resp, "123.docx")
```

更多示例见[demo](https://github.com/iFLYTEK-OP/websdk-python-demo)

## 核心客户端

### BankCardClient

对银行卡进行识别，返回银行卡原件上的银行卡卡号、有效日期、发卡行、卡片类型（借记卡&信用卡）、持卡人姓名（限信用卡）等信息

### BusinessCardClient

纸质名片进行识别，返回名片上的姓名、手机、电话、公司、部门、职位、传真、邮箱、网站、地址等关键信息

### FingerOCRClient

指尖文字识别，可检测图片中指尖位置，将指尖处文字转化为计算机可编码的文字

### WordOCRClient

基于深度神经网络模型的端到端文字识别系统和讯飞自研的行业先进的光学字符识别技术，将图片（来源如扫描仪或数码相机）中的印刷/手写字体，支持扫描体以及复杂自然场景下的文字识别，直接转换为可编辑文本

### ImageWordOCRClient

通用文字识别 , 见功能特点介绍

### IntsigOCRClient

通用文字识别Intsig , 见功能特点介绍

### InvoiceOCRClient

票据卡证识别, 见功能特点介绍

### ItrOCRClient

数学识别, 见功能特点介绍

### JDOCRClient

车相关识别, 见功能特点介绍

### PDRecClient

基于深度神经网络模型的端到端文档重建技术，可以识别文档、合同等形式的图片，生成保留内容格式的docx、pptx或xlsx文档

### RecOCRClient

场地识别, 见功能特点介绍


## 许可证

请参见LICENSE文件