import base64
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import AntiSpoofError


class AntiSpoofClient(HttpClient):
    """Client for 静默活体检测 Anti Spoof

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

    def send(self, image_base64: str, image_format: str):
        body = self._build_param(image_base64, image_format)
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, image_base64: str, image_format: str) -> Dict[str, Any]:
        """Build request parameters for AntiSpoof."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "s67c9c78c": {
                        "service_kind": "anti_spoof",
                        "anti_spoof_result": {
                            "encoding": self.encoding,
                            "compress": self.compress,
                            "format": self.format
                        }
                    }
                },
                "payload": {
                    "input1": {
                        "encoding": image_format,
                        "image": image_base64,
                    }
                }
            }
            logger.debug(f"AntiSpoof Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise AntiSpoofError(f"Failed to build parameters: {e}")
