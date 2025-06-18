from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import FaceCompareError


class FaceCompareClient(HttpClient):
    """Client for 人脸比对 Face Compare

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://api.xf-yun.com/v1/private/s67c9c78c",
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

    def send(self, image_base64_first: str, image_format_first: str,
             image_base64_sec: str, image_format_sec: str):
        body = self._build_param(image_base64_first, image_format_first, image_base64_sec, image_format_sec)
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, image_base64_first: str, image_format_first: str,
                     image_base64_sec: str, image_format_sec: str) -> Dict[str, Any]:
        """Build request parameters for Face Compare."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "s67c9c78c": {
                        "service_kind": "face_compare",
                        "face_compare_result": {
                            "encoding": self.encoding,
                            "compress": self.compress,
                            "format": self.format
                        }
                    }
                },
                "payload": {
                    "input1": {
                        "encoding": image_format_first,
                        "image": image_base64_first,
                    },
                    "input2": {
                        "encoding": image_format_sec,
                        "image": image_base64_sec,
                    }
                }
            }
            logger.debug(f"Face Compare Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise FaceCompareError(f"Failed to build parameters: {e}")
