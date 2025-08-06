import time
from typing import Optional, Dict
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from enum import Enum
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import LFasrError


class LFasrEnum(Enum):
    UPLOAD = ("文件上传", "https://raasr.xfyun.cn/v2/api/upload", "POST")
    GET_RESULT = ("查询结果", "https://raasr.xfyun.cn/v2/api/getResult", "POST")

    def get_url(self):
        return self.value[1]

    def get_method(self):
        return self.value[2]

    def get_desc(self):
        return self.value[0]


def param_check(param, file):
    if param is None:
        raise LFasrError("参数不能为空")
    elif param["fileName"] is None or param["fileSize"] is None:
        raise LFasrError(f"位置的audioMode参数: {param['audioMode']}")
    elif param["audioMode"] not in ["fileStream", "urlLink"]:
        raise LFasrError(f"位置的audioMode参数: {param['audioMode']}")
    elif param["audioMode"] == "fileStream" and file is None:
        raise LFasrError("audioMode为fileStream时，文件不能为空")
    elif param["audioMode"] == "urlLink" and param["audioUrl"] is None:
        raise LFasrError("audioMode为urlLink时，audioUrl不能为空")


class LFasrClient(HttpClient):
    """Client for 录音文件转写 Long Form ASR"""

    def __init__(self, app_id: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 timeout=30,
                 enable_retry=False,
                 max_retries=3,
                 retry_interval=1):
        super().__init__("https://raasr.xfyun.cn", app_id,
                         secret_key,
                         None,
                         timeout,
                         enable_retry,
                         max_retries,
                         retry_interval)

    def send(self, lf_asr_enum, param: Dict, file=None):
        # 构建请求参数
        timestamp = str(int(time.time()))
        signature = Signature.get_signature(self.app_id, timestamp, self.api_key)
        param.update({
            "appId": self.app_id,
            "signa": signature,
            "ts": timestamp
        })
        # 构建请求头
        headers = {
            "Content-Type": "application/octet-stream" if file else "application/json",
        }

        # 拼接url
        url = lf_asr_enum.get_url()

        logger.debug(f"{lf_asr_enum.get_desc()}请求URL：{url}，参数：{param}")

        # 发送请求
        method = lf_asr_enum.get_method()
        if file:
            response = self.post(url, headers=headers, data=file, params=param)
        elif method == "POST":
            response = self.post(url, headers=headers, json=None, params=param)
        else:
            response = self.get(url, headers=headers)

        return response.text

    def upload(self, param: Dict, file_path: str = None):
        param_check(param, file_path)

        if param["audioMode"] == "fileStream":
            with open(file_path, "rb") as f:
                return self.send(LFasrEnum.UPLOAD, param, f.read(param["fileSize"]))
        else:
            return self.send(LFasrEnum.UPLOAD, param)

    def get_result(self, param: Dict):
        if param is None:
            raise LFasrError("参数不能为空")
        elif param["orderId"] is None:
            raise LFasrError("转写订单号不能为空")
        return self.send(LFasrEnum.GET_RESULT, param, False)
