import json
from typing import Optional
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature


class SaClient(HttpClient):
    """Client for 情感分析 Sa

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://ltpapi.xfyun.cn/v2/sa",
                 type: str = "dependent",
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
        self.type = type

    def send(self, text: str):
        body = {"type": self.type}
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        text = {"text": text}
        response = self.post(self.host_url, data=text, headers=header)
        return response.text
