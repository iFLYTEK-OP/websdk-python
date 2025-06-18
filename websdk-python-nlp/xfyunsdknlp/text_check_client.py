import base64
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import TextCheckError


class TextCheckClient(HttpClient):
    """Client for 文本纠错 TextCheck

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://api.xf-yun.com/v1/private/s9a87e3ec",
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

    def send(self, text: str):
        body = self._build_param(text)
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, text: str) -> Dict[str, Any]:
        """Build request parameters for Text Check."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "s9a87e3ec": {
                        "result": {
                            "encoding": self.encoding,
                            "compress": self.compress,
                            "format": self.format
                        }
                    }
                },
                "payload": {
                    "input": {
                        "encoding": self.encoding,
                        "compress": self.compress,
                        "format": self.format,
                        "status": self.status,
                        "text": base64.b64encode(text.encode("utf-8")).decode('utf-8'),
                    }
                }
            }
            logger.debug(f"Text Check Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise TextCheckError(f"Failed to build parameters: {e}")
