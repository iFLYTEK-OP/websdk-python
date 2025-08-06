import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import RecOCRError


class RecOCREnum(Enum):
    SCENE = ("场景识别", "http://tupapi.xfyun.cn/v1/scene")
    CURRENCY = ("物体识别", "http://tupapi.xfyun.cn/v1/currency")
    PLACE = ("场所识别", "https://api.xf-yun.com/v1/private/s5833e7f6")

    def get_url(self):
        return self.value[1]

    def get_desc(self):
        return self.value[0]


class RecOCRClient(HttpClient):
    """Client for Rec OCR
     场景识别 & 物体识别 & 场所识别

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = None,
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

    def scene(self, image_name: str, image_url: str = None, file=None):
        body = _build_param(image_name, image_url)
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        response = self.post(RecOCREnum.SCENE.get_url(), data=file, headers=header)

        return response.text

    def currency(self, image_name: str, image_url: str = None, file=None):
        body = _build_param(image_name, image_url)
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        response = self.post(RecOCREnum.CURRENCY.get_url(), data=file, headers=header)
        return response.text

    def place(self, image_base64: str, image_format: str):
        body = self._build_place_param(image_base64, image_format)
        url = Signature.create_signed_url(RecOCREnum.PLACE.get_url(), self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_place_param(self, image_base64: str, image_format: str) -> Dict[str, Any]:
        """Build request parameters for Place Rec."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": 3
                },
                "parameter": {
                    "s5833e7f6": {
                        "result": {
                            "encoding": "utf8",
                            "format": "json",
                            "compress": "raw"
                        },
                        "func": "image/place"
                    }
                },
                "payload": {
                    "data1": {
                        "encoding": image_format,
                        "image": image_base64,
                        "status": 3
                    }
                }
            }
            logger.debug(f"Place Rec Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise RecOCRError(f"Failed to build parameters: {e}")


def _build_param(image_name: str, image_url: str = None) -> Dict[str, Any]:
    """Build request parameters for Rec OCR."""
    try:
        param: Dict[str, Any] = {
            "image_name": image_name,
            "image_url": image_url
        }
        logger.debug(f"Rec OCR Request Parameters: {param}")
        return param
    except Exception as e:
        logger.error(f"Failed to build parameters: {e}")
        raise RecOCRError(f"Failed to build parameters: {e}")
