import json
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import BankCardError


class BankCardClient(HttpClient):
    """Client for 银行卡识别 Bank Card"""

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://webapi.xfyun.cn/v1/service/v1/ocr/bankcard",
                 card_number_image: str = "0",
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
        self.card_number_image = card_number_image

    def send(self, image_base64: str):
        param = self._build_param()
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(param))
        data = {"image": image_base64}
        response = self.post(self.host_url, data=data, headers=header)

        return response.text

    def _build_param(self) -> Dict[str, Any]:
        """Build request parameters for Bank Card API."""
        try:
            param: Dict[str, Any] = {
                "engine_type": "bankcard",
                "card_number_image": self.card_number_image,
            }
            logger.debug(f"Bank Card Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise BankCardError(f"Failed to build parameters: {e}")
