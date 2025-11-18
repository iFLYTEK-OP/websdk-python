import json
from xfyunsdkcore.model.aiui_knowledge_model import (
    AiUiCreate,
    AiUiUpload,
    AiUiDelete,
    AiUiLink,
    AiUiSearch
)
from xfyunsdkcore.http_client import HttpClient
from enum import Enum
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import AiUiKnowledgeError
from xfyunsdkcore.utils import JsonUtils
from contextlib import ExitStack


class AiUiKnowledgeEnum(Enum):
    CREATE = ("用户知识库创建", "/repo/create", "POST")
    UPLOAD = ("知识库追加文件上传", "/doc/saveRepoDoc", "POST")
    DELETE = ("删除用户知识库或某个文件", "/repo/file/delete", "DELETE")
    LIST = ("查询应用已绑定知识库列表及全量知识库列表", "/app/getRepoConfig", "POST")
    LINK = ("用户应用关联绑定知识库", "/app/saveRepoConfig", "POST")

    def get_url(self):
        return self.value[1]

    def get_method(self):
        return self.value[2]

    def get_desc(self):
        return self.value[0]


def null_check(param):
    if param is None:
        raise AiUiKnowledgeError("参数不能为空")


class AiUiKnowledgeClient(HttpClient):
    """Client for 超拟人个性化知识库 """

    def __init__(self, app_id: str,
                 api_password: str,
                 timeout=30,
                 enable_retry=False,
                 max_retries=3,
                 retry_interval=1):
        super().__init__("https://sparkcons-rag.cn-huabei-1.xf-yun.com/aiuiKnowledge/rag/api", app_id,
                         None,
                         api_password,
                         timeout,
                         enable_retry,
                         max_retries,
                         retry_interval)

    def create(self, knowledge_create: AiUiCreate):
        # 参数校验
        null_check(knowledge_create)
        knowledge_create.create_check()
        # 请求头
        headers = {
            "Authorization": f"Bearer {self.api_secret}"
        }
        # 请求地址
        url = self.host_url + AiUiKnowledgeEnum.CREATE.get_url()
        logger.debug(f"{AiUiKnowledgeEnum.CREATE.get_desc()}请求URL：{url}，入参：{knowledge_create}")
        response = self.post(url, headers=headers, json=knowledge_create.to_dict())
        return response.text

    def upload(self, knowledge_upload: AiUiUpload):
        # 参数校验
        null_check(knowledge_upload)
        knowledge_upload.upload_check()
        # 请求头
        headers = {
            "Authorization": f"Bearer {self.api_secret}"
        }
        # 请求地址
        url = self.host_url + AiUiKnowledgeEnum.UPLOAD.get_url()
        # 请求参数
        body = knowledge_upload.to_dict()
        logger.debug(f"{AiUiKnowledgeEnum.UPLOAD.get_desc()}请求URL：{url}，入参：{knowledge_upload}")
        # 取出文件参数
        file_paths = body.pop("files")
        file_urls = body.pop("fileList")
        body = JsonUtils.remove_none_values(body)

        if file_paths:
            # 通过文件流的方式上传
            with ExitStack() as stack:
                files = []
                for path in file_paths:
                    if isinstance(path, str):
                        # 是文件路径：打开并推入
                        f = stack.enter_context(open(path, 'rb'))
                        # 自动猜测 MIME（可选）
                        files.append(('file', f))
                    elif isinstance(path, tuple):
                        # 假设用户传入的是 (filename, content_bytes) 或完整元组
                        # 但注意：requests 需要 file-like object，不是 bytes！
                        # 所以更安全的做法是只接受路径或已打开的文件对象
                        raise ValueError("建议只传入文件路径字符串，或自行构造 files 列表")
                    else:
                        # 如果 path 已经是 (filename, file_obj, mime) 形式？
                        # 需要明确约定，否则容易出错
                        files.append(path)
                response = self.post(url, headers=headers, data=body, files=files)
                return response.text
        else:
            # 通过文件地址的方式上传
            body.update({"fileListStr": json.dumps(file_urls)})
            files = {}
            for key, value in body.items():
                if isinstance(value, (dict, list, tuple)):
                    # 复杂类型 → JSON 字符串
                    files[key] = (None, json.dumps(value))
                else:
                    # 简单类型 → 转字符串
                    files[key] = (None, str(value))
            response = self.post(url, headers=headers, files=files)
            return response.text

    def delete(self, knowledge_delete: AiUiDelete):
        # 参数校验
        null_check(knowledge_delete)
        knowledge_delete.delete_check()
        # 请求头
        headers = {
            "Authorization": f"Bearer {self.api_secret}"
        }
        # 请求地址
        url = self.host_url + AiUiKnowledgeEnum.DELETE.get_url()
        logger.debug(f"{AiUiKnowledgeEnum.DELETE.get_desc()}请求URL：{url}，入参：{knowledge_delete}")
        response = self.request("DELETE", url, headers=headers, params=knowledge_delete.to_dict())
        return response.text

    def list(self, knowledge_search: AiUiSearch):
        # 参数校验
        null_check(knowledge_search)
        knowledge_search.search_check()
        # 请求头
        headers = {
            "Authorization": f"Bearer {self.api_secret}"
        }
        # 请求地址
        url = self.host_url + AiUiKnowledgeEnum.LIST.get_url()
        logger.debug(f"{AiUiKnowledgeEnum.LIST.get_desc()}请求URL：{url}，入参：{knowledge_search}")
        response = self.get(url, headers=headers, params=knowledge_search.to_dict())
        return response.text

    def link(self, knowledge_link: AiUiLink):
        # 参数校验
        null_check(knowledge_link)
        knowledge_link.link_check()
        # 请求头
        headers = {
            "Authorization": f"Bearer {self.api_secret}"
        }
        # 请求地址
        url = self.host_url + AiUiKnowledgeEnum.LINK.get_url()
        logger.debug(f"{AiUiKnowledgeEnum.LINK.get_desc()}请求URL：{url}，入参：{knowledge_link}")
        response = self.post(url, headers=headers, json=knowledge_link.to_dict())
        return response.text
