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
from xfyunsdkcore.errors import SimInterpError

# WebSocket API URLs
HOST_URL = "wss://ws-api.xf-yun.com/v1/private/simult_interpretation"
DEFAULT_TIMEOUT = 30
WAIT_MILLIS = 40  # 发送帧间隔（毫秒）
STATUS_FIRST_FRAME = 0  # 第一帧
STATUS_CONTINUE_FRAME = 1  # 中间帧
STATUS_LAST_FRAME = 2  # 最后一帧


class SimInterpCallback(Protocol):
    """实时语音转写回调接口协议"""

    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用

        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _SimInterpClient:
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
        logger.info("SimInterpClient initialized")

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
                seq = 1
                while True:
                    buf = stream.read(frame_size)
                    if not buf:
                        status = STATUS_LAST_FRAME
                    param["header"]["status"] = status
                    param["payload"]["data"]["seq"] = seq
                    param["payload"]["data"]["status"] = status
                    param["payload"]["data"]["audio"] = str(base64.b64encode(buf), 'utf-8')
                    if status == STATUS_FIRST_FRAME:
                        ws.send(json.dumps(param))
                        status = STATUS_CONTINUE_FRAME
                        del param["parameter"]
                    elif status == STATUS_CONTINUE_FRAME:
                        ws.send(json.dumps(param))
                    elif status == STATUS_LAST_FRAME:
                        ws.send(json.dumps(param))
                        time.sleep(1)
                        break
                    time.sleep(WAIT_MILLIS / 1000.0)
                    seq += 1
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
            code = data["header"].get("code", -1)
            if code != 0:
                error_msg = data["header"].get('message', 'Unknown error')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return
            if "payload" in data:
                self.queue.put({"data": data["payload"]})
                if data["payload"].get("result", {}).get("status") == 2:
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
            SimInterpError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"SimInterpClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise SimInterpError(content["error"], content.get("error_code", -1))
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
            SimInterpError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"SimInterpClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise SimInterpError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class SimInterpClient:
    """讯飞 开放平台同声传译接口封装，支持流式同步/异步调用"""

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            vcn: str = "x2_xiaoguo",
            language: str = "zh_cn",
            language_type: int = 1,
            domain: str = "ist_ed_open",
            accent: str = "mandarin",
            vto: int = 15000,
            eos: int = 600000,
            nunum: int = 1,
            from_lang: str = "cn",
            to_lang: str = "en",
            encoding: str = "raw",
            sample_rate: int = 16000,
            channels: int = 1,
            bit_depth: int = 16,
            frame_size: int = 1280,
            host_url: str = None,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[SimInterpCallback] = None):
        """初始化 SimInterpClient

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            vcn: 发音人
            language: 转写语种，可选值：zh_cn
            from_lang: 源语种
            to_lang: 目标语种
            language_type: 语言过滤筛选
                            1：中英文模式，中文英文均可识别（默认）
                            2：中文模式，可识别出简单英文
                            3：英文模式，只识别出英文
                            4：纯中文模式，只识别出中文
                            注意：中文引擎支持该参数，其他语言不支持。
            domain: 应用领域
            accent: 方言
            eos: 用于设置端点检测的静默时间，单位是毫秒。即静默多长时间后引擎认为音频结束，取值范围0~99999999
            vto: vad强切控制，单位毫秒，默认15000
            encoding: 音频编码，注意更改生成文件的后缀（如.pcm或.mp3），可选值：
                        raw：合成pcm音频
                        lame：合成mp3音频
            nunum: （仅中文支持）数字规整：将语音识别结果中的原始文字串转为相应的阿拉伯数字或者符号
                    1：开启（默认值） 0：关闭
            frame_size: 每帧音频大小
            host_url: 自定义API地址
            request_timeout: 请求超时时间
            callback: 可选回调
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.language = language
        self.language_type = language_type
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.vcn = vcn
        self.domain = domain
        self.accent = accent
        self.encoding = encoding
        self.eos = eos
        self.nunum = nunum
        self.vto = vto
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _SimInterpClient(app_id, api_key, api_secret, host_url)
        logger.info("_SimInterpClient initialized with parameters")

    def _build_param(self) -> Dict[str, Any]:
        """构建请求参数"""
        param: Dict[str, Any] = {
            "header": {
                "app_id": self.app_id,
                "status": 0
            },
            "parameter": {
                "ist": {
                    "domain": self.domain,
                    "language": self.language,
                    "language_type": self.language_type,
                    "accent": self.accent,
                    "eos": self.eos,
                    "vto": self.vto,
                    "nunum": self.nunum
                },
                "streamtrans": {
                    "from": self.from_lang,
                    "to": self.to_lang
                },
                "tts": {
                    "vcn": self.vcn,
                    "tts_results": {
                        "encoding": self.encoding,
                        "sample_rate": self.sample_rate,
                        "channels": self.channels,
                        "bit_depth": self.bit_depth
                    }
                }
            },
            "payload": {
                "data": {
                    "audio": "",
                    "encoding": "raw",
                    "sample_rate": 16000,
                    "seq": 0,
                    "status": 0
                }
            }
        }
        logger.debug(f"SimInterp Request Parameters: {param}")
        return param

    def stream(self, stream) -> Generator[Any, None, None]:
        """同步流式转写

        Args:
            stream: 音频流对象
        Yields:
            转写结果
        Raises:
            SparkIatError: 转写失败
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
            raise SimInterpError(f"Failed to stream audio: {str(e)}")

    async def astream(self, stream) -> AsyncGenerator[Any, None]:
        """异步流式转写

        Args:
            stream: 音频流对象
        Yields:
            转写结果
        Raises:
            SparkIatError: 转写失败
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
            raise SimInterpError(f"Failed to stream audio: {str(e)}")
