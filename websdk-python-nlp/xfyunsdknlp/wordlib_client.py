import json
import time
from typing import List
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from enum import Enum
from xfyunsdkcore.log.logger import logger


class WordLibEnum(Enum):
    CREATE_BLACK = ("新增黑名单词库", "https://audit.iflyaisol.com/audit_res/v1/wordLib/createBlack")
    CREATE_WHITE = ("新增白名单词库", "https://audit.iflyaisol.com/audit_res/v1/wordLib/createWhite")
    ADD_WORD = ("根据lib_id添加黑名单词条", "https://audit.iflyaisol.com/audit_res/v1/wordLib/addWord")
    INFO = ("根据lib_id查询词条明细", "https://audit.iflyaisol.com/audit_res/v1/wordLib/info")
    DEL_WORD = ("根据lib_id删除词条", "https://audit.iflyaisol.com/audit_res/v1/wordLib/delWord")
    LIST = ("根据appid查询账户下所有词库", "https://audit.iflyaisol.com/audit_res/v1/wordLib/list")
    DEL_LIB = ("根据lib_id删除词库", "https://audit.iflyaisol.com/audit_res/v1/wordLib/delete")

    def get_url(self):
        return self.value[1]

    def get_desc(self):
        return self.value[0]


class WordLibClient(HttpClient):
    """Client for WordLib"""

    def __init__(self, app_id: str, api_key: str, api_secret: str):
        super().__init__("https://audit.iflyaisol.com", app_id, api_key, api_secret)

    def create_lib(self, name: str, category: str = None, suggestion: str = "block", is_white: bool = False) -> str:
        """
        创建黑/白词库

        Args:
            name: 词库名称(不去重)
            category:   指定检测的敏感分类：
                        pornDetection 色情
                        violentTerrorism 暴恐
                        political 涉政
                        lowQualityIrrigation 低质量灌水
                        contraband 违禁
                        advertisement 广告
                        uncivilizedLanguage 不文明用语
            suggestion: block：违规
            is_white: 是否白名单
        """
        if not is_white and not category:
            raise ValueError("请指定词库策略")
        body = {
            "name": name,
            "category": category,
            "suggestion": suggestion
        }
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        url = WordLibEnum.CREATE_WHITE.get_url() if is_white else WordLibEnum.CREATE_BLACK.get_url()
        response = self.post(url, json=body, params=params)
        return response.text

    def add_word(self, lib_id: str, word_list: List[str]) -> str:
        """
        根据lib_id添加黑名单词条

        Args:
            lib_id: 词库Id
            word_list: 需要添加的词条
        """
        body = {
            "lib_id": lib_id,
            "word_list": word_list
        }
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(WordLibEnum.ADD_WORD.get_url(), json=body, params=params)
        return response.text

    def del_word(self, lib_id: str, word_list: List[str]) -> str:
        """
        根据lib_id删除词条

        Args:
            lib_id: 词库Id
            word_list: 需要删除的词条
        """
        body = {
            "lib_id": lib_id,
            "word_list": word_list
        }
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(WordLibEnum.DEL_WORD.get_url(), json=body, params=params)
        return response.text

    def detail(self, lib_id: str, return_word: bool = True) -> str:
        """
        根据lib_id查询词条明细

        Args:
            lib_id: 词库Id
            return_word: 决定是否返回词条明细，建议必传true
        """
        body = {
            "lib_id": lib_id,
            "return_word": return_word
        }
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(WordLibEnum.INFO.get_url(), json=body, params=params)
        return response.text

    def list_lib(self) -> str:
        """
        根据appid查询账户下所有词库

        Args:
        """
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(WordLibEnum.LIST.get_url(), json={}, params=params)
        return response.text

    def delete_lib(self, lib_id: str) -> str:
        """
        根据lib_id删除词库

        Args:
            lib_id: 词库ID
        """
        body = {"lib_id": lib_id}
        params = Signature.get_auth(self.app_id, self.api_key, self.api_secret)
        response = self.post(WordLibEnum.DEL_LIB.get_url(), json=body, params=params)
        return response.text
