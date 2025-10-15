"""
语音听写客户端单元测试
"""
import json
import pytest
import os
from xfyunsdkspeech.iat_client import IatClient, _IatClient

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestIatClient:
    """语音听写客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = IatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = IatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    def test_on_error(self):
        """测试 ws回调错误"""
        client = _IatClient('app_id', 'api_key', 'api_secret', False, 'host_url')
        param = {
            "code": -1,
            "message": "未知错误",
            "data": {
                "status": 2
            }
        }
        try:
            client.on_message(None, json.dumps(param))
        except Exception as e:
            pass
        param['code'] = 0
        try:
            client.on_message(None, json.dumps(param))
        except Exception as e:
            pass
        try:
            client.on_error(None, None)
        except Exception as e:
            pass
        try:
            client.on_close(None, 0, "")
        except Exception as e:
            pass

    def test_success_stream(self):
        """测试 成功"""
        client = IatClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            # dwa="wpgs",
            vinfo=1
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources/iat', 'iat_pcm_16k.pcm')
        f = open(file_path, 'rb')

        for chunk in client.stream(f):
            pass

    @pytest.mark.asyncio
    async def test_astream(self):
        """测试 astream 异步方法"""
        client = IatClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            # dwa="wpgs",
            vinfo=1
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources/iat', 'iat_pcm_16k.pcm')
        f = open(file_path, 'rb')

        async for chunk in client.astream(f):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

