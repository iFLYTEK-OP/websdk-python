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
from xfyunsdkcore.errors import IatError

# WebSocket API URLs
CH_EN_LANGUAGE = "wss://iat-api.xfyun.cn/v2/iat"
SMALL_LANGUAGE = "wss://iat-niche-api.xfyun.cn/v2/iat"
DEFAULT_TIMEOUT = 30
WAIT_MILLIS = 40  # 发送帧间隔（毫秒）
STATUS_FIRST_FRAME = 0  # 第一帧
STATUS_CONTINUE_FRAME = 1  # 中间帧
STATUS_LAST_FRAME = 2  # 最后一帧


class IatCallback(Protocol):
    """实时语音转写回调接口协议"""
    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用

        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _IatClient:
    """底层 WebSocket 客户端实现"""

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 small_language: bool = False,
                 api_url: Optional[str] = None):
        """初始化底层 WebSocket 客户端

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            small_language: 是否使用小语种服务
            api_url: 可选自定义API地址
        """
        self.api_url = api_url if api_url else (
            SMALL_LANGUAGE if small_language else CH_EN_LANGUAGE)
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("IatClient initialized")

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
                    if status == STATUS_FIRST_FRAME:
                        data["status"] = STATUS_FIRST_FRAME
                        data["audio"] = str(base64.b64encode(buf), 'utf-8')
                        d = {"common": param["common"],
                             "business": param["business"],
                             "data": data}
                        ws.send(json.dumps(d))
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        data["status"] = STATUS_CONTINUE_FRAME
                        data["audio"] = str(base64.b64encode(buf), 'utf-8')
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
            IatError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"IatClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise IatError(content["error"], content.get("error_code", -1))
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
            IatError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"IatClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise IatError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class IatClient:
    """讯飞 Iat 语音转写接口封装，支持流式同步/异步调用"""

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            language: str = "zh_cn",
            domain: str = "iat",
            accent: str = "mandarin",
            format: str = "audio/L16;rate=16000",
            encoding: str = "raw",
            vad_eos: int = 2000,
            dwa: str = None,
            pd: str = None,
            ptt: int = 1,
            rlang: str = "zh-cn",
            vinfo: int = 0,
            nunum: int = 1,
            pcm: int = 1,
            speex_size: int = 2,
            nbest: int = None,
            wbest: int = None,
            frame_size: int = 1280,
            host_url: str = None,
            small_lang: bool = False,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[IatCallback] = None):
        """初始化 IatClient

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            language: 语种
            domain: 应用领域
            accent: 方言
            format: 音频格式
            encoding: 编码方式
            vad_eos: 端点检测
            dwa: 动态标点
            pd: 领域个性化参数
            ptt: 是否返回标点
            rlang: 多语种标识
            vinfo: 是否返回音频信息
            nunum: 是否开启多候选
            pcm: 是否返回pcm
            speex_size: speex压缩等级
            nbest: 候选数
            wbest: 词级别候选数
            frame_size: 每帧音频大小
            host_url: 自定义API地址
            small_lang: 是否小语种
            request_timeout: 请求超时时间
            callback: 可选回调
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.language = language
        self.domain = domain
        self.accent = accent
        self.format = format
        self.encoding = encoding
        self.vad_eos = vad_eos
        self.dwa = dwa
        self.pd = pd
        self.ptt = ptt
        self.rlang = rlang
        self.vinfo = vinfo
        self.pcm = pcm
        self.nunum = nunum
        self.speex_size = speex_size
        self.nbest = nbest
        self.wbest = wbest
        self.frame_size = frame_size
        self.small_lang = small_lang
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _IatClient(app_id, api_key, api_secret, small_lang, host_url)
        logger.info("IatClient initialized with parameters")

    def _build_param(self) -> Dict[str, Any]:
        """构建请求参数"""
        param: Dict[str, Any] = {
            "common": {
                "app_id": self.app_id
            },
            "business": {
                "language": self.language,
                "domain": self.domain,
                "accent": self.accent,
                "vad_eos": self.vad_eos,
                "dwa": self.dwa,
                "pd": self.pd,
                "ptt": self.ptt,
                "pcm": self.pcm,
                "rlang": self.rlang,
                "vinfo": self.vinfo,
                "nunum": self.nunum,
                "speex_size": self.speex_size,
                "nbest": self.nbest,
                "wbest": self.wbest
            },
            "data": {
                "status": 0,
                "format": self.format,
                "encoding": self.encoding,
                "audio": "",
            }
        }
        logger.debug(f"Iat Clone Request Parameters: {param}")
        return param

    def stream(self, stream) -> Generator[Any, None, None]:
        """同步流式转写

        Args:
            stream: 音频流对象
        Yields:
            转写结果
        Raises:
            IatError: 转写失败
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
            raise IatError(f"Failed to stream audio: {str(e)}")

    async def astream(self, stream) -> AsyncGenerator[Any, None]:
        """异步流式转写

        Args:
            stream: 音频流对象
        Yields:
            转写结果
        Raises:
            IatError: 转写失败
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
            raise IatError(f"Failed to stream audio: {str(e)}")
