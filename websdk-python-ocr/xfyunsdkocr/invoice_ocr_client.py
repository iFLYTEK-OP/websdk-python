import json
from enum import Enum
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import InvoiceOCRError


class InvoiceTypeEnum(Enum):
    ID_CARD = ("id_card", "身份证")
    PRINT_INVOICE = ("print_invoice", "机打发票")
    MOTOR_VEHICLE = ("motor_vehicle", "机动车销售发票")
    REFUND_VOUCHER = ("refund_voucher", "退票凭证")
    DIDI_ITINERARY = ("didi_itinerary", "网约车行程单")
    BUS_LICENSE = ("bus_license", "营业执照")
    ORGANIZATION_CODE = ("organization_code", "组织机构代码证")
    HOUSEHOLD_REGISTER = ("household_register", "户口本")
    DRIVE_LICENSE = ("drive_license", "驾驶证")
    VEHICLE_CARD = ("vehicle_card", "行驶证")
    MARRIAGE_CERTIFICATE = ("marriage_certificate", "结婚证")
    VAT_INVOICE = ("vat_invoice", "增值税发票")
    FULL_INVOICE = ("full_invoice", "全电发票")
    ROLL_INVOICE = ("roll_invoice", "增值税发票（卷票）")
    TRAIN_TICKET = ("train_ticket", "火车票")
    TAXI_TICKET = ("taxi_ticket", "出租车发票")
    BUS_PASSENGER = ("bus_passenger", "客运汽车票")
    AIR_ITINERARY = ("air_itinerary", "航空行程单")
    QUOTA_INVOICE = ("quota_invoice", "定额发票")
    ROAD_TOLL = ("road_toll", "过路费发票")
    VEHICLE_QUALIFICATION_CERTIFICATE = ("vehicle_qualification_certificate", "车辆合格证")
    VEHICLE_REGISTRATION_CERTIFICATE = ("vehicle_registration_certificate", "车辆登记证书")
    HYGIENIC_LICENSE = ("hygienic_license", "卫生许可证")
    PATENT_CERTIFICATE = ("patent_certificate", "专利证书")
    SOCIAL_SECURITY_CARD = ("social_security_card", "社保卡")
    CHINESE_PASSPORT = ("chinese_passport", "中国护照")
    TEMPORARY_ID_CARD = ("temporary_id_card", "临时身份证")
    DIVORCE_CERTIFICATE = ("divorce_certificate", "离婚证")
    PROPERTY_CERTIFICATE = ("property_certificate", "房屋所有权证")
    REAL_ESTATE_CERTIFICATE = ("real_estate_certificate", "不动产权证")
    INSTITUTION_LEGAL_PERSON_CERTIFICATE = ("institution_legal_person_certificate", "事业单位法人证")
    NON_TAX_REVENUE_RECEIPT = ("non_tax_revenue_receipt", "非税收入统一票据")
    MAINLAND_TRAVEL_TO_HONGKONG_MACAO_PERMIT = ("mainland_travel_to_hongkong_macao_permit", "往来港澳通行证")
    MAINLAND_TRAVEL_TO_TAIWAN_PERMIT = ("mainland_travel_to_taiwan_permit", "往来台湾通行证")
    HONGKONG_MACAO_TRAVEL_TO_MAINLAND_PERMIT = ("hongkong_macao_travel_to_mainland_permit", "港澳居民来往内地通行证")
    TAIWAN_TRAVEL_TO_MAINLAND_PERMIT = ("taiwan_travel_to_mainland_permit", "台湾居民来往大陆通行证")
    VEHICLE_COMPULSORY_INSURANCE = ("vehicle_compulsory_insurance", "机动车交强险保单")
    VEHICLE_COMMERCIAL_INSURANCE = ("vehicle_commercial_insurance", "机动车商业险保单")
    MOBILE_PAYMENT_VOUCHER = ("mobile_payment_voucher", "手机支付凭证")
    TAX_PAYMENT_CERTIFICATE = ("tax_payment_certificate", "税收完税证明")
    SHOPPING_RECEIPT = ("shopping_receipt", "购物小票")
    TAX_REGISTRATION_CERTIFICATE = ("tax_registration_certificate", "税务登记证")
    CONSTRUCTION_QUALIFICATION_CERTIFICATE = ("construction_qualification_certificate", "建筑企业资质证书")
    QUALITY_MANAGEMENT_CERTIFICATE = ("quality_management_certificate", "质量管理体系证书")
    MEDICAL_INVOICE = ("medical_invoice", "医疗发票")
    BANK_RECEIPT = ("bank_receipt", "银行回单")
    BANK_ACCEPTANCE_BILL = ("bank_acceptance_bill", "银行承兑汇票")
    HONGKONG_ID_CARD = ("hongkong_id_card", "香港身份证")
    MACAO_ID_CARD = ("macao_id_card", "澳门身份证")
    TAIWAN_ID_CARD = ("taiwan_id_card", "台湾身份证")
    BIRTH_MEDICAL_CERTIFICATE = ("birth_medical_certificate", "出生医学证明")
    BUSINESS_CARD = ("business_card", "名片")
    SHIP_TICKET = ("ship_ticket", "船票")
    USED_VEHICLE_INVOICE = ("used_vehicle_invoice", "二手车销售发票")
    HONGKONG_MACAO_TAIWAN_RESIDENCE_PERMIT = ("hongkong_macao_taiwan_residence_permit", "港澳台居民居住证")
    FOREIGNER_RESIDENCE_PERMIT = ("foreigner_residence_permit", "外国人永久居留证")
    TEACHER_CERTIFICATE = ("teacher_certificate", "教师资格证")
    DISABILITY_CERTIFICATE = ("disability_certificate", "残疾人证")
    PHYSICIAN_PRACTICE_CERTIFICATE = ("physician_practice_certificate", "医师执业证")
    CONSTRUCTOR_CERTIFICATE = ("constructor_certificate", "建造师证")
    LAWYER_CERTIFICATE = ("lawyer_certificate", "律师证")
    TOURIST_GUIDE_CERTIFICATE = ("tourist_guide_certificate", "导游证")
    TRANSFER_CHEQUE = ("transfer_cheque", "转账支票")
    BANK_CARD = ("bank_card", "银行卡")

    def get_type(self):
        return self.value[0]

    def get_desc(self):
        return self.value[1]


class InvoiceOCREnum(Enum):
    SINO_SECU = ("国内通用票证识别sinosecu", "https://api.xf-yun.com/v1/private/sc45f0684")
    TICKET_IDENTIFY = ("票据卡证识别", "https://cn-huadong-1.xf-yun.com/v1/inv")

    def get_url(self):
        return self.value[1]

    def get_desc(self):
        return self.value[0]


class InvoiceOCRClient(HttpClient):
    """Client for Invoice OCR
    国内通用票证识别sinosecu & 票据卡证识别

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 host_url: Optional[str] = None,
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

    def identify_sino(self, image_base64: str, image_format: str):
        body = self._build_param(image_base64, image_format)
        url = Signature.create_signed_url(InvoiceOCREnum.SINO_SECU.get_url(), self.api_key, self.api_secret,
                                          "POST")
        response = self.post(url, json=body)
        return response.text

    def identify(self,
                 image_base64: str,
                 image_format: str,
                 invoice_type: InvoiceTypeEnum,
                 uid: str = None,
                 level: int = 1):
        body = self._build_param(image_base64, image_format, invoice_type, uid, level)
        url = Signature.create_signed_url(InvoiceOCREnum.TICKET_IDENTIFY.get_url(), self.api_key, self.api_secret,
                                          "POST")
        response = self.post(url, json=body)
        return response.text

    def _build_param(self,
                     image_base64: str,
                     image_format: str,
                     invoice_type: InvoiceTypeEnum = None,
                     uid: str = None,
                     level: int = 1) -> Dict[str, Any]:
        """Build request parameters for Invoice OCR."""
        try:
            if invoice_type:
                param: Dict[str, Any] = {
                    "header": {
                        "app_id": self.app_id,
                        "status": self.status,
                        "uid": uid
                    },
                    "parameter": {
                        "ocr": {
                            "result": {
                                "encoding": self.encoding,
                                "compress": self.compress,
                                "format": self.format
                            },
                            "type": invoice_type.get_type(),
                            "level": level,
                        }
                    },
                    "payload": {
                        "image": {
                            "encoding": image_format,
                            "image": image_base64,
                            "status": self.status,
                        }
                    }
                }
            else:
                param: Dict[str, Any] = {
                    "header": {
                        "app_id": self.app_id,
                        "status": self.status
                    },
                    "parameter": {
                        "image_recognize": {
                            "output_text_result": {
                                "encoding": self.encoding,
                                "compress": self.compress,
                                "format": self.format
                            }
                        }
                    },
                    "payload": {
                        "image": {
                            "encoding": image_format,
                            "image": image_base64,
                            "status": self.status,
                        }
                    }
                }
            logger.debug(f"Invoice OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise InvoiceOCRError(f"Failed to build parameters: {e}")
