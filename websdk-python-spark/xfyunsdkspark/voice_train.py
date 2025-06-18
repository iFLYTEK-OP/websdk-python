import json
import time
from typing import (
    Optional,
    Dict,
    Any,
    Union,
    IO,
    Mapping
)
from dataclasses import dataclass
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import VoiceCloneSignature
from enum import Enum
from xfyunsdkcore.log.logger import logger


class VoiceTrainEnum(Enum):
    TOKEN = ("一句话复刻获取token", "http://avatar-hci.xfyousheng.com/aiauth/v1/token")
    TRAIN_TEXT = ("获取训练文本", "http://opentrain.xfyousheng.com/voice_train/task/traintext")
    TASK_ADD = ("创建音色训练任务", "http://opentrain.xfyousheng.com/voice_train/task/add")
    AUDIO_ADD = ("向训练任务添加音频（url链接）", "http://opentrain.xfyousheng.com/voice_train/audio/v1/add")
    TASK_SUBMIT = ("音色训练任务提交训练(异步)", "http://opentrain.xfyousheng.com/voice_train/task/submit")
    AUDIO_SUBMIT = (
        "向训练任务添加音频（本地文件）并提交训练任务",
        "http://opentrain.xfyousheng.com/voice_train/task/submitWithAudio")
    TASK_RESULT = ("根据任务id查询音色训练任务的状态", "http://opentrain.xfyousheng.com/voice_train/task/result")

    def __init__(self, desc: str, url: str):
        self.desc = desc
        self.url = url


@dataclass
class AudioAddRequest:
    taskId: str
    textId: int
    textSegId: int
    denoiseSwitch: Optional[int] = None
    mosRatio: Optional[float] = None
    files: Optional[Union[str, IO]] = None
    audioUrl: Optional[str] = None

    def validate_url(self):
        if not self.audioUrl:
            raise ValueError("Audio URL is required for URL-based requests")

    def validate_file(self):
        if not self.files:
            raise ValueError("File path is required for file-based requests")


@dataclass
class CreateTaskRequest:
    taskName: str
    sex: int
    ageGroup: int
    language: str
    resourceName: str
    resourceType: int = 12
    denoiseSwitch: Optional[int] = None
    mosRatio: Optional[float] = None
    thirdUser: Optional[str] = None
    callbackUrl: Optional[str] = None


class VoiceTrainClient(HttpClient):
    """Client for voice training"""

    def __init__(self, app_id: str, api_key: str):
        super().__init__("http://opentrain.xfyousheng.com/voice_train/", app_id, api_key)
        self.token = None
        self.token_expiry_time = 0
        self.token_auto_refresh_time = 1800  # 30 minutes in seconds
        self.refresh_token()

    def refresh_token(self) -> Optional[str]:
        """
        Get authentication token

        Returns:
            The authentication token
        """
        try:
            timestamp = str(int(time.time() * 1000))
            body = self._build_token_param(timestamp)
            response = self._post(VoiceTrainEnum.TOKEN, False, body, timestamp)
            self._cache_token(response)
            return response
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    def train_text(self, text_id: int, async_mode: bool = False) -> str:
        self._token_check(text_id)
        body = {"textId": text_id}
        return self._post(VoiceTrainEnum.TRAIN_TEXT, async_mode, body)

    def create_task(self, request: CreateTaskRequest, async_mode: bool = False) -> str:
        self._token_check(request)
        return self._post(VoiceTrainEnum.TASK_ADD, async_mode, request.__dict__)

    def audio_add(self, request: AudioAddRequest, async_mode: bool = False) -> str:
        self._token_check(request)
        request.validate_url()
        return self._post(VoiceTrainEnum.AUDIO_ADD, async_mode, request.__dict__)

    def submit(self, task_id: str, async_mode: bool = False) -> str:
        self._token_check(task_id)
        body = {"taskId": task_id}
        return self._post(VoiceTrainEnum.TASK_SUBMIT, async_mode, body)

    def submit_with_audio(self, request: AudioAddRequest, async_mode: bool = False) -> str:
        self._token_check(request)
        request.validate_file()

        data = {
            'taskId': request.taskId,
            'textId': str(request.textId),
            'textSegId': str(request.textSegId)
        }

        file = request.files
        if isinstance(file, str):
            with open(file, "rb") as f:
                final_file = {"file": f}
                return self._post(VoiceTrainEnum.AUDIO_SUBMIT, async_mode, data=data, files=final_file)
        else:
            final_file = {"file": file}
            return self._post(VoiceTrainEnum.AUDIO_SUBMIT, async_mode, data=data, files=final_file)

    def result(self, task_id: str, async_mode: bool = False) -> str:
        self._token_check(task_id)
        body = {"taskId": task_id}
        return self._post(VoiceTrainEnum.TASK_RESULT, async_mode, body)

    def _post(self, train_enum: VoiceTrainEnum, async_mode: bool = False, body: Optional[Any] = None,
              timestamp: Optional[str] = None, files: Optional[Any] = None,
              data: Optional[Mapping[str, Any]] = None) -> str:
        headers = self._get_headers(train_enum, body, timestamp)
        if async_mode:
            response = self.async_post(url=train_enum.url, json=body, data=data, files=files, headers=headers)
        else:
            response = self.post(url=train_enum.url, json=body, data=data, files=files, headers=headers)
        return response.text

    def _get_headers(self, train_enum: VoiceTrainEnum, body: Optional[Any],
                     timestamp: Optional[str]) -> Dict[str, str]:
        if train_enum == VoiceTrainEnum.TOKEN:
            return VoiceCloneSignature.token_sign(api_key=self.api_key, timestamp=timestamp, body=json.dumps(body))
        else:
            return VoiceCloneSignature.common_sign(app_id=self.app_id, api_key=self.api_key, body=json.dumps(body),
                                                   token=self.token)

    def _token_check(self, param: Optional[Any] = None):
        if not param:
            raise ValueError("参数不能为空")
        if not self.token or int(time.time() * 1000) > self.token_expiry_time:
            self.refresh_token()

    def _cache_token(self, response: str):
        if response:
            token_data = json.loads(response)
            self.token = token_data.get("accesstoken")
            expires_in = int(token_data.get("expiresin", '0'))

            if expires_in > self.token_auto_refresh_time:
                expires_in -= self.token_auto_refresh_time

            self.token_expiry_time = int(time.time() + expires_in) * 1000

    def _build_token_param(self, timestamp: str) -> dict:
        return {
            "model": "remote",
            "base": {
                "appid": self.app_id,
                "timestamp": timestamp,
                "version": "v1"
            }
        }
