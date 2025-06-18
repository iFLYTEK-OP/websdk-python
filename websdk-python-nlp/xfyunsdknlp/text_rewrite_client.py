import base64
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import TextRewriteError


class TextRewriteClient(HttpClient):
    """Client for 文本改写 TextRewrite

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://api.xf-yun.com/v1/private/se3acbe7f",
                 level: str = "L1",
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
        self.level = level

    def send(self, text: str, level: str = None):
        body = self._build_param(text, level)
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, text: str, level: str = None) -> Dict[str, Any]:
        """Build request parameters for Text Check."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "se3acbe7f": {
                        "result": {
                            "encoding": self.encoding,
                            "compress": self.compress,
                            "format": self.format
                        },
                        "level": f"<{level if level else self.level}>"
                    }
                },
                "payload": {
                    "input1": {
                        "encoding": self.encoding,
                        "compress": self.compress,
                        "format": self.format,
                        "status": self.status,
                        "text": base64.b64encode(text.encode("utf-8")).decode('utf-8'),
                    }
                }
            }
            logger.debug(f"Text Rewrite Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise TextRewriteError(f"Failed to build parameters: {e}")
