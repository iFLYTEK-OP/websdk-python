import base64
import json
import queue
import ssl
import threading
import time
from enum import Enum
from queue import Queue
from typing import Any, Dict, Generator, AsyncGenerator, Optional
from typing_extensions import Protocol
import websocket
from xfyunsdkcore.log.logger import logger
from xfyunsdkcore.signature import Signature
from xfyunsdkcore.errors import SparkIatError

# WebSocket API URLs
CN_LANGUAGE_API = "wss://iat.xf-yun.com/v1"
MULTI_LANGUAGE_API = "wss://iat.cn-huabei-1.xf-yun.com/v1"
DEFAULT_TIMEOUT = 30
WAIT_MILLIS = 40  # 发送帧间隔（毫秒）
STATUS_FIRST_FRAME = 0  # 第一帧
STATUS_CONTINUE_FRAME = 1  # 中间帧
STATUS_LAST_FRAME = 2  # 最后一帧


class SparkIatModel(Enum):
    ZH_CN_MANDARIN = ("中文大模型", "mandarin", CN_LANGUAGE_API, "zh_cn")
    ZH_CN_MULACC = ("方言大模型", "mulacc", MULTI_LANGUAGE_API, "zh_cn")
    MUL_CN_MANDARIN = ("多语种大模型", "mul_cn", MULTI_LANGUAGE_API, "mul_cn")

    def get_url(self):
        return self.value[2]

    def get_accent(self):
        return self.value[1]

    def get_desc(self):
        return self.value[0]

    def get_lang(self):
        return self.value[3]


class SparkIatCallback(Protocol):
    """实时语音转写回调接口协议"""

    def chunk(self, chunk: str, **kwargs: Any) -> None:
        """每次接收到一个转写片段时调用

        Args:
            chunk: 音频数据片段
            **kwargs: 其他参数
        """
        ...


class _SparkIatClient:
    """底层 WebSocket 客户端实现"""

    def __init__(self,
                 app_id: str,
                 api_key: str,
                 api_secret: str,
                 sim_enum: SparkIatModel = SparkIatModel.ZH_CN_MANDARIN,
                 api_url: Optional[str] = None):
        """初始化底层 WebSocket 客户端

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            sim_enum: 语种模型枚举
            api_url: 可选自定义API地址
        """
        self.api_url = api_url if api_url else sim_enum.get_url()
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.queue: Queue[Dict] = Queue()
        self.client = websocket
        logger.info("SparkIatClient initialized")

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
                    param["payload"]["audio"]["seq"] = seq
                    param["payload"]["audio"]["status"] = status
                    param["payload"]["audio"]["audio"] = str(base64.b64encode(buf), 'utf-8')
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
                ws.close()

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
            SparkIatError: 处理过程中发生错误
        """
        while True:
            try:
                content = self.queue.get(timeout=timeout)
            except queue.Empty:
                logger.error(f"Response timeout after {timeout} seconds")
                raise TimeoutError(f"SparkIatClient response timeout after {timeout} seconds.")
            if "error" in content:
                raise SparkIatError(content["error"], content.get("error_code", -1))
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
                raise SparkIatError(content["error"], content.get("error_code", -1))
            if "done" in content:
                break
            yield content
            self.queue.task_done()


class SparkIatClient:
    """讯飞 SparkIat 语音转写接口封装，支持流式同步/异步调用"""

    def __init__(
            self,
            app_id: str,
            api_key: str,
            api_secret: str,
            iat_model_enum: SparkIatModel,
            ln: str = "none",
            language: str = None,
            format: str = "json",
            domain: str = "slm",
            accent: str = None,
            encoding: str = "raw",
            dwa: str = None,
            smth: int = None,
            eos: int = 6000,
            ptt: int = None,
            rlang: str = None,
            nunum: int = None,
            nbest: int = 0,
            wbest: int = 0,
            vinfo: int = 1,
            dhw: str = None,
            opt: int = None,
            ltc: int = None,
            sample_rate: int = 16000,
            channels: int = 1,
            bit_depth: int = 16,
            text_encoding: int = "utf8",
            text_compress: int = "raw",
            text_format: int = "json",
            frame_size: int = 1280,
            host_url: str = None,
            request_timeout: int = DEFAULT_TIMEOUT,
            callback: Optional[SparkIatCallback] = None):
        """初始化 SparkIatClient

        Args:
            app_id: 应用ID
            api_key: API Key
            api_secret: API Secret
            iat_model_enum: 语音识别模型枚举
            language: 语种
            domain: 应用领域
            accent: 方言
            dwa: 流式识别PGS 返回速度更快，仅中文支持
            smth: 顺滑功能：将语音识别结果中的顺滑词（语气词、叠词）进行标记，业务侧通过标记过滤语气词最终展现识别结果
                  1：开启 ; 0：关闭（默认值）
            eos: 用于设置端点检测的静默时间，单位是毫秒[600,60000]。即静默多长时间后引擎认为音频结束。
            format: 音频格式
            encoding: 编码方式
            ltc: （仅中文支持）是否进行中英文筛选  1:不进行筛选, 2:只出中文, 3:只出英文
            ptt: （仅中文支持）标点预测：在语音识别结果中增加标点符号 1：开启（默认值） 0：关闭
            rlang: （仅中文支持）返回字体指定zh-cn/zh-hk/zh-mo/zh-tw，服务默认是简体字
            vinfo: 返回子句结果对应的起始和结束的端点帧偏移值。端点帧偏移值表示从音频开头起已过去的帧长度。
                   0：关闭（默认值） 1：开启  开启后返回的结果中会增加data.result.vad字段
                   开通并使用了动态修正功能，则该功能无法使用。
            nunum: （仅中文支持）数字规整：将语音识别结果中的原始文字串转为相应的阿拉伯数字或者符号
                    1：开启（默认值） 0：关闭
            dhw: 会话热词，支持utf-8和gb2312；
                    取值样例：“dhw=db2312;你好|大家”（对应gb2312编码）；
                    “dhw=utf-8;你好|大家”（对应utf-8编码）
            opt: 是否输出属性
                0:json格式输出，不带属性,
                1:文本格式输出，不带属性,
                2:json格式输出，带文字属性"wp":"n"和标点符号属性"wp":"p"
            nbest: 取值范围[1,5]，通过设置此参数，获取在发音相似时的句子多侯选结果。设置多候选会影响性能，响应时间延迟200ms左右。
                    该扩展功能若未授权无法使用
            wbest: 取值范围[1,5]，通过设置此参数，获取在发音相似时的词语多侯选结果。设置多候选会影响性能，响应时间延迟200ms左右。
                    该扩展功能若未授权无法使用
            frame_size: 每帧音频大小
            host_url: 自定义API地址
            request_timeout: 请求超时时间
            callback: 可选回调
        """
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_url = host_url
        self.iat_model_enum = iat_model_enum
        self.language = language
        self.domain = domain
        self.accent = accent
        self.encoding = encoding
        self.format = format
        self.eos = eos
        self.smth = smth
        self.dwa = dwa
        self.dhw = dhw
        self.ptt = ptt
        self.rlang = rlang
        self.vinfo = vinfo
        self.opt = opt
        self.nunum = nunum
        self.ltc = ltc
        self.nbest = nbest
        self.wbest = wbest
        self.frame_size = frame_size
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.text_encoding = text_encoding
        self.text_compress = text_compress
        self.text_format = text_format
        self.ln = ln
        self.request_timeout = request_timeout
        self.callback = callback
        self.client = _SparkIatClient(app_id, api_key, api_secret, iat_model_enum, host_url)
        logger.info("SparkIatClient initialized with parameters")

    def _build_param(self) -> Dict[str, Any]:
        """构建请求参数"""
        param: Dict[str, Any] = {
            "header": {
                "app_id": self.app_id,
                "status": 0
            },
            "parameter": {
                "iat": {
                    "domain": self.domain,
                    "language": self.language or self.iat_model_enum.get_lang(),
                    "accent": self.accent or self.iat_model_enum.get_accent(),
                    "eos": self.eos,
                    "vinfo": self.vinfo,
                    "dwa": self.dwa,
                    "result": {
                        "encoding": self.text_encoding,
                        "compress": self.text_compress,
                        "format": self.text_format
                    }
                }
            },
            "payload": {
                "audio": {
                    "encoding": self.encoding,
                    "sample_rate": self.sample_rate,
                    "channels": self.channels,
                    "bit_depth": self.bit_depth,
                    "seq": 0,
                    "status": 0,
                    "audio": ""
                }
            }
        }
        if self.iat_model_enum == SparkIatModel.ZH_CN_MULACC:
            param.update({
                "parameter": {
                    "iat": {
                        "nbest": self.nbest,
                        "wbest": self.wbest,
                        "ptt": self.ptt,
                        "smth": self.smth,
                        "nunum": self.nunum,
                        "opt": self.opt,
                        "dhw": self.dhw,
                        "rlang": self.rlang,
                        "ltc": self.ltc,
                    }
                }
            })
        elif self.iat_model_enum == SparkIatModel.MUL_CN_MANDARIN:
            param.update({
                "parameter": {
                    "iat": {
                        "ln": self.ln,
                    }
                }
            })
        logger.debug(f"SparkIat Request Parameters: {param}")
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
            raise SparkIatError(f"Failed to stream audio: {str(e)}")

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
            raise SparkIatError(f"Failed to stream audio: {str(e)}")
