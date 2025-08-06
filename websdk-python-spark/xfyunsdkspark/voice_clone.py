import base64
import json
import queue
import ssl
import threading
from queue import Queue
import websocket
from typing import (Any,
                    Dict,
                    Generator,
                    AsyncGenerator,
                    Optional)
from typing_extensions import Protocol
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.model.voice_clone_model import (
    AudioInfo,
    PybufInfo,
    ResponseData)
from xfyunsdkcore.errors import VoiceCloneError


class BaseConfig:
    """Base configuration class for common settings"""
    DEFAULT_API_URL = "wss://cn-huabei-1.xf-yun.com/v1/private/voice_clone"
    DEFAULT_TIMEOUT = 30
    DEFAULT_TEXT_ENCODING = "utf8"
    DEFAULT_SAMPLE_RATE = 16000


class VoiceCloneCallback(Protocol):
    """语音合成回调接口"""

    def on_audio_chunk(self, audio_chunk: str, **kwargs: Any) -> None:
        """每次接收到一个音频片段时调用
        
        Args:
            audio_chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _VoiceCloneClient:
    """底层 WebSocket 客户端实现"""

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 text_encoding: str,
                 api_url: Optional[str] = None):
        """Initialize the Voice Clone client
        
        Args:
            app_id: Application ID
            api_key: API key
            api_secret: API secret
            text_encoding: Text encoding
            api_url: Optional custom API URL
        """
        self.api_url = api_url or BaseConfig.DEFAULT_API_URL
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.blocking_audio: AudioInfo = {}
        self.blocking_pybuf: PybufInfo = {"text": ""}
        self.client = websocket
        self.text_encoding = text_encoding
        self.byte = bytearray()
        logger.info("VoiceCloneClient initialized")

    def run(self, param: dict, streaming: bool = False) -> None:
        """Run the WebSocket client
        
        Args:
            param: Request parameters
            streaming: Whether to use streaming mode
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
            ws.streaming = streaming
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {str(e)}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: dict, streaming: bool = False) -> threading.Thread:
        """Run the WebSocket client in a separate thread
        
        Args:
            param: Request parameters
            streaming: Whether to use streaming mode
            
        Returns:
            threading.Thread: The thread running the WebSocket client
        """
        thread = threading.Thread(target=self.run, args=(param, streaming))
        thread.daemon = True
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """Handle WebSocket connection open event"""
        try:
            logger.info("WebSocket connection opened")
            ws.send(json.dumps(ws.param))
        except Exception as e:
            logger.error(f"Failed to send initial message: {str(e)}")
            self.queue.put({"error": f"Failed to send initial message: {str(e)}", "error_code": -1})
            ws.close()

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                error_msg = data['header'].get('message', '')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return

            payload = data.get("payload")
            if payload:
                self._process_payload(ws, payload)
        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            self.queue.put({"error": f"Failed to process message: {str(e)}", "error_code": -1})
            ws.close()

    def _process_payload(self, ws: websocket.WebSocketApp, payload: Dict) -> None:
        """Process the payload from the WebSocket message"""
        try:
            audio_info = payload.get("audio")
            pybuf = payload.get("pybuf")

            if audio_info:
                audio = audio_info["audio"]
                status = audio_info["status"]

                if ws.streaming:
                    self._process_streaming_payload(audio_info, pybuf)
                else:
                    self._process_blocking_payload(audio_info, pybuf, audio)

                if status == 2:
                    self._handle_final_status(ws, pybuf)
        except Exception as e:
            logger.error(f"Failed to process payload: {str(e)}")
            self.queue.put({"error": f"Failed to process payload: {str(e)}", "error_code": -1})
            ws.close()

    def _process_streaming_payload(self, audio_info: Dict, pybuf: Optional[Dict]) -> None:
        """Process streaming mode payload"""
        audio = audio_info["audio"]
        audio_info = AudioInfo(
            audio=base64.b64decode(audio) if audio else None,
            encoding=audio_info.get("encoding"),
            sample_rate=audio_info.get("sample_rate"),
            ced=audio_info.get("ced"),
            type=audio_info.get("type")
        )
        pybuf_info = self._process_pybuf(pybuf) if pybuf else None
        self.queue.put({"data": {"audio": audio_info, "pybuf": pybuf_info}})

    def _process_blocking_payload(self, audio_info: Dict, pybuf: Optional[Dict], audio: Optional[str]) -> None:
        """Process blocking mode payload"""
        if audio_info["status"] == 2:
            self._initialize_blocking_data(audio_info, pybuf)
        if pybuf:
            self.blocking_pybuf["text"] += pybuf.get("text", "")
        if audio:
            self.byte.extend(base64.b64decode(audio))

    def _handle_final_status(self, ws: websocket.WebSocketApp, pybuf: Optional[Dict]) -> None:
        """Handle final status message"""
        if not ws.streaming:
            self.blocking_audio.update({"audio": bytes(self.byte)})
            if pybuf:
                final_text = self.blocking_pybuf["text"]
                if final_text:
                    decoded_str = base64.b64decode(final_text).decode(self.text_encoding)
                    self.blocking_pybuf.update({"text": decoded_str})
            blocking_final = {"audio": self.blocking_audio, "pybuf": self.blocking_pybuf}
            self.queue.put({"data": blocking_final})
        self.queue.put({"done": True})
        ws.close()

    def _process_pybuf(self, pybuf: Dict) -> Optional[PybufInfo]:
        """Process pybuf data"""
        _text = pybuf.get("text", "")
        if _text:
            _text = base64.b64decode(_text).decode(self.text_encoding)
        return PybufInfo(
            text=_text,
            type=pybuf.get("type")
        )

    def _initialize_blocking_data(self, audio_info: Dict, pybuf: Optional[Dict]) -> None:
        """Initialize blocking data structures"""
        self.blocking_audio.update({
            "encoding": audio_info.get("encoding"),
            "sample_rate": audio_info.get("sample_rate"),
            "ced": audio_info.get("ced"),
            "type": audio_info.get("type")
        })
        if pybuf:
            self.blocking_pybuf["type"] = pybuf.get("type")

    def on_error(self, ws: websocket.WebSocketApp, error: Any) -> None:
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {str(error)}")
        self.queue.put({"error": str(error), "error_code": -1})
        ws.close()

    def on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
        """Handle WebSocket connection close event"""
        logger.info(f"WebSocket closed: code={close_status_code}, reason={close_msg}")
        self.queue.put({"done": True})

    def subscribe(self, timeout: int = BaseConfig.DEFAULT_TIMEOUT) -> Generator[Dict, None, None]:
        """Subscribe to the WebSocket messages

        Args:
            timeout: Timeout in seconds

        Yields:
            Dict: Message content

        Raises:
            TimeoutError: If no message is received within the timeout period
            VoiceCloneError: If an error occurs during processing
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"VoiceCloneClient response timeout after {timeout} seconds.")

            if "error" in content:
                raise VoiceCloneError(content["error"], content.get("error_code", -1))

            if "done" in content:
                break
            yield content
            self.queue.task_done()

    async def a_subscribe(self, timeout: int = BaseConfig.DEFAULT_TIMEOUT) -> AsyncGenerator[Dict, None]:
        """Asynchronously subscribe to the WebSocket messages

        Args:
            timeout: Timeout in seconds

        Yields:
            Dict: Message content

        Raises:
            TimeoutError: If no message is received within the timeout period
            VoiceCloneError: If an error occurs during processing
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"VoiceCloneClient response timeout after {timeout} seconds.")

            if "error" in content:
                raise VoiceCloneError(content["error"], content.get("error_code", -1))

            if "done" in content:
                break
            yield content
            self.queue.task_done()


# 上层封装，对外暴露接口
class VoiceCloneClient:
    """封装讯飞 Voice Clone 合成接口，支持流式/非流式

    Attributes:
        app_id: Application ID
        api_key: API key
        api_secret: API secret
        res_id: Resource ID
        host_url: API endpoint URL
        text_encoding: Text encoding (default: utf8)
        text_compress: Text compression method (default: raw)
        text_format: Text format (default: plain)
        language_id: Language ID (default: 0)
        speed: Speech speed (default: 50)
        volume: Volume level (default: 50)
        pybuffer: Pybuffer setting (default: 1)
        pitch: Pitch level (default: 50)
        bgs: Background sound setting (default: 0)
        reg: Region setting (default: 0)
        rdn: Random setting (default: 0)
        rhy: Rhythm setting (default: 0)
        encoding: Audio encoding (default: lame)
        sample_rate: Sample rate (default: 16000)
        vcn: Voice clone name (default: x5_clone)
        status: Status code (default: 2)
        request_timeout: Request timeout in seconds (default: 30)
        callback: Optional callback for audio chunks
    """

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            res_id: str,
            host_url: str = BaseConfig.DEFAULT_API_URL,
            text_encoding: str = BaseConfig.DEFAULT_TEXT_ENCODING,
            text_compress: str = "raw",
            text_format: str = "plain",
            language_id: int = 0,
            speed: int = 50,
            volume: int = 50,
            pybuffer: int = 1,
            pitch: int = 50,
            bgs: int = 0,
            reg: int = 0,
            rdn: int = 0,
            rhy: int = 0,
            encoding: str = "lame",
            sample_rate: int = BaseConfig.DEFAULT_SAMPLE_RATE,
            vcn: str = "x5_clone",
            status: int = 2,
            request_timeout: int = BaseConfig.DEFAULT_TIMEOUT,
            callback: Optional[VoiceCloneCallback] = None):
        """Initialize the Voice Clone client

        Args:
            app_id: Application ID
            api_key: API key
            api_secret: API secret
            res_id: Resource ID
            host_url: API endpoint URL
            text_encoding: Text encoding
            text_compress: Text compression method
            text_format: Text format
            language_id: Language ID
            speed: Speech speed
            volume: Volume level
            pybuffer: Pybuffer setting
            pitch: Pitch level
            bgs: Background sound setting
            reg: Region setting
            rdn: Random setting
            rhy: Rhythm setting
            encoding: Audio encoding
            sample_rate: Sample rate
            vcn: Voice clone name
            status: Status code
            request_timeout: Request timeout in seconds
            callback: Optional callback for audio chunks
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.text_encoding = text_encoding
        self.text_compress = text_compress
        self.text_format = text_format
        self.res_id = res_id
        self.language_id = language_id
        self.speed = speed
        self.volume = volume
        self.pybuffer = pybuffer
        self.pitch = pitch
        self.bgs = bgs
        self.reg = reg
        self.rdn = rdn
        self.rhy = rhy
        self.encoding = encoding
        self.sample_rate = sample_rate
        self.vcn = vcn
        self.status = status
        self.request_timeout = request_timeout
        self.callback = callback

        self.client = _VoiceCloneClient(app_id, api_key, api_secret, text_encoding, host_url)
        logger.info("VoiceCloneClient initialized with parameters")

    def _build_param(self, text: str) -> Dict[str, Any]:
        """Build request parameters

        Args:
            text: Text to be synthesized

        Returns:
            Dict[str, Any]: Request parameters

        Raises:
            VoiceCloneError: If text encoding fails
        """
        try:
            param: Dict[str, Any] = {
                "header": {
                    "app_id": self.app_id,
                    "status": self.status,
                    "res_id": self.res_id
                },
                "parameter": {
                    "tts": {
                        "rhy": self.rhy,
                        "vcn": self.vcn,
                        "volume": self.volume,
                        "pybuffer": self.pybuffer,
                        "speed": self.speed,
                        "pitch": self.pitch,
                        "bgs": self.bgs,
                        "reg": self.reg,
                        "rdn": self.rdn,
                        "LanguageID": self.language_id,
                        "audio": {
                            "encoding": self.encoding,
                            "sample_rate": self.sample_rate,
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
                        "text": base64.b64encode(text.encode('utf-8')).decode('utf-8')
                    }
                }
            }

            logger.debug(f"Voice Clone Request Parameters: {param}")
            return param
        except Exception as e:
            logger.error(f"Failed to build parameters: {str(e)}")
            raise VoiceCloneError(f"Failed to build parameters: {str(e)}")

    def generate(self, text: str) -> Generator[ResponseData, None, None]:
        """Synchronously generate complete audio

        Args:
            text: Text to be synthesized

        Yields:
            ResponseData: Audio data

        Raises:
            VoiceCloneError: If synthesis fails
        """
        try:
            logger.info(f"Generating audio for text: {text[:50]}...")
            self.client.arun(self._build_param(text), streaming=False)
            completion = {}
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    completion = ResponseData.from_dict(content["data"])
                    if self.callback:
                        self.callback.on_audio_chunk(completion, final=True)
            return completion
        except Exception as e:
            logger.error(f"Failed to generate audio: {str(e)}")
            raise VoiceCloneError(f"Failed to generate audio: {str(e)}")

    def stream(self, text: str) -> Generator[ResponseData, None, None]:
        """Synchronously stream audio chunks

        Args:
            text: Text to be synthesized

        Yields:
            ResponseData: Audio data chunks

        Raises:
            VoiceCloneError: If streaming fails
        """
        try:
            logger.info(f"Streaming audio for text: {text[:50]}...")
            self.client.arun(self._build_param(text), streaming=True)
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    completion = ResponseData.from_dict(content["data"])
                    if self.callback:
                        self.callback.on_audio_chunk(completion, final=False)
                    yield completion
        except Exception as e:
            logger.error(f"Failed to stream audio: {str(e)}")
            raise VoiceCloneError(f"Failed to stream audio: {str(e)}")

    async def astream(self, text: str) -> AsyncGenerator[ResponseData, None]:
        """Asynchronously stream audio chunks

        Args:
            text: Text to be synthesized

        Yields:
            ResponseData: Audio data chunks

        Raises:
            VoiceCloneError: If streaming fails
        """
        try:
            logger.info(f"Async streaming audio for text: {text[:50]}...")
            self.client.arun(self._build_param(text), streaming=True)
            async for content in self.client.a_subscribe(timeout=self.request_timeout):
                if "data" in content:
                    completion = ResponseData.from_dict(content["data"])
                    if self.callback:
                        self.callback.on_audio_chunk(completion, final=False)
                    yield completion
        except Exception as e:
            logger.error(f"Failed to stream audio: {str(e)}")
            raise VoiceCloneError(f"Failed to stream audio: {str(e)}")
