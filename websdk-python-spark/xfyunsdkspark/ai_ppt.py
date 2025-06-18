import time
from typing import Optional
from xfyunsdkcore.model.ai_ppt_model import PPTSearch, PPTCreate
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from enum import Enum
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import AIPPTError


class AIPPTEnum(Enum):
    LIST = ("PPT主题列表查询", "https://zwapi.xfyun.cn/api/ppt/v2/template/list", "POST")
    CREATE = ("PPT生成", "https://zwapi.xfyun.cn/api/ppt/v2/create", "POST")
    CREATE_OUTLINE = ("大纲生成", "https://zwapi.xfyun.cn/api/ppt/v2/createOutline", "POST")
    CREATE_OUTLINE_BY_DOC = ("自定义大纲生成", "https://zwapi.xfyun.cn/api/ppt/v2/createOutlineByDoc", "POST")
    CREATE_PPT_BY_OUTLINE = ("通过大纲生成PPT", "https://zwapi.xfyun.cn/api/ppt/v2/createPptByOutline", "POST")
    PROGRESS = ("PPT进度查询", "https://zwapi.xfyun.cn/api/ppt/v2/progress?sid=%s", "GET")

    def get_url(self):
        return self.value[1]

    def get_method(self):
        return self.value[2]

    def get_desc(self):
        return self.value[0]


def null_check(param):
    if param is None:
        raise AIPPTError("参数不能为空")


class AIPPTClient(HttpClient):
    """Client for 智能PPT ai ppt"""

    def __init__(self, app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 timeout=30,
                 enable_retry=False,
                 max_retries=3,
                 retry_interval=1):
        super().__init__("https://zwapi.xfyun.cn", app_id,
                         api_key,
                         api_secret,
                         timeout,
                         enable_retry,
                         max_retries,
                         retry_interval)

    def send(self, ai_ppt_enum, body=None, file=None, is_form=False, *param):
        # 构建请求头
        timestamp = str(int(time.time()))
        signature = Signature.get_signature(self.app_id, timestamp, self.api_secret)
        headers = {
            "signature": signature,
            "appId": self.app_id,
            "timestamp": timestamp
        }

        # 拼接url
        url = ai_ppt_enum.get_url()
        if param:
            url = ai_ppt_enum.get_url() % param

        logger.debug(f"{ai_ppt_enum.get_desc()}请求URL：{url}，入参：{body}")

        # 发送请求
        method = ai_ppt_enum.get_method()
        if file or is_form:
            response = self.post(url, headers=headers, data=body, files=file)
        elif method == "POST":
            response = self.post(url, headers=headers, json=body)
        else:
            response = self.get(url, headers=headers)

        return response.text

    def list(self, ppt_search: PPTSearch):
        null_check(ppt_search)
        return self.send(AIPPTEnum.LIST, ppt_search.to_dict())

    def create(self, ppt_create: PPTCreate):
        null_check(ppt_create)
        ppt_create.create_check()
        # 请求体
        body = ppt_create.to_form_data_body()
        # 文件
        file = ppt_create.file
        if isinstance(file, str):
            with open(file, "rb") as f:
                final_file = {"file": f}
                return self.send(AIPPTEnum.CREATE, body, final_file)
        else:
            final_file = {"file": file}
            return self.send(AIPPTEnum.CREATE, body, final_file)

    def create_outline(self, ppt_create: PPTCreate):
        null_check(ppt_create)
        ppt_create.create_out_line_check()
        body = ppt_create.to_form_data_body()
        return self.send(AIPPTEnum.CREATE_OUTLINE, body, is_form=True)

    def create_outline_by_doc(self, ppt_create: PPTCreate):
        null_check(ppt_create)
        ppt_create.create_outline_by_doc_check()
        # 请求体
        body = ppt_create.to_form_data_body()
        # 文件
        file = ppt_create.file
        if isinstance(file, str):
            with open(file, "rb") as f:
                final_file = {"file": f}
                return self.send(AIPPTEnum.CREATE_OUTLINE_BY_DOC, body, final_file)
        else:
            final_file = {"file": file}
            return self.send(AIPPTEnum.CREATE_OUTLINE_BY_DOC, body, final_file)

    def create_ppt_by_outline(self, ppt_create: PPTCreate):
        null_check(ppt_create)
        ppt_create.create_ppt_by_outline_check()
        return self.send(AIPPTEnum.CREATE_PPT_BY_OUTLINE, ppt_create.to_dict())

    def progress(self, sid):
        return self.send(AIPPTEnum.PROGRESS, None, None, False, sid)
