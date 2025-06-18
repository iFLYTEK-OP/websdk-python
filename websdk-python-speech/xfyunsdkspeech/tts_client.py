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
from xfyunsdkcore.errors import TTSError

DEFAULT_API_URL = "wss://tts-api.xfyun.cn/v2/tts"
DEFAULT_TIMEOUT = 30


class TTSCallback(Protocol):
    """TTS synthesis callback interface."""
    def chunk(self, audio_chunk: str, **kwargs: Any) -> None:
        """Called when an audio chunk is received."""
        ...


class _TTSClient:
    """Low-level WebSocket client for TTS."""
    def __init__(self, app_id: str, api_key: str, api_secret: str, api_url: Optional[str] = None):
        self.api_url = api_url or DEFAULT_API_URL
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("TTSClient initialized")

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
            code = data["code"]
            if code != 0:
                error_msg = data.get('message', '')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return
            result = data.get("data")
            if result:
                self.queue.put({"data": result})
                if result["status"] == 2:
                    self.queue.put({"done": True})
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
                raise TimeoutError(f"TTSClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise TTSError(content["error"], content.get("error_code", -1))
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
                raise TimeoutError(f"TTSClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise TTSError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class TTSClient:
    """High-level TTS client for Xunfei TTS API, supports streaming and callback."""
    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            vcn: str,
            host_url: str = None,
            aue: str = "lame",
            auf: str = None,
            sfl: int = 1,
            speed: int = None,
            volume: int = None,
            pitch: int = None,
            bgs: int = None,
            tte: str = "UTF8",
            reg: str = None,
            rdn: str = None,
            status: int = 2,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[TTSCallback] = None):
        """
        初始化 TTSClient
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.vcn = vcn
        self.aue = aue
        self.auf = auf
        self.sfl = sfl
        self.speed = speed
        self.volume = volume
        self.pitch = pitch
        self.bgs = bgs
        self.tte = tte
        self.reg = reg
        self.rdn = rdn
        self.status = status
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _TTSClient(app_id, api_key, api_secret, host_url)
        logger.info("TTSClient initialized with parameters")

    def _build_param(self, text: str) -> Dict[str, Any]:
        """Build request parameters for TTS API."""
        try:
            encoded_text = base64.b64encode(
                text.encode('utf-16') if self.tte.upper() == "UNICODE" else text.encode('utf-8')
            ).decode("UTF8")
            param: Dict[str, Any] = {
                "common": {"app_id": self.app_id},
                "business": {
                    "aue": self.aue,
                    "sfl": self.sfl,
                    "auf": self.auf,
                    "vcn": self.vcn,
                    "speed": self.speed,
                    "volume": self.volume,
                    "pitch": self.pitch,
                    "bgs": self.bgs,
                    "tte": self.tte,
                    "reg": self.reg,
                    "rdn": self.rdn,
                },
                "data": {"status": self.status, "text": encoded_text}
            }
            logger.debug(f"TTS Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {e}")
            raise TTSError(f"Failed to build parameters: {e}")

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
            raise TTSError(f"Failed to stream audio: {e}")

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
            raise TTSError(f"Failed to stream audio: {e}")
