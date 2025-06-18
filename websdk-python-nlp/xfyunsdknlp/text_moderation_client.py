from typing import Optional, List
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature


class TextModerationClient(HttpClient):
    """Client for 文本合规 TextModeration

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://audit.iflyaisol.com/audit/v2/syncText",
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

    def send(self, content: str, is_match_all: int = 0, lib_ids: List[str] = None, categories: List[str] = None):
        body = {
            "is_match_all": is_match_all,
            "content": content,
            "lib_ids": lib_ids,
            "categories": categories
        }
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(self.host_url, json=body, params=params)
        return response.text

