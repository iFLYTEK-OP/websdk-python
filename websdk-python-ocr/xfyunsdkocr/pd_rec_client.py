import base64
import json
import queue
import ssl
import threading
from queue import Queue
from typing import Any, Dict, Generator, AsyncGenerator, Optional
from typing_extensions import Protocol
import websocket
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import PDRecError

# WebSocket API URLs
HOST_URL = "wss://ws-api.xf-yun.com/v1/private/ma008db16"
DEFAULT_TIMEOUT = 30


class PDRecCallback(Protocol):
    """图片还原文档回调接口协议"""

    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个片段时调用

        Args:
            chunk: 数据片段
            **kwargs: 其他参数
        """
        ...


class _PDRecClient:
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
        self.byte = bytearray()
        self.client = websocket
        logger.info("PDRecClient initialized")

    def run(self, param: Dict[str, Any]) -> None:
        """运行 WebSocket 客户端

        Args:
            param: 请求参数
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
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        except Exception as e:
            logger.error(f"WebSocket client error: {str(e)}")
            self.queue.put({"error": str(e), "error_code": -1})

    def arun(self, param: Dict[str, Any]) -> threading.Thread:
        """在新线程中运行 WebSocket 客户端

        Args:
            param: 请求参数
        Returns:
            运行中的线程对象
        """
        thread = threading.Thread(target=self.run, args=(param,))
        thread.start()
        return thread

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        """WebSocket 连接建立时回调"""
        ws.send(json.dumps(ws.param))

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """处理 WebSocket 消息回调"""
        try:
            data = json.loads(message)
            header = data.get("header", {})
            code = header.get("code", -1)
            status = header.get("status")

            if code != 0:
                error_msg = header.get('message', 'Unknown error')
                logger.error(f"API error: Code {code}, Message: {error_msg}")
                self.queue.put({"error": f"Error Code: {code}, Message: {error_msg}", "error_code": code})
                ws.close()
                return

            self.queue.put({"data": data})
            payload = data.get("payload", {})

            if status == 1 and payload:
                result = payload.get("result")
                if result:
                    document_chunk = base64.b64decode(result.get("text", ""))
                    self.byte.extend(document_chunk)

            elif status == 2:
                self.queue.put({"byte": self.byte})
                self.queue.put({"done": True})
                ws.close()

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON message")
            self.queue.put({"error": "Invalid JSON format", "error_code": -1})
            ws.close()

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
            SparkIatError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"SparkIatClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise PDRecError(content["error"], content.get("error_code", -1))
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
            SparkIatError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"SparkIatClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise PDRecError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class PDRecClient:
    """讯飞 图片还原文档 接口封装，支持流式同步/异步调用"""

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            category: str = "ch_en_public_cloud",
            encoding: str = "utf8",
            compress: str = "raw",
            format: str = "plain",
            host_url: str = None,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[PDRecCallback] = None):
        """初始化 PDRecClient

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            category: ch_en_public_cloud：中英文识别
            encoding: 文本编码 可选值：utf8(默认)、 gb2312
            compress: 文本压缩格式 可选值：raw(默认)、 gzip
            format: 文本格式 可选值：plain(默认)、json、 xml
            host_url: 自定义API地址
            request_timeout: 请求超时时间
            callback: 可选回调
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.category = category
        self.encoding = encoding
        self.compress = compress
        self.format = format
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _PDRecClient(app_id, api_key, api_secret, host_url)
        logger.info("PDRecClient initialized with parameters")

    def _build_param(self, img_base64: str, result_type: str, img_format: str) -> Dict[str, Any]:
        """构建请求参数"""
        param: Dict[str, Any] = {
            "header": {
                "app_id": self.app_id,
                "status": 2
            },
            "parameter": {
                "s15282f39": {
                    "category": self.category,
                    "result": {
                        "encoding": self.encoding,
                        "compress": self.compress,
                        "format": self.format
                    }
                },
                "s5eac762f": {
                    "result_type": result_type,
                    "result": {
                        "encoding": self.encoding,
                        "compress": self.compress,
                        "format": self.format
                    }
                }
            },
            "payload": {
                "test": {
                    "encoding": img_format,
                    "image": img_base64,
                    "status": 3,
                }
            }
        }
        logger.debug(f"PDRec Request Parameters: {param}")
        return param

    def generate(self, img_base64: str, result_type: str, img_format: str) -> bytes:
        """同步转换文档

        Args:
            img_base64: 图像base64编码后数据，最小尺寸:0B，最大尺寸:10485760B
            result_type: 音频流对象 结果文件获，可选值：
                         0:excel
                         1:doc
                         2:ppt
            img_format: 转写结果 图像编码,可选值：
                        jpg：jpg格式(默认)
                        jpeg：jpeg格式
                        png：png格式
                        bmp：bmp格式
        Raises:
            PDRecError: 转换失败
        """
        try:
            logger.info("Start conversion...")
            self.client.arun(self._build_param(img_base64, result_type, img_format))
            completion = bytearray()
            for content in self.client.subscribe(timeout=self.request_timeout):
                if "data" in content:
                    if self.callback:
                        self.callback.chunk(content["data"])
                if "byte" in content:
                    completion.extend(content["byte"])
            return completion
        except Exception as e:
            logger.error(f"Conversion failure: {str(e)}")
            raise PDRecError(f"Conversion failure: {str(e)}")
