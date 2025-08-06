from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import JDOCRError


class JDOCREnum(Enum):
    JD_OCR_VEHICLE = ("行驶证识别", "jd_ocr_vehicle", "vehicleLicenseRes", "jd_ocr_vehicle", "vehicleLicense")
    JD_OCR_DRIVER = ("驾驶证识别", "jd_ocr_driver", "driverLicenseRes", "jd_ocr_driver", "driverLicense")
    JD_OCR_CAR = ("车牌识别", "jd_ocr_car", "carLicenseRes", "jd_ocr_car", "carImgBase64Str")

    def get_desc(self):
        return self.value[0]

    def get_value(self):
        return self.value[1]

    def get_service(self):
        return self.value[2]

    def get_parameter(self):
        return self.value[3]

    def get_payload(self):
        return self.value[4]


class JDOCRClient(HttpClient):
    """Client for JD OCR
    行驶证识别  驾驶证识别  车牌识别

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 ocr_type: JDOCREnum,
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
        self.ocr_type = ocr_type
        self.status = status
        self.encoding = encoding
        self.compress = compress
        self.format = format

    def send(self, image_base64: str, image_format: str):
        body = self._build_param(image_base64, image_format)
        url = Signature.create_signed_url(self.host_url + self.ocr_type.get_value(), self.api_key, self.api_secret, "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self, image_base64: str, image_format: str) -> Dict[str, Any]:
        """Build request parameters for JD OCR."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    self.ocr_type.get_parameter(): {
                        self.ocr_type.get_service(): {
                            "encoding": self.encoding,
                            "format": self.format,
                            "compress": self.compress,
                        }
                    }
                },
                "payload": {
                    self.ocr_type.get_payload(): {
                        "encoding": image_format,
                        "image": image_base64,
                        "status": self.status
                    }
                }
            }
            logger.debug(f"{self.ocr_type} OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise JDOCRError(f"Failed to build parameters: {e}")
