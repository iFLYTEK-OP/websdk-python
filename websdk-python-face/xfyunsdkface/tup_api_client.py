import json
from enum import Enum
from typing import Optional, Union, IO
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import TupApiError
from xfyunsdkcore.log.logger import logger


class TupEnum(Enum):
    AGE = ("age", "年龄分析")
    SEX = ("sex", "性别分析")
    EXPRESSION = ("expression", "表情分析")
    FACE_SCORE = ("face_score", "颜值分析")

    def get_func(self):
        return self.value[0]

    def get_desc(self):
        return self.value[1]


class TupApiClient(HttpClient):
    """Client for 人脸特征分析tuputech Tuputech Api

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 tup_type: TupEnum,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "http://tupapi.xfyun.cn/v1/",
                 status: int = 3,
                 encoding: str = "utf8",
                 compress: str = "raw",
                 format: str = "plain",
                 timeout: int = 120,
                 enable_retry: bool = False,
                 max_retries: int = 3,
                 retry_interval: int = 1):
        super().__init__(host_url,
                         app_id,
                         api_key,
                         api_secret,
                         timeout,
                         enable_retry,
                         max_retries,
                         retry_interval)
        self.status = status
        self.encoding = encoding
        self.compress = compress
        self.format = format
        self.tup_type = tup_type

    def send(self, image_name: str, image_bytes: Union[IO, str], image_url: str = None):
        if image_url is None and image_bytes is None:
            raise TupApiError("image_url和image_bytes不能同时为空")

        params = {"image_name": image_name, "image_url": image_url}
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(params))
        url = self.host_url + self.tup_type.get_func()
        if image_url:
            logger.debug(f"Sending request with audio_url: {image_url}")
            response = self.post(url, headers=header)
        else:
            if isinstance(image_bytes, str):
                with open(image_bytes, "rb") as f:
                    response = self.post(url, headers=header, data=f)
            else:
                response = self.post(url, headers=header, data=image_bytes)
        return response.text
