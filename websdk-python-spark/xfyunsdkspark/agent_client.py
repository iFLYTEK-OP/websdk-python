"""
星火智能体客户端模块

提供与星火智能体API交互的功能，包括工作流执行、恢复和文件上传等操作。
"""

from typing import Optional, Any, List, Union, BinaryIO, Dict, Iterator
from dataclasses import dataclass, asdict, field
from xfyunsdkcore.http_client import HttpClient
from xfyunsdkcore.errors import AgentClientError
from enum import Enum
import mimetypes
from pathlib import Path


class AgentEndpoint(Enum):
    """星火智能体API端点枚举"""

    COMPLETIONS = ("执行工作流", "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions", "POST")
    RESUME = ("恢复运行工作流", "https://xingchen-api.xf-yun.com/workflow/v1/resume", "POST")
    UPLOAD_FILE = ("文件上传", "https://xingchen-api.xf-yun.com/workflow/v1/upload_file", "POST")

    def __init__(self, description: str, url: str, method: str):
        self._description = description
        self._url = url
        self._method = method

    @property
    def description(self) -> str:
        """获取端点描述"""
        return self._description

    @property
    def url(self) -> str:
        """获取端点URL"""
        return self._url

    @property
    def method(self) -> str:
        """获取HTTP方法"""
        return self._method


@dataclass
class AgentChatParam:
    """智能体聊天参数"""

    flow_id: str
    parameters: Any
    uid: Optional[str] = None
    stream: bool = True
    ext: Optional[Any] = None
    chat_id: Optional[str] = None
    history: Optional[List[Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，过滤None值"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def validate(self) -> None:
        """验证参数有效性"""
        if not self.flow_id:
            raise ValueError("flow_id不能为空")
        if self.parameters is None:
            raise ValueError("parameters不能为空")


@dataclass
class AgentResumeParam:
    """智能体恢复参数"""

    event_id: str
    event_type: str
    content: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，过滤None值"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def validate(self) -> None:
        """验证参数有效性"""
        if not self.event_id:
            raise ValueError("event_id不能为空")
        if not self.event_type:
            raise ValueError("event_type不能为空")
        if not self.content:
            raise ValueError("content不能为空")


class AgentClient(HttpClient):
    """
    星火智能体客户端
    
    提供与星火智能体API交互的功能，包括工作流执行、恢复和文件上传等操作。
    
    Attributes:
        app_id: 应用ID
        api_key: API密钥
        api_secret: API密钥
        timeout: 请求超时时间（秒）
        enable_retry: 是否启用重试
        max_retries: 最大重试次数
        retry_interval: 重试间隔（秒）
    """

    # 默认配置
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_INTERVAL = 1
    DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    def __init__(self,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 timeout: int = DEFAULT_TIMEOUT,
                 enable_retry: bool = False,
                 max_retries: int = DEFAULT_MAX_RETRIES,
                 retry_interval: int = DEFAULT_RETRY_INTERVAL,
                 max_file_size: int = DEFAULT_MAX_FILE_SIZE):
        """
        初始化智能体客户端
        
        Args:
            app_id: 应用ID
            api_key: API密钥
            api_secret: API密钥
            timeout: 请求超时时间（秒）
            enable_retry: 是否启用重试
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            max_file_size: 最大文件大小（字节）
        """
        super().__init__(
            host_url="https://xingchen-api.xf-yun.com",
            app_id=app_id,
            api_key=api_key,
            api_secret=api_secret,
            timeout=timeout,
            enable_retry=enable_retry,
            max_retries=max_retries,
            retry_interval=retry_interval
        )
        self.max_file_size = max_file_size

    def _build_auth_headers(self) -> Dict[str, str]:
        """构建认证请求头"""
        if not self.api_key or not self.api_secret:
            raise AgentClientError("API密钥和密钥不能为空")
        return {"Authorization": f"Bearer {self.api_key}:{self.api_secret}"}

    def completion(self, param: AgentChatParam) -> Union[str, Iterator[str]]:
        """
        执行智能体工作流
        
        Args:
            param: 聊天参数
            
        Returns:
            流式请求返回生成器，非流式请求返回响应文本
            
        Raises:
            AgentClientError: 请求失败
            ValueError: 参数验证失败
        """
        try:
            param.validate()
        except ValueError as e:
            raise ValueError(f"参数验证失败: {e}")

        headers = self._build_auth_headers()

        try:
            if param.stream:
                # 流式请求
                headers.update({"Accept": "text/event-stream"})
                return self.sse_post(
                    url=AgentEndpoint.COMPLETIONS.url,
                    json=param.to_dict(),
                    headers=headers
                )
            else:
                # 非流式请求
                response = self.post(
                    url=AgentEndpoint.COMPLETIONS.url,
                    json=param.to_dict(),
                    headers=headers
                )
                response.raise_for_status()
                return response.text

        except Exception as e:
            raise AgentClientError(f"执行工作流失败: {str(e)}") from e

    def resume(self, param: AgentResumeParam) -> Iterator[str]:
        """
        恢复运行工作流
        
        Args:
            param: 恢复参数
            
        Returns:
            流式响应生成器
            
        Raises:
            AgentClientError: 请求失败
            ValueError: 参数验证失败
        """
        try:
            param.validate()
        except ValueError as e:
            raise ValueError(f"参数验证失败: {e}")

        headers = self._build_auth_headers()
        headers.update({"Accept": "text/event-stream"})

        try:
            return self.sse_post(
                url=AgentEndpoint.RESUME.url,
                json=param.to_dict(),
                headers=headers
            )
        except Exception as e:
            raise AgentClientError(f"恢复工作流失败: {str(e)}") from e

    def upload(self, file: Union[str, Path, BinaryIO, bytes],
               filename: Optional[str] = None) -> str:
        """
        上传文件到星火智能体平台
        
        Args:
            file: 文件路径、Path对象、文件对象或字节数据
            filename: 文件名，当file为字节数据或文件对象时必须提供
            
        Returns:
            上传响应结果
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 参数错误
            AgentClientError: 上传失败
        """
        headers = self._build_auth_headers()

        try:
            files = self._prepare_file_for_upload(file, filename)
            response = self.post(
                url=AgentEndpoint.UPLOAD_FILE.url,
                files=files,
                headers=headers
            )
            response.raise_for_status()
            return response.text

        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            else:
                raise AgentClientError(f"文件上传失败: {str(e)}") from e

    def _prepare_file_for_upload(self, file: Union[str, Path, BinaryIO, bytes],
                                 filename: Optional[str]) -> Dict[str, tuple]:
        """
        准备文件用于上传
        
        Args:
            file: 文件输入
            filename: 文件名
            
        Returns:
            格式化的文件字典
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 参数错误
        """
        if isinstance(file, (str, Path)):
            # 文件路径
            file_path = Path(file)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 获取文件名
            filename = filename or file_path.name

            # 验证文件大小
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"文件大小超过限制: {file_size} bytes (最大: {self.max_file_size} bytes)")

            # 打开文件
            file_obj = open(file_path, "rb")
            return {"file": (filename, file_obj, self._get_mime_type(filename))}

        elif isinstance(file, bytes):
            # 字节数据
            if not filename:
                raise ValueError("当file为字节数据时，必须提供filename参数")

            return {"file": (filename, file, self._get_mime_type(filename))}

        elif hasattr(file, 'read'):
            # 文件对象
            if not filename:
                raise ValueError("当file为文件对象时，必须提供filename参数")

            return {"file": (filename, file, self._get_mime_type(filename))}

        else:
            raise ValueError("不支持的文件类型，file参数必须是文件路径、Path对象、文件对象或字节数据")

    def _get_mime_type(self, filename: str) -> str:
        """
        根据文件名获取MIME类型
        
        Args:
            filename: 文件名
            
        Returns:
            MIME类型
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 可以在这里添加清理逻辑
        pass
