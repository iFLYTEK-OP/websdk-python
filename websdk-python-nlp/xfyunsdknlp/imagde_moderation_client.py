from typing import Optional
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import ModerationError


class ImageModerationClient(HttpClient):
    """Client for 图片合规 ImageModeration

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://audit.iflyaisol.com/audit/v2/image",
                 biz_type: Optional[str] = None,
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
        self.biz_type = biz_type

    def send(self, image_base64: str = None, image_url: str = None):
        if image_base64:
            mode_type = "base64"
            body = {"content": image_base64, "biz_type": self.biz_type}
        elif image_url:
            mode_type = "link"
            body = {"content": image_url, "biz_type": self.biz_type}
        else:
            raise ModerationError("图片信息不能为空")
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret, mode_type)
        response = self.post(self.host_url, json=body, params=params)
        return response.text

