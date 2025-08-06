import json
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import BusinessCardError


class BusinessCardClient(HttpClient):
    """Client for 名片识别 Business Card"""

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://webapi.xfyun.cn/v1/service/v1/ocr/business_card",
                 pic_required: str = "0",
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
        self.pic_required = pic_required

    def send(self, image_base64: str, imei: str = None, osid: str = None, ua: str = None):
        param = self._build_param(imei, osid, ua)
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(param))
        data = {"image": image_base64}
        response = self.post(self.host_url, data=data, headers=header)

        return response.text

    def _build_param(self, imei: str = None, osid: str = None, ua: str = None) -> Dict[str, Any]:
        """Build request parameters for Business Card API."""
        try:
            param: Dict[str, Any] = {
                "engine_type": "business_card",
                "pic_required": self.pic_required,
                "imei": imei,
                "osid": osid,
                "ua": ua,
            }
            logger.debug(f"Business Card Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise BusinessCardError(f"Failed to build parameters: {e}")
