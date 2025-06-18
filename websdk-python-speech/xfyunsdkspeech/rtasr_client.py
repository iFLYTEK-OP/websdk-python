import json
import queue
import ssl
import threading
import time
from queue import Queue
import websocket
from typing import (Any,
                    Dict,
                    Generator,
                    AsyncGenerator,
                    Optional
                    )
from typing_extensions import Protocol
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import RtasrSignature
from xfyunsdkcore.errors import RtasrError

DEFAULT_API_URL = "wss://rtasr.xfyun.cn/v1/ws"
DEFAULT_TIMEOUT = 30
WAIT_MILLIS = 40  # 每次发送间隔，毫秒
CHUNK = 1280  # 每次读取音频帧数
SEND_END = "{\"end\": true}"  # 结束消息


class RtasrCallback(Protocol):
    """实时语音转写回调接口（Protocol）"""

    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用

        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _RtasrClient:
    """底层 WebSocket 客户端实现"""

    def __init__(self, app_id: str, api_key: str, api_url: Optional[str] = DEFAULT_API_URL):
        self.api_url = api_url
        self.app_id = app_id
        self.api_key = api_key
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("RtasrClient initialized")

    def run(self, param: str, stream) -> None:
        """运行 WebSocket 客户端"""
        try:
            self.client.enableTrace(False)
            ws = self.client.WebSocketApp(
                RtasrSignature.create_signed_url(self.api_url, self.app_id, self.api_key) + param,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            ws.param = stream
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {str(e)}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: str, stream) -> threading.Thread:
        """异步运行 WebSocket 客户端，返回线程对象"""
        thread = threading.Thread(target=self.run, args=(param, stream))
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """WebSocket 连接建立回调"""
        logger.info("WebSocket connection opened")

        def run(stream):
            try:
                while True:
                    data = stream.read(CHUNK)
                    if not data:
                        break
                    ws.send(data)
                    time.sleep(WAIT_MILLIS / 1000.0)
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                self.queue.put({"error": f"Failed to send initial message: {str(e)}", "error_code": -1})
            finally:
                if hasattr(stream, 'stop_stream'):
                    stream.stop_stream()
                if hasattr(stream, 'close'):
                    stream.close()
                ws.send(bytes(SEND_END.encode('utf-8')))
                ws.close()

        thread = threading.Thread(target=run, args=(ws.param,))
        thread.start()

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """WebSocket 消息接收回调"""
        try:
            data = json.loads(message)
            code = data.get("code", -1)
            if code != "0":
                error_msg = data.get('desc', 'Unknown error')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return
            self.queue.put({"data": data["data"]})
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            self.queue.put({"error": f"Failed to process message: {str(e)}", "error_code": -1})
            ws.close()

    def on_error(self, ws: websocket.WebSocketApp, error: Any) -> None:
        """WebSocket 错误回调"""
        logger.error(f"WebSocket error: {str(error)}")
        self.queue.put({"error": str(error), "error_code": -1})
        ws.close()

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        """WebSocket 关闭回调"""
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
                raise RtasrError(content["error"], content.get("error_code", -1))
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
            RtasrError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"RtasrClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise RtasrError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class RtasrClient:
    """讯飞 Rtasr 流式转写接口封装
    支持同步/异步流式转写，支持自定义回调
    """

    def __init__(
            self,
            app_id: str,
            api_key: str,
            punc: Optional[str] = None,
            pd: Optional[str] = None,
            lang: Optional[str] = None,
            trans_type: Optional[str] = None,
            trans_strategy: Optional[int] = None,
            target_lang: Optional[str] = None,
            vad_mdn: Optional[int] = None,
            role_type: Optional[int] = None,
            eng_lang_type: Optional[int] = None,
            host_url: str = DEFAULT_API_URL,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[RtasrCallback] = None):
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
        self.host_url = host_url
        self.punc = punc
        self.pd = pd
        self.lang = lang
        self.trans_type = trans_type
        self.trans_strategy = trans_strategy
        self.target_lang = target_lang
        self.vad_mdn = vad_mdn
        self.role_type = role_type
        self.eng_lang_type = eng_lang_type
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _RtasrClient(app_id, api_key, host_url)
        logger.info("RtasrClient initialized with parameters")

    def _link_param(self) -> str:
        """构建URL参数字符串"""
        try:
            params = []
            if self.punc:
                params.append(f"&punc={self.punc}")
            if self.pd:
                params.append(f"&pd={self.pd}")
            if self.lang:
                params.append(f"&lang={self.lang}")
            if self.trans_type:
                params.append(f"&transType={self.trans_type}")
            if self.trans_strategy is not None:
                params.append(f"&transStrategy={self.trans_strategy}")
            if self.target_lang:
                params.append(f"&targetLang={self.target_lang}")
            if self.vad_mdn is not None:
                params.append(f"&vadMdn={self.vad_mdn}")
            if self.role_type is not None:
                params.append(f"&roleType={self.role_type}")
            if self.eng_lang_type is not None:
                params.append(f"&engLangType={self.eng_lang_type}")
            params_string = ''.join(params)
            logger.debug(f"Rtasr Request link Parameters: {params_string}")
            return params_string
        except Exception as e:
            logger.error(f"Failed to build parameters: {str(e)}")
            raise RtasrError(f"Failed to build parameters: {str(e)}")

    def stream(self, stream) -> Generator[Any, None, None]:
        """同步流式转写

        Args:
            stream: 音频流对象，需实现 read 方法
        Yields:
            识别结果数据
        Raises:
            RtasrError: 转写失败
        """
        try:
            logger.info("Start transform...")
            self.client.arun(self._link_param(), stream)
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {str(e)}")
            raise RtasrError(f"Failed to stream audio: {str(e)}")

    async def astream(self, stream) -> AsyncGenerator[Any, None]:
        """异步流式转写

        Args:
            stream: 音频流对象，需实现 read 方法
        Yields:
            识别结果数据
        Raises:
            RtasrError: 转写失败
        """
        try:
            logger.info("Async Start transform...")
            self.client.arun(self._link_param(), stream)
            async for content in self.client.a_subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {str(e)}")
            raise RtasrError(f"Failed to stream audio: {str(e)}")
