import json
from typing import Optional
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.errors import QbhError


class QbhClient(HttpClient):
    """Client for 歌曲识别 Qbh"""

    def __init__(self, app_id: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 timeout=30,
                 enable_retry=False,
                 max_retries=3,
                 retry_interval=1):
        super().__init__("https://webqbh.xfyun.cn/v1/service/v1/qbh", app_id,
                         secret_key,
                         None,
                         timeout,
                         enable_retry,
                         max_retries,
                         retry_interval)

    def send(self,
             file_path: str = None,
             audio_url: str = None,
             engine_type: str = "afs",
             aue: str = "raw",
             sample_rate: str = "16000"):
        if audio_url is None and file_path is None:
            raise QbhError("audio_url和file_path不能同时为空")
        if aue == "aac":
            sample_rate = "8000"
        param = {"engine_type": engine_type, "aue": aue, "sample_rate": sample_rate}
        if audio_url:
            param.update({"audio_url": audio_url})
        header = Signature.get_signature_header(self.app_id, self.api_key, json.dumps(param))
        if audio_url:
            logger.debug(f"Sending request with audio_url: {audio_url}")
            response = self.post(self.host_url, headers=header)
        else:
            logger.debug(f"Sending request with file: {file_path}")
            with open(file_path, "rb") as f:
                response = self.post(self.host_url, headers=header, data=f)

        return response.text
