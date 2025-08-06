import base64
import json
import queue
import ssl
import threading
from queue import Queue
import websocket
from typing import Any, Dict, Generator, AsyncGenerator, Optional
from typing_extensions import Protocol
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import OralError

DEFAULT_API_URL = "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6"
DEFAULT_TIMEOUT = 30


class OralCallback(Protocol):
    """Oral synthesis callback interface."""

    def chunk(self, audio_chunk: str, **kwargs: Any) -> None:
        """Called when an audio chunk is received."""
        ...


class _OralClient:
    """WebSocket client for Oral."""

    def __init__(self, app_id: str, api_key: str, api_secret: str, api_url: Optional[str] = None):
        self.api_url = api_url or DEFAULT_API_URL
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("OralClient initialized")

    def run(self, param: dict) -> None:
        """Run the WebSocket client synchronously."""
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
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {e}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: dict) -> threading.Thread:
        """Run the WebSocket client in a separate thread."""
        thread = threading.Thread(target=self.run, args=(param,))
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        logger.info("WebSocket connection opened")
        try:
            ws.send(json.dumps(ws.param))
        except Exception as e:
            logger.error(f"Failed to send initial message: {e}")
            self.queue.put({"error": f"Failed to send initial message: {e}", "error_code": -1})
            ws.close()

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        try:
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                error_msg = data['header'].get('message', 'Unknown error')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return
            result = data.get("payload")
            if result:
                self.queue.put({"data": result})
                if result["audio"]["status"] == 2:
                    self.queue.put({"done": True})
                    ws.close()
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            self.queue.put({"error": f"Failed to process message: {e}", "error_code": -1})
            ws.close()

    def on_error(self, ws: websocket.WebSocketApp, error: Any) -> None:
        logger.error(f"WebSocket error: {error}")
        self.queue.put({"error": str(error), "error_code": -1})
        ws.close()

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        logger.info(f"WebSocket closed: code={close_status_code}, reason={close_msg}")
        self.queue.put({"done": True})

    def subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> Generator[Dict, None, None]:
        """Yield WebSocket messages until done or error."""
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"OralClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise OralError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()

    async def a_subscribe(self, timeout: int = DEFAULT_TIMEOUT) -> AsyncGenerator[Dict, None]:
        """Asynchronously yield WebSocket messages until done or error."""
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"OralClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise OralError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class OralClient:
    """Oral client for Xunfei Oral API, supports streaming and callback."""

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            vcn: str = "x4_lingxiaoxuan_oral",
            text_encoding: str = "utf8",
            text_compress: str = "raw",
            text_format: str = "plain",
            oral_level: str = "mid",
            spark_assist: int = 1,
            stop_split: int = 0,
            remain: int = 0,
            speed: int = 50,
            volume: int = 50,
            pitch: int = 50,
            bgs: int = 0,
            reg: int = 0,
            rdn: int = 0,
            rhy: int = 0,
            encoding: str = "lame",
            sample_rate: int = 24000,
            channels: int = 1,
            bit_depth: int = 16,
            frame_size: int = 0,
            status: int = 2,
            host_url: str = None,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[OralCallback] = None):
        """
        初始化 OralClient
        
        Args:
            app_id: Application ID
            api_key: API key
            api_secret: API secret
            vcn: 超拟人发音人
            host_url: API endpoint URL
            text_encoding: 文本编码
            text_compress: 文本压缩格式
            text_format: 返回结果格式
            oral_level: 口语化等级
            spark_assist: 是否通过大模型进行口语化
            stop_split: 关闭服务端拆句
            remain: 是否保留原书面语的样子
            speed: 语速[0,100]
            volume: 音量[0,100]
            pitch: 语调[0,100]
            bgs: 背景音   默认0
            reg: 英文发音方式: 0:自动判断处理，如果不确定将按照英文词语拼写处理（缺省）,
                             1:所有英文按字母发音
                             2:自动判断处理，如果不确定将按照字母朗读
            rdn: 合成音频数字发音方式: 0:自动判断（缺省）,
                                   1:完全数值,
                                   2:完全字符串,
                                   3:字符串优先
            rhy: 是否返回拼音标注: 0:不返回拼音
                                1:返回拼音（纯文本格式，utf8编码）
            encoding: 音频编码, raw,lame, speex, opus, opus-wb, opus-swb, speex-wb
            sample_rate: 音频采样率, 16000, 8000, 24000（缺省）
            sample_rate: 音频采样率, 16000, 8000, 24000（缺省）
            channels: 声道数   1（缺省）, 2
            bit_depth: 位深    16（缺省）, 8
            frame_size: 帧大小[0,1024]   默认0
            text_format: 返回结果格式json, plain（缺省）
            status: Status code
            request_timeout: Request timeout in seconds
            callback: Optional callback for audio chunks
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.vcn = vcn
        self.text_encoding = text_encoding
        self.text_compress = text_compress
        self.text_format = text_format
        self.oral_level = oral_level
        self.spark_assist = spark_assist
        self.stop_split = stop_split
        self.remain = remain
        self.speed = speed
        self.volume = volume
        self.pitch = pitch
        self.bgs = bgs
        self.reg = reg
        self.rdn = rdn
        self.rhy = rhy
        self.encoding = encoding
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.frame_size = frame_size
        self.status = status
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _OralClient(app_id, api_key, api_secret, host_url)
        logger.info("OralClient initialized with parameters")

    def _build_param(self, text: str) -> Dict[str, Any]:
        """Build request parameters for Oral API."""
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                },
                "parameter": {
                    "oral": {
                        "oral_level": self.oral_level,
                        "spark_assist": self.spark_assist,
                        "stop_split": self.stop_split,
                        "remain": self.remain,
                    },
                    "tts": {
                        "vcn": self.vcn,
                        "speed": self.speed,
                        "volume": self.volume,
                        "pitch": self.pitch,
                        "bgs": self.bgs,
                        "reg": self.reg,
                        "rdn": self.rdn,
                        "rhy": self.rhy,
                        "audio": {
                            "encoding": self.encoding,
                            "sample_rate": self.sample_rate,
                            "channels": self.channels,
                            "bit_depth": self.bit_depth,
                            "frame_size": self.frame_size
                        }
                    }
                },
                "payload": {
                    "text": {
                        "encoding": self.text_encoding,
                        "compress": self.text_compress,
                        "format": self.text_format,
                        "status": self.status,
                        "seq": 0,
                        "text": base64.b64encode(text.encode('utf-8')).decode("UTF8")
                    }
                }
            }
            logger.debug(f"Oral Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise OralError(f"Failed to build parameters: {e}")

    def stream(self, text: str) -> Generator[Any, None, None]:
        """Synchronously stream audio chunks for the given text."""
        try:
            logger.info(f"Streaming audio for text: {text[:50]}...")
            self.client.arun(self._build_param(text))
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {e}")
            raise OralError(f"Failed to stream audio: {e}")

    async def astream(self, text: str) -> AsyncGenerator[Any, None]:
        """Asynchronously stream audio chunks for the given text."""
        try:
            logger.info(f"Async streaming audio for text: {text[:50]}...")
            self.client.arun(self._build_param(text))
            async for content in self.client.a_subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                    yield content["data"]
        except Exception as e:
            logger.error(f"Failed to stream audio: {e}")
            raise OralError(f"Failed to stream audio: {e}")
