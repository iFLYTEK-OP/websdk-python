import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import WordOCRError


class WordOCREnum(Enum):
    GENERAL = ("印刷文字识别", "https://webapi.xfyun.cn/v1/service/v1/ocr/general", "POST")
    HANDWRITING = ("手写文字识别", "https://webapi.xfyun.cn/v1/service/v1/ocr/handwriting", "POST")

    def get_url(self):
        return self.value[1]

    def get_method(self):
        return self.value[2]

    def get_desc(self):
        return self.value[0]


class WordOCRClient(HttpClient):
    """Client for General Words
    印刷文字识别 & 手写文字识别

    Args:
            language: 文本语言   cn|en - 中英文混合   en -英文
            location: 是否返回文本位置信息  默认false
    """

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://webapi.xfyun.cn/v1/service/v1/ocr",
                 language: str = "cn|en",
                 location: str = "false",
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
        self.language = language
        self.location = location

    def general(self, image_base64: str):
        body = self._build_param()
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        data = {"image": image_base64}
        response = self.post(WordOCREnum.GENERAL.get_url(), data=data, headers=header)

        return response.text

    def handwriting(self, image_base64: str):
        body = self._build_param()
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        data = {"image": image_base64}
        response = self.post(WordOCREnum.HANDWRITING.get_url(), data=data, headers=header)

        return response.text

    def _build_param(self) -> Dict[str, Any]:
        """Build request parameters for General Words OCR."""
        try:
            param: Dict[str, Any] = {
                "language": self.language,
                "location": self.location,
            }
            logger.debug(f"General Words OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise WordOCRError(f"Failed to build parameters: {e}")
