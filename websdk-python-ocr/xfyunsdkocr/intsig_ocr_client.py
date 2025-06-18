import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import IntsigOCRError


class IntsigOCREnum(Enum):
    IDCARD = ("身份证识别", "idcard", "https://webapi.xfyun.cn/v1/service/v1/ocr/idcard")
    BUSINESS_LICENSE = ("营业执照识别", "business_license", "https://webapi.xfyun.cn/v1/service/v1/ocr/business_license")
    INVOICE = ("增值税发票识别", "invoice", "https://webapi.xfyun.cn/v1/service/v1/ocr/invoice")
    RECOGNIZE_DOCUMENT = ("印刷文字识别（多语种）", "recognize_document", "https://webapi.xfyun.cn/v1/service/v1/ocr/recognize_document")
    COMMON_WORD = ("通用文本识别（多语种）", "hh_ocr_recognize_doc", "https://api.xf-yun.com/v1/private/hh_ocr_recognize_doc")

    def get_desc(self):
        return self.value[0]

    def get_value(self):
        return self.value[1]

    def get_url(self):
        return self.value[2]

    def get_result(self):
        return self.value[3]


class IntsigOCRClient(HttpClient):
    """Client for Intsig OCR
     身份证识别 营业执照识别 增值税发票识别  通用文字识别

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 ocr_type: IntsigOCREnum,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://webapi.xfyun.cn",
                 head_portrait: str = "0",
                 crop_image: str = "0",
                 id_number_image: str = "0",
                 recognize_mode: str = "0",
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
        self.head_portrait = head_portrait
        self.crop_image = crop_image
        self.id_number_image = id_number_image
        self.recognize_mode = recognize_mode
        self.ocr_type = ocr_type

    def send(self, image_base64: str, image_format: str = None):
        body = self._build_param(image_base64, image_format)
        if self.ocr_type == IntsigOCREnum.COMMON_WORD:
            url = Signature.create_signed_url(self.ocr_type.get_url(), self.api_key, self.api_secret, "POST")
            response = self.post(url, json=body)
        else:
            data = {"image": image_base64}
            header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
            response = self.post(self.ocr_type.get_url(), data=data, headers=header)
        return response.text

    def _build_param(self, image_base64: str, image_format: str = None) -> Dict[str, Any]:
        """Build request parameters for Intsig OCR."""
        try:
            if self.ocr_type == IntsigOCREnum.IDCARD:
                param = {
                    "engine_type": self.ocr_type.get_value(),
                    "head_portrait": self.head_portrait,
                    "crop_image": self.crop_image,
                    "id_number_image": self.id_number_image,
                    "recognize_mode": self.recognize_mode
                }
            elif self.ocr_type == IntsigOCREnum.COMMON_WORD:
                param = {
                    "header": {
                        "app_id": self.app_id,
                        "status": 3,
                    },
                    "parameter": {
                        self.ocr_type.get_value(): {
                            "recognizeDocumentRes": {
                                "encoding": "utf8",
                                "format": "json",
                                "compress": "raw",
                            }
                        }
                    },
                    "payload": {
                        "image": {
                            "encoding": image_format,
                            "image": image_base64,
                            "status": 3
                        }
                    }
                }
            else:
                param = {
                    "engine_type": self.ocr_type.get_value()
                }
            logger.debug(f"Intsig OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise IntsigOCRError(f"Failed to build parameters: {e}")
