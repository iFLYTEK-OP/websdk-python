from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import LlmOcrError
from dataclasses import dataclass
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.utils import JsonUtils


@dataclass
class LlmOcrParam:
    """大模型识别参数"""

    image_base64: str
    format: Optional[str] = None
    uid: Optional[str] = None
    did: Optional[str] = None
    request_id: Optional[str] = None

    def validate(self) -> None:
        """验证参数有效性"""
        if not self.image_base64:
            raise ValueError("图片信息不能为空")


class LlmOcrClient(HttpClient):
    """Client for 通用大模型识别

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 host_url: Optional[str] = "https://cbm01.cn-huabei-1.xf-yun.com/v1/private/se75ocrbm",
                 imei: Optional[str] = None,
                 imsi: Optional[str] = None,
                 mac: Optional[str] = None,
                 net_type: Optional[str] = None,
                 net_isp: Optional[str] = None,
                 res_id: Optional[str] = None,
                 result_option: Optional[str] = None,
                 result_format: Optional[str] = None,
                 output_type: Optional[str] = None,
                 exif_option: Optional[str] = None,
                 json_element_option: Optional[str] = None,
                 markdown_element_option: Optional[str] = None,
                 sed_element_option: Optional[str] = None,
                 alpha_option: Optional[str] = None,
                 rotation_min_angle: Optional[float] = None,
                 status: Optional[int] = 2,
                 encoding: Optional[str] = "utf8",
                 compress: Optional[str] = "raw",
                 format: Optional[str] = "json",
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
        self.imei = imei
        self.imsi = imsi
        self.mac = mac
        self.net_type = net_type
        self.net_isp = net_isp
        self.res_id = res_id
        self.result_option = result_option
        self.result_format = result_format
        self.output_type = output_type
        self.exif_option = exif_option
        self.json_element_option = json_element_option
        self.markdown_element_option = markdown_element_option
        self.sed_element_option = sed_element_option
        self.alpha_option = alpha_option
        self.rotation_min_angle = rotation_min_angle
        self.status = status
        self.encoding = encoding
        self.compress = compress
        self.format = format

    def send(self, param: LlmOcrParam):
        if param:
            param.validate()
        else:
            raise LlmOcrError("参数不能为空")
        body = self._build_param(param)
        url = Signature.create_signed_url(self.host_url, self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, param: LlmOcrParam) -> Dict[str, Any]:
        """Build request parameters

        Args:
            param: 參數

        Returns:
            Dict[str, Any]: Request parameters

        Raises:
            LlmOcrError: If text encoding fails
        """
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                    "uid": param.uid,
                    "did": param.did,
                    "imei": self.imei,
                    "imsi": self.imsi,
                    "mac": self.mac,
                    "net_type": self.net_type,
                    "net_isp": self.net_isp,
                    "request_id": param.request_id,
                    "res_id": self.res_id,
                },
                "parameter": {
                    "ocr": {
                        "result_option": self.result_option,
                        "result_format": self.result_format,
                        "output_type": self.output_type,
                        "exif_option": self.exif_option,
                        "json_element_option": self.json_element_option,
                        "markdown_element_option": self.markdown_element_option,
                        "sed_element_option": self.sed_element_option,
                        "alpha_option": self.alpha_option,
                        "rotation_min_angle": self.rotation_min_angle,
                        "result": {
                            "encoding": self.encoding,
                            "format": self.format,
                            "compress": self.compress
                        }

                    }
                },
                "payload": {
                    "image": {
                        "encoding": param.format,
                        "image": param.image_base64,
                        "status": self.status,
                        "seq": 0
                    }
                }
            }

            param = JsonUtils.remove_none_values(param)
            logger.debug(f"LLM OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {str(e)}")
            raise LlmOcrError(f"Failed to build parameters: {str(e)}")
