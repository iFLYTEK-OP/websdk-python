import base64
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import ResumeGenError


class ResumeGenClient(HttpClient):
    """Client for 简历生成 Resume Generation"""

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://cn-huadong-1.xf-yun.com/v1/private/s73f4add9",
                 encoding="utf8",
                 compress="raw",
                 format="json",
                 status=3,
                 timeout=120,
                 enable_retry=False,
                 max_retries=3,
                 retry_interval=1):
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
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=self._build_param(text))
        return response.text

    def _build_param(self, text: str) -> Dict[str, Any]:
        """Build request parameters for Oral API."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "ai_resume": {
                        "resData": {
                            "encoding": self.encoding,
                            "compress": self.compress,
                            "format": self.format
                        }
                    }
                },
                "payload": {
                    "reqData": {
                        "encoding": self.encoding,
                        "compress": self.compress,
                        "format": self.format,
                        "status": self.status,
                        "text": base64.b64encode(text.encode("utf-8")).decode('utf-8')
                    }
                }
            }
            logger.debug(f"Resume Generate Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise ResumeGenError(f"Failed to build parameters: {e}")
