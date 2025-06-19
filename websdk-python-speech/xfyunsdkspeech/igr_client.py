import base64
import json
import queue
import ssl
import threading
import time
from queue import Queue
from typing import Any, Dict, Generator, AsyncGenerator, Optional
from typing_extensions import Protocol
import websocket
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import IgrError

# WebSocket API URLs
HOST_URL = "wss://ws-api.xfyun.cn/v2/igr"
DEFAULT_TIMEOUT = 30
WAIT_MILLIS = 40  # 发送帧间隔（毫秒）
STATUS_FIRST_FRAME = 0  # 第一帧
STATUS_CONTINUE_FRAME = 1  # 中间帧
STATUS_LAST_FRAME = 2  # 最后一帧


class IgrCallback(Protocol):
    """实时语音转写回调接口协议"""

    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用

        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _IgrClient:
    """底层 WebSocket 客户端实现"""

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 api_url: Optional[str] = None):
        """初始化底层 WebSocket 客户端

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            api_url: 可选自定义API地址
        """
        self.api_url = api_url if api_url else HOST_URL
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("IgrClient initialized")

    def run(self, param: Dict[str, Any], stream, frame_size: int) -> None:
        """运行 WebSocket 客户端

        Args:
            param: 请求参数
            stream: 音频流对象
            frame_size: 每帧音频大小
        """
        try:
            self.client.enableTrace(False)
            ws = self.client.WebSocketApp(
                Signature.create_signed_url(self.api_url, self.api_key, self.api_secret),
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            ws.param = param
            ws.stream = stream
            ws.frame_size = frame_size
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {str(e)}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: Dict[str, Any], stream, frame_size: int) -> threading.Thread:
        """在新线程中运行 WebSocket 客户端

        Args:
            param: 请求参数
            stream: 音频流对象
            frame_size: 每帧音频大小
        Returns:
            运行中的线程对象
        """
        thread = threading.Thread(target=self.run, args=(param, stream, frame_size))
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """WebSocket 连接建立时回调"""
        logger.info("WebSocket connection opened")

        def run(param, stream, frame_size):
            status = STATUS_FIRST_FRAME
            try:
                while True:
                    buf = stream.read(frame_size)
                    if not buf:
                        status = STATUS_LAST_FRAME
                    data = param["data"]
                    data["audio"] = str(base64.b64encode(buf), 'utf-8')
                    if status == STATUS_FIRST_FRAME:
                        data["status"] = STATUS_FIRST_FRAME
                        d = {"common": param["common"],
                             "business": param["business"],
                             "data": data}
                        ws.send(json.dumps(d))
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        data["status"] = STATUS_CONTINUE_FRAME
                        ws.send(json.dumps({"data": data}))
                    elif status == STATUS_LAST_FRAME:
                        data["status"] = STATUS_LAST_FRAME
                        ws.send(json.dumps({"data": data}))
                        time.sleep(1)
                        break
                    time.sleep(WAIT_MILLIS / 1000.0)
            except IOError as e:
                # 捕捉 PyAudio 中 stream 被关闭时的典型异常
                if "Input overflowed" in str(e) or "Stream closed" in str(e):
                    logger.warning(f"Stream read failed (possibly closed): {e}")
                else:
                    # 如果是其他IO错误，继续抛出
                    logger.error(f"Error during audio send: {e}")
                    self.queue.put({"error": f"Failed to send audio: {e}", "error_code": -1})
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                self.queue.put({"error": f"Failed to send initial message: {str(e)}", "error_code": -1})
            finally:
                if hasattr(stream, 'stop_stream'):
                    stream.stop_stream()
                if hasattr(stream, 'close'):
                    stream.close()

        thread = threading.Thread(target=run, args=(ws.param, ws.stream, ws.frame_size))
        thread.start()

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """处理 WebSocket 消息回调"""
        try:
            data = json.loads(message)
            code = data.get("code", -1)
            if code != 0:
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return
            self.queue.put({"data": data["data"]})
            if data.get("data", {}).get("status") == STATUS_LAST_FRAME:
                ws.close()
                self.queue.put({"done": True})
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
            消息内容字典
        Raises:
            TimeoutError: 超时未收到消息
            IgrError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"IgrClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise IgrError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()

    async def a_subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> AsyncGenerator[Dict, None]:
        """异步订阅 WebSocket 消息

        Args:
            timeout: 超时时间（秒）
        Yields:
            消息内容字典
        Raises:
            TimeoutError: 超时未收到消息
            IgrError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"IgrClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise IgrError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class IgrClient:
    """讯飞 Igr 语音转写接口封装，支持流式同步/异步调用"""

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            ent: str = "igr",
            aue: str = "raw",
            rate: int = 16000,
            frame_size: int = 1280,
            host_url: str = None,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[IgrCallback] = None):
        """初始化 IgrClient

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            ent: 引擎类型
            aue: 音频格式raw：原生音频数据pcm格式
                 speex：speex格式（rate需设置为8000）
                 speex-wb：宽频speex格式（rate需设置为16000）
                 amr：amr格式（rate需设置为8000）
                 amr-wb：宽频amr格式（rate需设置为16000）
            rate: 音频采样率 16000/8000
            frame_size: 每帧音频大小
            host_url: 自定义API地址
            request_timeout: 请求超时时间
            callback: 可选回调
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.ent = ent
        self.aue = aue
        self.rate = rate
        self.frame_size = frame_size
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _IgrClient(app_id, api_key, api_secret, host_url)
        logger.info("IgrClient initialized with parameters")

    def _build_param(self) -> Dict[str, Any]:
        """构建请求参数"""
        param: Dict[str, Any] = {
            "common": {
                "app_id": self.app_id
            },
            "business": {
                "ent": self.ent,
                "aue": self.aue,
                "rate": self.rate
            },
            "data": {
                "status": 0,
                "audio": "",
            }
        }
        logger.debug(f"Igr Request Parameters: {param}")
        return param

    def stream(self, stream) -> Generator[Any, None, None]:
        """同步流式转写

        Args:
            stream: 音频流对象
        Yields:
            转写结果
        Raises:
            IgrError: 转写失败
        """
        try:
            logger.info("Start transform...")
            self.client.arun(self._build_param(), stream, self.frame_size)
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {str(e)}")
            raise IgrError(f"Failed to stream audio: {str(e)}")

    async def astream(self, stream) -> AsyncGenerator[Any, None]:
        """异步流式转写

        Args:
            stream: 音频流对象
        Yields:
            转写结果
        Raises:
            IgrError: 转写失败
        """
        try:
            logger.info("Async Start transform...")
            self.client.arun(self._build_param(), stream, self.frame_size)
            async for content in self.client.a_subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {str(e)}")
            raise IgrError(f"Failed to stream audio: {str(e)}")
