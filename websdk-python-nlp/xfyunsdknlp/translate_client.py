import base64
import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import TranslateError


class TranslateEnum(Enum):
    IST = ("自研翻译", "https://itrans.xfyun.cn/v2/its")
    IST_V2 = ("自研机器翻译（新）", "https://itrans.xf-yun.com/v1/its")
    NIU_TRANS = ("小牛翻译", "https://ntrans.xfyun.cn/v2/ots")

    def get_url(self):
        return self.value[1]

    def get_desc(self):
        return self.value[0]


class TranslateClient(HttpClient):
    """Client for 机械翻译 Translate

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = None,
                 trans_from: str = "cn",
                 trans_to: str = "en",
                 res_id: str = None,
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
        self.trans_from = trans_from
        self.trans_to = trans_to
        self.res_id = res_id

    def send_ist(self, text: str, trans_from: str = None, trans_to: str = None):
        body = self._build_param(text, trans_from, trans_to)
        header = Signature.get_digest_header(TranslateEnum.IST.get_url(), self.api_key, self.api_secret,
                                             json.dumps(body))
        response = self.post(TranslateEnum.IST.get_url(), headers=header, json=body)
        return response.text

    def send_niu_trans(self, text: str, trans_from: str = None, trans_to: str = None):
        body = self._build_param(text, trans_from, trans_to)
        header = Signature.get_digest_header(TranslateEnum.NIU_TRANS.get_url(), self.api_key, self.api_secret,
                                             json.dumps(body))
        response = self.post(TranslateEnum.NIU_TRANS.get_url(), headers=header, json=body)
        return response.text

    def send_ist_v2(self, text: str, trans_from: str = None, trans_to: str = None, res_id: str = None):
        body = self._build_param(text, trans_from, trans_to, res_id, True)
        url = Signature.create_signed_url(TranslateEnum.IST_V2.get_url(), self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, text: str, trans_from: str = None, trans_to: str = None, res_id: str = None,
                     is_niu: bool = False) -> Dict[str, Any]:
        """Build request parameters for Translate."""
        try:
            if is_niu:
                param: Dict[str, Any] = {
                    "header": {
                        "app_id": self.app_id,
                        "status": 3,
                        "res_id": res_id if res_id else self.res_id
                    },
                    "parameter": {
                        "its": {
                            "from": trans_from if trans_from else self.trans_from,
                            "to": trans_to if trans_to else self.trans_to,
                            "result": {}
                        }
                    },
                    "payload": {
                        "input_data": {
                            "encoding": "utf8",
                            "status": 3,
                            "text": base64.b64encode(text.encode("utf-8")).decode('utf-8')
                        }
                    }
                }
            else:
                param: Dict[str, Any] = {
                    "common": {
                        "app_id": self.app_id
                    },
                    "business": {
                        "from": trans_from if trans_from else self.trans_from,
                        "to": trans_to if trans_to else self.trans_to
                    },
                    "data": {
                        "text": base64.b64encode(text.encode("utf-8")).decode('utf-8')
                    }
                }
            logger.debug(f"Translate Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise TranslateError(f"Failed to build parameters: {e}")
