import asyncio
from typing import Optional, Dict, Any, Union, Tuple, IO, Iterator, AsyncIterator
import httpx
from time import sleep


class HttpClient:
    def __init__(self,
                 host_url: str,
                 app_id: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_secret: Optional[str] = None,
                 timeout=30,
                 enable_retry=False,
                 max_retries=3,
                 retry_interval=1):
        self.host_url = host_url
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.retry_interval = retry_interval

    def _sync_request(
            self, method: str, url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None,
            json: Optional[Any] = None,
            files: Optional[Dict[str, Tuple[str, IO, Optional[str]]]] = None,
    ) -> httpx.Response:
        attempt = 0
        while True:
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.request(method, url, params=params, data=data, headers=headers, json=json, files=files)
                    # response.raise_for_status()
                    return response
            except httpx.HTTPError as e:
                attempt += 1
                if not self.enable_retry or attempt > self.max_retries:
                    raise e
                sleep(0.3 * attempt)

    async def _async_request(
            self, method: str, url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            headers: Optional[Dict[str, str]] = None,
            json: Optional[Any] = None,
    ) -> httpx.Response:
        attempt = 0
        while True:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(method, url, params=params, data=data, headers=headers, json=json)
                    # response.raise_for_status()
                    return response
            except httpx.HTTPError as e:
                attempt += 1
                if not self.enable_retry or attempt > self.max_retries:
                    raise e
                await asyncio.sleep(0.3 * attempt)

    def _sync_sse_request(
            self, method: str, url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None,
            json: Optional[Any] = None,
    ) -> Iterator[str]:
        """
        同步SSE流式请求
        返回一个生成器，用于迭代接收到的SSE数据
        """
        attempt = 0
        while True:
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    # 设置SSE相关headers
                    sse_headers = headers or {}
                    sse_headers.update({
                        'Accept': 'text/event-stream',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                    })
                    
                    with client.stream(method, url, params=params, data=data, headers=sse_headers, json=json) as response:
                        # response.raise_for_status()
                        for line_str in response.iter_lines():
                            if line_str:
                                # 忽略空数据
                                if line_str.startswith('data: '):
                                    # 去掉 'data: ' 前缀
                                    data_content = line_str[6:]
                                    # 忽略空数据
                                    if data_content.strip():
                                        yield data_content
                                elif line_str.startswith('event: '):
                                    # 可以处理事件类型
                                    event_type = line_str[7:]
                                    yield f"event: {event_type}"
                                elif line_str.startswith('id: '):
                                    # 可以处理消息ID
                                    msg_id = line_str[4:]
                                    yield f"id: {msg_id}"
                                elif line_str.startswith('retry: '):
                                    # 可以处理重试时间
                                    retry_time = line_str[7:]
                                    yield f"retry: {retry_time}"
                    break
            except httpx.HTTPError as e:
                attempt += 1
                if not self.enable_retry or attempt > self.max_retries:
                    raise e
                sleep(0.3 * attempt)

    async def _async_sse_request(
            self, method: str, url: str,
            params: Optional[Dict[str, Any]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            headers: Optional[Dict[str, str]] = None,
            json: Optional[Any] = None,
    ) -> AsyncIterator[str]:
        """
        异步SSE流式请求
        返回一个异步生成器，用于异步迭代接收到的SSE数据
        """
        attempt = 0
        while True:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # 设置SSE相关headers
                    sse_headers = headers or {}
                    sse_headers.update({
                        'Accept': 'text/event-stream',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                    })
                    
                    async with client.stream(method, url, params=params, data=data, headers=sse_headers, json=json) as response:
                        # response.raise_for_status()
                        async for line_str in response.aiter_lines():
                            if line_str:
                                if line_str.startswith('data: '):
                                    data_content = line_str[6:]  # 去掉 'data: ' 前缀
                                    if data_content.strip():  # 忽略空数据
                                        yield data_content
                                elif line_str.startswith('event: '):
                                    # 可以处理事件类型
                                    event_type = line_str[7:]
                                    yield f"event: {event_type}"
                                elif line_str.startswith('id: '):
                                    # 可以处理消息ID
                                    msg_id = line_str[4:]
                                    yield f"id: {msg_id}"
                                elif line_str.startswith('retry: '):
                                    # 可以处理重试时间
                                    retry_time = line_str[7:]
                                    yield f"retry: {retry_time}"
                    break
            except httpx.HTTPError as e:
                attempt += 1
                if not self.enable_retry or attempt > self.max_retries:
                    raise e
                await asyncio.sleep(0.3 * attempt)

    # 公共接口
    def get(self, url: str, **kwargs) -> httpx.Response:
        return self._sync_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self._sync_request("POST", url, **kwargs)

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        return self._sync_request(method.upper(), url, **kwargs)

    async def async_get(self, url: str, **kwargs) -> httpx.Response:
        return await self._async_request("GET", url, **kwargs)

    async def async_post(self, url: str, **kwargs) -> httpx.Response:
        return await self._async_request("POST", url, **kwargs)

    # SSE流式请求接口
    def sse_get(self, url: str, **kwargs) -> Iterator[str]:
        """
        同步GET SSE流式请求
        返回一个生成器，用于迭代接收到的SSE数据
        """
        return self._sync_sse_request("GET", url, **kwargs)

    def sse_post(self, url: str, **kwargs) -> Iterator[str]:
        """
        同步POST SSE流式请求
        返回一个生成器，用于迭代接收到的SSE数据
        """
        return self._sync_sse_request("POST", url, **kwargs)

    def sse_request(self, method: str, url: str, **kwargs) -> Iterator[str]:
        """
        同步SSE流式请求
        返回一个生成器，用于迭代接收到的SSE数据
        """
        return self._sync_sse_request(method.upper(), url, **kwargs)

    async def async_sse_get(self, url: str, **kwargs) -> AsyncIterator[str]:
        """
        异步GET SSE流式请求
        返回一个异步生成器，用于异步迭代接收到的SSE数据
        """
        return self._async_sse_request("GET", url, **kwargs)

    async def async_sse_post(self, url: str, **kwargs) -> AsyncIterator[str]:
        """
        异步POST SSE流式请求
        返回一个异步生成器，用于异步迭代接收到的SSE数据
        """
        return self._async_sse_request("POST", url, **kwargs)

    async def async_sse_request(self, method: str, url: str, **kwargs) -> AsyncIterator[str]:
        """
        异步SSE流式请求
        返回一个异步生成器，用于异步迭代接收到的SSE数据
        """
        return self._async_sse_request(method.upper(), url, **kwargs)
