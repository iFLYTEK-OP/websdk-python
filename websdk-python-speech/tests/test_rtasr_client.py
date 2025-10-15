"""
实时转写客户端单元测试
"""
import pytest
import json
import os
from xfyunsdkspeech.rtasr_client import RtasrClient, _RtasrClient

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestRtasrClient:
    """实时转写客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = RtasrClient(
            app_id="test_app_id",
            api_key="test_api_key"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = RtasrClient(
            app_id="test_app_id",
            api_key="test_api_key"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')

    def test_on_error(self):
        """测试 ws回调错误"""
        client = _RtasrClient('app_id', 'api_key', 'api_secret')
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
        try:
            client.run(None, None)
        except Exception as e:
            pass

    def test_success_stream(self):
        """测试 成功"""
        client = RtasrClient(
            app_id=os.getenv('RTASR_ID'),  # 替换为你的应用ID
            api_key=os.getenv('RTASR_KEY'),  # 替换为你的API密钥
        )

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources/rtasr', 'rtasr.pcm')
        f = open(file_path, 'rb')

        for chunk in client.stream(f):
            pass

        client = RtasrClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )
        try:
            for chunk in client.stream(None):
                pass
        except Exception as e:
            pass

    @pytest.mark.asyncio
    async def test_astream(self):
        """测试 astream 异步方法"""
        client = RtasrClient(
            app_id=os.getenv('RTASR_ID'),  # 替换为你的应用ID
            api_key=os.getenv('RTASR_KEY'),  # 替换为你的API密钥
        )

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources/rtasr', 'rtasr.pcm')
        f = open(file_path, 'rb')

        async for chunk in client.astream(f):
            pass

        client = RtasrClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )
        try:
            async for chunk in client.astream(None):
                pass
        except Exception as e:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

