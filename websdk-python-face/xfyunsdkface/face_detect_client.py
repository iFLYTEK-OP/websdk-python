from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import FaceDetectError


class FaceDetectClient(HttpClient):
    """Client for 人脸检测和属性分析 Face Compare

    Args:
        detect_points: 	检测特征点开关
                        0:只检测人脸，不检测特征点
                        1:检测到人脸之后检测特征点
        detect_property: 检测人脸属性开关
                         0:不检测人脸属性
                         1:检测人脸属性
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://api.xf-yun.com/v1/private/s67c9c78c",
                 detect_points: str = None,
                 detect_property: str = None,
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
        self.detect_points = detect_points
        self.detect_property = detect_property

    def send(self, image_base64: str, image_format: str):
        body = self._build_param(image_base64, image_format)
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, image_base64: str, image_format: str) -> Dict[str, Any]:
        """Build request parameters for Face Detect."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "s67c9c78c": {
                        "service_kind": "face_detect",
                        "detect_points": self.detect_points,
                        "detect_property": self.detect_property,
                        "face_detect_result": {
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
            logger.debug(f"Face Detect Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise FaceDetectError(f"Failed to build parameters: {e}")
