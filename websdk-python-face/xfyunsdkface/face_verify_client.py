import json
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import FaceVerificationError


class FaceVerifyClient(HttpClient):
    """Client for 人脸比对sensetime Face Verify

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://api.xfyun.cn/v1/service/v1/image_identify/face_verification",
                 get_image: bool = False,
                 auto_rotate: bool = False,
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
        self.auto_rotate = auto_rotate
        self.get_image = get_image

    def send(self, image_base64_first: str, image_base64_sec: str):
        body = self._build_param()
        headers = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        data = {"first_image": image_base64_first, "second_image": image_base64_sec}
        response = self.post(self.host_url, data=data, headers=headers)
        return response.text

    def _build_param(self) -> Dict[str, Any]:
        """Build request parameters for Face Verify."""
        try:
            param: Dict[str, Any] = {
                "get_image": self.get_image,
                "auto_rotate": self.auto_rotate,
            }
            logger.debug(f"Face Verify Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise FaceVerificationError(f"Failed to build parameters: {e}")
