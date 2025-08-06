import json
import queue
import ssl
import threading
from queue import Queue
import base64
from dataclasses import dataclass
import websocket
import time
from typing import (Any,
                    Dict,
                    Generator,
                    AsyncGenerator,
                    Optional
                    )
from typing_extensions import Protocol
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import OralChatClientError
from xfyunsdkcore.utils import JsonUtils

DEFAULT_API_URL = "wss://sparkos.xfyun.cn/v1/openapi/chat"
DEFAULT_TIMEOUT = 10
WAIT_MILLIS = 40  # 每次发送间隔，毫秒
CHUNK = 1280  # 每次读取音频帧数
STATUS_FIRST_FRAME = 0  # 第一帧
STATUS_CONTINUE_FRAME = 1  # 中间帧
STATUS_LAST_FRAME = 2  # 最后一帧
CONTINUOUS_VAD = "continuous_vad"  # 单工模式
CONTINUOUS = "continuous"  # 双工模式


@dataclass
class OralChatParam:
    """超拟人聊天开启参数"""
    uid: str = None
    scene: str = "sos_app"
    interact_mode: str = None
    stmid: int = -1
    new_session: str = None
    personal: str = None
    prompt: str = None
    vcn: str = "x5_lingxiaoyue_flow"
    speed: int = 50
    volume: int = 50
    pitch: int = 50
    res_id: str = None
    res_gender: str = None
    os_sys: str = None
    pers_param: str = None

    def self_check(self):
        """参数自检"""
        if not self.interact_mode:
            raise OralChatClientError("交互模式不能为空")
        if not self.uid:
            raise OralChatClientError("uid不能为空")


class OralChatCallback(Protocol):
    """超拟人交互回调接口（Protocol）"""

    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用

        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _OralChatClient:
    """底层 WebSocket 客户端实现"""

    def __init__(self,
                 api_key: str,
                 api_secret: str,
                 api_url: str = DEFAULT_API_URL,
                 text_encoding: str = "utf8"):
        self.api_url = api_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.text_encoding = text_encoding
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        self.ws = None
        self.stmid = -1
        self.param = None
        logger.info("OralChatClient initialized")

    def run(self, param: OralChatParam) -> None:
        """运行 WebSocket 客户端

        Args:
            param: 请求参数
        """
        try:
            self.client.enableTrace(False)
            self.ws = self.client.WebSocketApp(
                Signature.create_signed_url(self.api_url, self.api_key, self.api_secret),
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            self.param = param
            self.ws.connected = False
            self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {str(e)}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: OralChatParam) -> threading.Thread:
        """异步运行 WebSocket 客户端，返回线程对象"""
        thread = threading.Thread(target=self.run, args=(param,))
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """WebSocket 连接建立回调"""
        ws.connected = True
        logger.info("WebSocket connection opened")

    def on_message(self, ws: websocket.WebSocketApp, message: bytes) -> None:
        """WebSocket 消息接收回调"""
        self.queue.put({"data": message.decode(self.text_encoding)})

    def on_error(self, ws: websocket.WebSocketApp, error: Any) -> None:
        """WebSocket 错误回调"""
        ws.connected = False
        logger.error(f"WebSocket error: {str(error)}")
        self.queue.put({"error": str(error), "error_code": -1})
        ws.close()

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        """WebSocket 关闭回调"""
        ws.connected = False
        logger.info(f"WebSocket closed: code={close_status_code}, reason={close_msg}")
        self.queue.put({"done": True})

    def subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> Generator[Dict, None, None]:
        """同步订阅 WebSocket 消息

        Args:
            timeout: 超时时间（秒）
        Yields:
            Dict: 消息内容
        Raises:
            TimeoutError: 超时未收到消息
            RtasrError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"RtasrClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise OralChatClientError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()

    async def a_subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> AsyncGenerator[Dict, None]:
        """异步订阅 WebSocket 消息

        Args:
            timeout: 超时时间（秒）
        Yields:
            Dict: 消息内容
        Raises:
            TimeoutError: 超时未收到消息
            OralChatClientError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.warning(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"RtasrClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise OralChatClientError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class OralChatClient:
    """讯飞 超拟人交互
    支持同步/异步流式转写，支持自定义回调
    """

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            vgap: int = 80,
            encoding_in: str = "raw",
            encoding_out: str = "raw",
            sample_rate_in: int = 16000,
            sample_rate_out: int = 16000,
            channels_in: int = 1,
            channels_out: int = 1,
            bit_depth_in: int = 16,
            bit_depth_out: int = 16,
            text_encoding: str = "utf8",
            text_compress: str = "raw",
            text_format: str = "json",
            frame_size: int = 0,
            dwa: str = None,
            eos: str = None,
            domain: str = None,
            host_url: str = DEFAULT_API_URL,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[OralChatCallback] = None):
        """初始化 RtasrClient

        Args:
            app_id: 应用ID
            api_key: API密钥
            punc, pd, lang, trans_type, trans_strategy, target_lang, vad_mdn, role_type, eng_lang_type: 详见官方文档
            host_url: API地址
            request_timeout: 超时时间（秒）
            callback: 可选回调对象
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.vgap = vgap
        self.encoding_in = encoding_in
        self.encoding_out = encoding_out
        self.sample_rate_in = sample_rate_in
        self.sample_rate_out = sample_rate_out
        self.channels_in = channels_in
        self.channels_out = channels_out
        self.bit_depth_in = bit_depth_in
        self.bit_depth_out = bit_depth_out
        self.text_encoding = text_encoding
        self.text_compress = text_compress
        self.text_format = text_format
        self.dwa = dwa
        self.eos = eos
        self.domain = domain
        self.frame_size = frame_size
        self.request_timeout = request_timeout
        self.callback = callback
        logger.info("OralChatClient initialized with parameters")

    def start(self, param: OralChatParam) -> _OralChatClient:
        """开启超拟人交互服务

        Args:
            param: 启动参数
        Return:
            _OralChatClient
        Raises:
            RtasrError: 转写失败
        """
        try:
            client = _OralChatClient(self.api_key, self.api_secret, self.host_url)
            client.arun(param)
            # 等待连接建立（可加超时控制）
            for _ in range(self.request_timeout):
                if client.ws.connected:
                    logger.info("OralClient Started...")
                    return client
                time.sleep(1)
            raise OralChatClientError("Connect TimeOut")
        except Exception as e:
            logger.error(f"Failed to start oral client: {str(e)}")
            raise OralChatClientError(f"Failed to start oral client: {str(e)}")

    def send_msg(self, bytes_data: bytes, status: int, client: _OralChatClient) -> None:
        """开启超拟人交互服务

        Args:
            bytes_data: 音频数据
            status: 启动参数
            client: _OralChatClient
        Return:
            _OralChatClient
        Raises:
            RtasrError: 转写失败
        """
        try:
            param = self._build_param(client.param, bytes_data, status, False)
            client.ws.send(param)
        except Exception as e:
            logger.error(f"Failed to start oral client: {str(e)}")
            raise OralChatClientError(f"Failed to start oral client: {str(e)}")

    def stream(self, client: _OralChatClient) -> Generator[Any, None, None]:
        """流式返回结果

        Args:
            client: _OralChatClient
        Yields:
            识别结果数据
        Raises:
            OralChatClientError: 获取流式结果失败
        """
        try:
            for content in client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to get stream result: {str(e)}")
            raise OralChatClientError(f"Failed to get stream result: {str(e)}")

    async def astream(self, client: _OralChatClient) -> AsyncGenerator[Any, None]:
        """异步流式返回结果

        Args:
            client: _OralChatClient
        Yields:
            识别结果数据
        Raises:
            OralChatClientError: 获取流式结果失败
        """
        try:
            async for content in client.a_subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to get stream result: {str(e)}")
            raise OralChatClientError(f"Failed to get stream result: {str(e)}")

    def stop(self, client: _OralChatClient) -> None:
        """超拟人交互服务停止

        Args:
            client: _OralChatClient
        """
        try:
            msg = self._build_param(status=2, param=client.param, is_end=True)
            client.ws.send(msg)
            time.sleep(0.04)
        except Exception as e:
            logger.warning(f"Failed to stop oral client: {str(e)}")
        finally:
            client.ws.close()
            client.queue.put({"done": True})

    def _build_param(self, param: OralChatParam,
                     bytes_data: Optional[bytes] = None,
                     status: int = 1,
                     is_end: bool = False) -> str:
        """构建参数"""
        # 是否新一轮会话
        new_chat = STATUS_FIRST_FRAME == status
        # 是否首帧
        first_frame = new_chat and (param.stmid == -1)
        # 流模式
        mode = param.interact_mode

        # 构建请求参数
        request = {
            "header": self._build_header(param, is_end, first_frame, mode, new_chat),
            "payload": self._build_payload(bytes_data, status, mode)
        }

        # 如果是首帧或新会话且为单工模式，添加参数
        if first_frame or (new_chat and CONTINUOUS_VAD == mode):
            request["parameter"] = self._build_parameter(param)

        request = JsonUtils.remove_none_values(request)
        body = json.dumps(request, ensure_ascii=False)
        logger.debug(f"超拟人交互请求入参：{body}")
        return body

    def _build_header(self, param: OralChatParam, is_end: bool, first_frame: bool, mode: str, new_chat: bool) -> dict:
        """构建Header"""
        header = {
            "app_id": self.app_id,
            "scene": param.scene,
            "uid": param.uid,
            "stmid": str(STATUS_FIRST_FRAME)
        }

        # 设置状态
        if is_end:
            header["status"] = STATUS_LAST_FRAME
        elif first_frame:
            header["status"] = STATUS_FIRST_FRAME
        else:
            header["status"] = STATUS_CONTINUE_FRAME

        is_continuous_vad = CONTINUOUS_VAD == mode
        if (new_chat and is_continuous_vad) or first_frame:
            # 第一帧或 CONTINUOUS_VAD 新会话，设置额外参数
            param.stmid += 1
            header["interact_mode"] = param.interact_mode
            header["os_sys"] = param.os_sys
            header["pers_param"] = param.pers_param
            header["stmid"] = str(param.stmid)
        elif is_continuous_vad:
            # CONTINUOUS_VAD 且不是新会话
            header["stmid"] = str(param.stmid)

        return header

    def _build_parameter(self, param: OralChatParam) -> dict:
        """构建Parameter"""
        return {
            "nlp": {
                "nlp": {
                    "encoding": self.text_encoding,
                    "compress": self.text_compress,
                    "format": self.text_format
                },
                "new_session": param.new_session,
                "personal": param.personal,
                "prompt": param.prompt
            },
            "tts": {
                "vcn": param.vcn,
                "res_id": param.res_id,
                "res_gender": param.res_gender,
                "speed": param.speed,
                "volume": param.volume,
                "pitch": param.pitch,
                "tts": {
                    "encoding": self.encoding_out,
                    "sample_rate": self.sample_rate_out,
                    "channels": self.channels_out,
                    "bit_depth": self.bit_depth_out,
                    "frame_size": self.frame_size
                }
            }
        }

    def _build_payload(self, bytes_data: Optional[bytes], status: int, mode: str) -> dict:
        """构建Payload"""
        # 根据流模式确定payload状态
        payload_status = status if CONTINUOUS_VAD == mode else status

        return {
            "audio": {
                "status": payload_status,
                "audio": base64.b64encode(bytes_data).decode('utf-8') if bytes_data else "",
                "encoding": self.encoding_in,
                "sample_rate": self.sample_rate_in,
                "channels": self.channels_in,
                "bit_depth": self.bit_depth_in,
                "frame_size": self.frame_size
            }
        }
