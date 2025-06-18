import asyncio
from typing import Optional, Dict, Any, Union, Tuple, IO
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
