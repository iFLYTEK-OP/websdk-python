import json
from typing import Optional
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature


class SilentDetectClient(HttpClient):
    """Client for 活体检查sensetime Silent Detect

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://api.xfyun.cn/v1/service/v1/image_identify/silent_detection",
                 get_image: bool = False,
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
        self.get_image = get_image

    def send(self, image_base64: str):
        headers = Signature.get_signature_header(self.app_id, self.api_key, json.dumps({"get_image": self.get_image}))
        data = {"file": image_base64}
        response = self.post(self.host_url, data=data, headers=headers)
        return response.text
