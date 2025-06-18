import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import ItrOCRError


class RecOCREnum(Enum):
    MATH_ARITH = ("拍照速算识别", "math-arith")
    TEACH_PHOTO_PRINT = ("公式识别", "teach-photo-print")

    def get_value(self):
        return self.value[1]

    def get_desc(self):
        return self.value[0]


class ItrOCRClient(HttpClient):
    """Client for Itr OCR
    拍照速算识别 & 公式识别

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 ocr_type: RecOCREnum,
                 host_url: Optional[str] = "https://rest-api.xfyun.cn/v2/itr",
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
        self.ocr_type = ocr_type

    def send(self, image_base64: str):
        body = self._build_param(image_base64)
        header = Signature.get_digest_header(self.host_url, self.api_key, self.api_secret, json.dumps(body))
        response = self.post(self.host_url, json=body, headers=header)
        return response.text

    def _build_param(self, image_base64: str) -> Dict[str, Any]:
        """Build request parameters for Itr OCR."""
        try:
            param: Dict[str, Any] = {
                "common": {
                    "app_id": self.app_id
                },
                "business": {
                    "ent": self.ocr_type.get_value(),
                    "aue": "raw",
                },
                "data": {
                    "image": image_base64
                }
            }
            logger.debug(f"Itr OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise ItrOCRError(f"Failed to build parameters: {e}")
