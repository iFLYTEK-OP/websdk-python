import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import ImageWordOCRError


class ImageWordOCREnum(Enum):
    BUSINESS_LICENSE = ("营业执照识别", "sff4ea3cf", "bus_license", "sff4ea3cf_data_1")
    TAXI_INVOICE = ("出租车发票识别", "sb6db0171", "taxi_ticket", "sb6db0171_data_1")
    TRAIN_TICKET = ("火车票识别", "s19cfe728", "train_ticket", "s19cfe728_data_1")
    INVOICE = ("增值税发票识别", "s824758f1", "vat_invoice", "s824758f1_data_1")
    IDCARD = ("身份证识别", "s5ccecfce", "id_card", "s5ccecfce_data_1")
    PRINTED_WORD = ("多语种文字识别", "s00b65163", "vat_invoice", "s00b65163_data_1")
    COMMON_WORD = ("通用文字识别", "sf8e6aca1", "vat_invoice", "sf8e6aca1_data_1")

    def get_desc(self):
        return self.value[0]

    def get_service(self):
        return self.value[1]

    def get_template(self):
        return self.value[2]

    def get_payload(self):
        return self.value[3]


class ImageWordOCRClient(HttpClient):
    """Client for Image Word OCR
    营业执照识别  出租车发票识别  火车票识别  增值税发票识别  身份证识别  印刷文字识别  通用文字识别  通用文字识别（intsig）

    Args:
    """

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 ocr_type: ImageWordOCREnum = ImageWordOCREnum.COMMON_WORD,
                 host_url: Optional[str] = "https://api.xf-yun.com/v1/private/",
                 status: int = 3,
                 encoding: str = "utf8",
                 compress: str = "raw",
                 format: str = "json",
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
        self.ocr_type = ocr_type

    def send(self, image_base64: str, image_format: str):
        body = self._build_param(image_base64, image_format, self.ocr_type)
        url = Signature.create_signed_url(self.host_url + self.ocr_type.get_service(), self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, image_base64: str, image_format: str, enum: ImageWordOCREnum) -> Dict[str, Any]:
        """Build request parameters for Image Word OCR."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    enum.get_service(): {
                        "result": {
                            "encoding": self.encoding,
                            "compress": self.compress,
                            "format": self.format,
                        }
                    }
                },
                "payload": {
                    enum.get_payload(): {
                        "encoding": image_format,
                        "image": image_base64,
                        "status": self.status,
                    }
                }
            }

            if ImageWordOCREnum.COMMON_WORD == enum:
                param["parameter"][enum.get_service()]["category"] = "ch_en_public_cloud"
            elif ImageWordOCREnum.PRINTED_WORD == enum:
                param["parameter"][enum.get_service()]["category"] = "mix0"
            else:
                param["parameter"][enum.get_service()]["template_list"] = enum.get_template()

            logger.debug(f"Image Word OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise ImageWordOCRError(f"Failed to build parameters: {e}")
