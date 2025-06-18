import json
from typing import Optional, Dict, Any
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import FingerOCRError


class FingerOCRClient(HttpClient):
    """Client for 指尖文字识别 FingerOCR

    Args:
            cut_w_scale: 根据指尖位置选取ROI（感兴趣区域）的宽度倍数，即设置ROI的宽度是手指宽度的几倍（宽度= cut_w_scale * 手指宽度），默认3.0，取值范围：[0,65536]
            cut_h_scale: 根据指尖位置选取ROI（感兴趣区域）的高度倍数，即设置ROI的高度是手指宽度的几倍（高度= cut_h_scale * 手指宽度），默认2.0，取值范围：[0,65536]
            cut_shift: 根据指尖位置选取ROI（感兴趣区域）的往下平移的倍数，即设置ROI往下平移的距离是ROI宽度的几倍（平移量= cut_shift * 手指宽度），默认0.3，取值范围：[0,1]
            resize_w: 引擎内部处理模块输入图像宽度，取值范围：[1,65536]。若应用端上传图像宽为input_w，scale为缩放系数，则resize_w=input_w*scale。若不缩放直接按原图处理，引擎耗时会变长，建议根据实际情况测试以寻求最佳值
            resize_h: 引擎内部处理模块输入图像高度，取值范围：[1,65536]。若应用端上传图像高为input_h，scale为缩放系数，则resize_h=input_h*scale。若不缩放直接按原图处理，引擎耗时会变长，建议根据实际情况测试以寻求最佳值
            mode:   模式，选择范围：finger,finger+ocr(默认值)。
                    finger模式：只进行手指检测，返回手指位置、方向、宽度等信息
                    finger+ocr模式：进行手指检测以及OCR识别，返回手指指向的字、词、句信息
            method: 方法，取值：dynamic(默认值)。根据指尖位置裁剪感兴趣区域（ROI）进行OCR识别
            ent: 请求引擎类型，只支持fingerocr
    """

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://tyocr.xfyun.cn/v2/ocr",
                 cut_w_scale: float = 3.0,
                 cut_h_scale: float = 2.0,
                 cut_shift: float = 0.3,
                 resize_w: int = 1088,
                 resize_h: int = 1632,
                 mode: str = "finger+ocr",
                 ent: str = "fingerocr",
                 method: str = "dynamic",
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
        self.cut_w_scale = cut_w_scale
        self.cut_h_scale = cut_h_scale
        self.cut_shift = cut_shift
        self.resize_w = resize_w
        self.resize_h = resize_h
        self.mode = mode
        self.ent = ent
        self.method = method

    def send(self, image_base64: str):
        body = self._build_param(image_base64)
        header = Signature.get_digest_header(self.host_url, self.api_key, self.api_secret, json.dumps(body))
        response = self.post(self.host_url, json=body, headers=header)

        return response.text

    def _build_param(self, image_base64: str) -> Dict[str, Any]:
        """Build request parameters for Finger Card OCR."""
        try:
            param: Dict[str, Any] = {
                "common": {
                    "app_id": self.app_id
                },
                "business": {
                    "ent": self.ent,
                    "mode": self.mode,
                    "method": self.method,
                    "cut_w_scale": self.cut_w_scale,
                    "cut_h_scale": self.cut_h_scale,
                    "cut_shift": self.cut_shift,
                    "resize_w": self.resize_w,
                    "resize_h": self.resize_h,
                },
                "data": {
                    "image": image_base64
                }
            }
            logger.debug(f"Finger OCR Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise FingerOCRError(f"Failed to build parameters: {e}")
