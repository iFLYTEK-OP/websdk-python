import json
from typing import Optional
from xfyunsdkcore.http_client import HttpClient
from enum import Enum
from xfyunsdkcore.signature import Signature


class LTPEnum(Enum):
    CWS = ("cws", "中文分词")
    NER = ("ner", "命名实体识别")
    DP = ("dp", "依存句法分析")
    SRL = ("srl", "语义角色标注")
    SDP = ("sdp", "语义依存 (依存树) 分析")
    SDGP = ("sdgp", "语义依存 (依存图) 分析")
    KE = ("ke", "关键词提取")
    POS = ("pos", "词性标注")

    def get_func(self):
        return self.value[0]

    def get_desc(self):
        return self.value[1]


class LTPClient(HttpClient):
    """Client for 语意分析 LTP

    Args:
    """

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: Optional[str] = None,
                 host_url: Optional[str] = "https://ltpapi.xfyun.cn/v1/",
                 type: str = "dependent",
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
        self.type = type

    def send(self, text: str, enum: LTPEnum):
        body = {"type": self.type}
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(body))
        text = {"text": text}
        response = self.post(self.host_url + enum.get_func(), data=text, headers=header)
        return response.text
