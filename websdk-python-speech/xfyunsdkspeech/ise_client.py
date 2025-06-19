import json
import ssl
import base64
import threading
import time
from queue import Queue, Empty
from typing import Any, Dict, Generator, AsyncGenerator, Optional
from typing_extensions import Protocol
import websocket
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import IseError

HOST_URL = "wss://ise-api.xfyun.cn/v2/open-ise"
DEFAULT_TIMEOUT = 30
WAIT_MILLIS = 40  # 每帧发送间隔（毫秒）
STATUS_FIRST_FRAME = 0  # 第一帧标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧标识


class IseCallback(Protocol):
    """实时语音转写回调接口协议"""
    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用
        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _IseClient:
    """底层 WebSocket 客户端实现"""
    def __init__(self, app_id: str, api_key: str, api_secret: str, api_url: Optional[str] = None):
        self.api_url = api_url or HOST_URL
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("IseClient initialized")

    def run(self, param: Dict[str, Any], stream, frame_size: int, text: str) -> None:
        """启动 WebSocket 客户端主循环"""
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
            ws._text = text
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {e}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: Dict[str, Any], stream, frame_size: int, text: str) -> threading.Thread:
        """异步启动 WebSocket 客户端"""
        thread = threading.Thread(target=self.run, args=(param, stream, frame_size, text))
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """WebSocket 连接建立时回调，负责音频流发送"""
        logger.info("WebSocket connection opened")

        def send_audio(param, stream, frame_size, text):
            status = STATUS_FIRST_FRAME
            try:
                while True:
                    buf = stream.read(frame_size)
                    if not buf:
                        status = STATUS_LAST_FRAME
                    if status == STATUS_FIRST_FRAME:
                        # 发送第一帧，带 business 参数
                        business = param["business"]
                        business["text"] = text
                        d1 = {"common": param["common"], "business": business, "data": param["data"]}
                        ws.send(json.dumps(d1))
                        time.sleep(WAIT_MILLIS / 1000.0)
                        status = STATUS_CONTINUE_FRAME
                        # 发送第一帧音频数据
                        d2 = {
                            "business": {"cmd": "auw", "aus": 1},
                            "data": {"status": 1, "data": base64.b64encode(buf).decode('utf-8')}
                        }
                        ws.send(json.dumps(d2))
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {
                            "business": {"cmd": "auw", "aus": 2},
                            "data": {"status": 1, "data": base64.b64encode(buf).decode('utf-8')}
                        }
                        ws.send(json.dumps(d))
                    elif status == STATUS_LAST_FRAME:
                        d = {
                            "business": {"cmd": "auw", "aus": 4},
                            "data": {"status": 2, "data": base64.b64encode(buf).decode('utf-8')}
                        }
                        ws.send(json.dumps(d))
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
                logger.error(f"Error during audio send: {e}")
                self.queue.put({"error": f"Failed to send audio: {e}", "error_code": -1})
            finally:
                # 关闭音频流和 WebSocket
                if hasattr(stream, 'stop_stream'):
                    stream.stop_stream()
                if hasattr(stream, 'close'):
                    stream.close()

        thread = threading.Thread(target=send_audio, args=(ws.param, ws.stream, ws.frame_size, ws._text))
        thread.start()

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """WebSocket 消息接收回调"""
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
            logger.error(f"Failed to process message: {e}")
            self.queue.put({"error": f"Failed to process message: {e}", "error_code": -1})
            ws.close()

    def on_error(self, ws: websocket.WebSocketApp, error: Any) -> None:
        """WebSocket 错误回调"""
        logger.error(f"WebSocket error: {error}")
        self.queue.put({"error": str(error), "error_code": -1})
        ws.close()

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        """WebSocket 关闭回调"""
        logger.info(f"WebSocket closed: code={close_status_code}, reason={close_msg}")
        self.queue.put({"done": True})

    def subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> Generator[Dict, None, None]:
        """同步订阅 WebSocket 消息，超时抛出异常"""
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"IseClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise IseError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()

    async def a_subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> AsyncGenerator[Dict, None]:
        """异步订阅 WebSocket 消息，超时抛出异常"""
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"IseClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise IseError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class IseClient:
    """讯飞 Ise 合成接口封装，支持流式处理"""
    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            sub: str = "ise",
            ent: str = "cn_vip",
            category: str = "read_sentence",
            frame_size: int = 1280,
            tte: str = "utf-8",
            ttp_skip: bool = True,
            extra_ability: Optional[str] = None,
            aue: str = "lame",
            auf: str = "audio/L16;rate=16000",
            rstcd: str = "utf8",
            group: Optional[str] = None,
            check_type: Optional[str] = None,
            grade: Optional[str] = None,
            rst: Optional[str] = None,
            ise_unite: Optional[str] = None,
            plev: Optional[str] = None,
            host_url: Optional[str] = None,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[IseCallback] = None):
        """
        初始化 IseClient
        Args:
            app_id (str): 应用ID
            api_key (str): API Key
            api_secret (str): API Secret
            sub (str): 服务类型指定，"ise"（开放评测）
            ent (str): 中文："cn_vip"，英文："en_vip"
            category (str): 题型，详见参数说明
            frame_size (int): 音频帧大小，默认1280
            tte (str): 待评测文本编码，"utf-8"/"gbk"
            ttp_skip (bool): 跳过ttp直接用ssb中的文本评测，默认true
            extra_ability (str): 拓展能力，详见参数说明
            aue (str): 音频格式，默认"lame"
            auf (str): 音频采样率，默认"audio/L16;rate=16000"
            rstcd (str): 返回结果格式，默认"utf8"
            group (str): 群体参数，详见参数说明
            check_type (str): 检错松严门限，详见参数说明
            grade (str): 学段参数，详见参数说明
            rst (str): 评测返回结果与分制控制，详见参数说明
            ise_unite (str): 返回结果控制，详见参数说明
            plev (str): 结果信息控制，详见参数说明
            host_url (str): 可选，自定义API URL
            request_timeout (int): 请求超时时间（秒）
            callback (IseCallback): 可选，音频片段回调
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.sub = sub
        self.ent = ent
        self.category = category
        self.frame_size = frame_size
        self.tte = tte
        self.ttp_skip = ttp_skip
        self.extra_ability = extra_ability
        self.aue = aue
        self.auf = auf
        self.rstcd = rstcd
        self.group = group
        self.check_type = check_type
        self.grade = grade
        self.rst = rst
        self.ise_unite = ise_unite
        self.plev = plev
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _IseClient(app_id, api_key, api_secret, host_url)
        logger.info("IseClient initialized with parameters")

    def _build_param(self) -> Dict[str, Any]:
        """
        构建请求参数。
        """
        param: Dict[str, Any] = {
            "common": {"app_id": self.app_id},
            "business": {
                "sub": self.sub,
                "ent": self.ent,
                "category": self.category,
                "aus": None,  # 由音频上传阶段动态赋值
                "cmd": "ssb",  # 参数上传阶段
                "text": None,  # 由调用时赋值
                "tte": self.tte,
                "ttp_skip": self.ttp_skip,
                "extra_ability": self.extra_ability,
                "aue": self.aue,
                "auf": self.auf,
                "rstcd": self.rstcd,
                "group": self.group,
                "check_type": self.check_type,
                "grade": self.grade,
                "rst": self.rst,
                "ise_unite": self.ise_unite,
                "plev": self.plev,
            },
            "data": {"data": None, "status": 0}
        }
        logger.debug(f"Ise Request Parameters: {param}")
        return param

    def stream(self, text: str, stream) -> Generator[Any, None, None]:
        """同步流式处理音频
        Args:
            text: 待合成文本
            stream: 音频流对象
        Yields:
            音频数据片段
        Raises:
            IseError: 流式处理失败
        """
        try:
            logger.info("Start transform...")
            self.client.arun(self._build_param(), stream, self.frame_size, text)
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {e}")
            raise IseError(f"Failed to stream audio: {e}")

    async def astream(self, text: str, stream) -> AsyncGenerator[Any, None]:
        """异步流式处理音频
        Args:
            text: 待合成文本
            stream: 音频流对象
        Yields:
            音频数据片段
        Raises:
            IseError: 流式处理失败
        """
        try:
            logger.info("Async Start transform...")
            self.client.arun(self._build_param(), stream, self.frame_size, text)
            async for content in self.client.a_subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {e}")
            raise IseError(f"Failed to stream audio: {e}")
