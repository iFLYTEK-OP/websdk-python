from typing import Optional, List
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from dataclasses import dataclass, asdict


@dataclass
class Audio:
    audio_type: str = None
    file_url: str = None
    name: str = None

    def to_dict(self):
        return asdict(self)


class AudioModerationClient(HttpClient):
    """Client for 音频合规 AudioModeration

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://audit.iflyaisol.com/audit/v2/audio",
                 query_url: Optional[str] = "https://audit.iflyaisol.com/audit/v2/query",
                 notify_url: Optional[str] = None,
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
        self.query_url = query_url
        self.notify_url = notify_url

    def send(self, audio_list: List):
        body = {"audio_list": audio_list, "notify_url": self.notify_url}
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(self.host_url, json=body, params=params)
        return response.text

    def query(self, request_id: str):
        body = {"request_id": request_id}
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(self.query_url, json=body, params=params)
        return response.text
