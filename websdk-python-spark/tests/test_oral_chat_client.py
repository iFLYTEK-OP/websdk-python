"""
口语聊天客户端单元测试
"""
import json
import pytest
import os
import time
from xfyunsdkspark.oral_chat_client import OralChatClient, OralChatParam, OralChatClientError, _OralChatClient

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestOralChatClient:
    """口语聊天客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = OralChatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = OralChatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    def test_on_message(self):
        """测试客户端属性"""
        client = _OralChatClient("test_api_key", "test_api_secret", "wss://sparkos.xfyun.cn/v1/openapi/chat")
        mock_message = {
            "header": {
                "code": -1,
                "message": "未知错误"
            }
        }
        try:
            client.on_message(None, json.dumps(mock_message).encode("utf-8"))
        except Exception as e:
            pass

    def test_validate_param(self):
        """测试 validate_param """
        param = OralChatParam(
            interact_mode=None,
            uid=None
        )
        try:
            param.self_check()
        except Exception as e:
            assert isinstance(e, OralChatClientError)
        param.interact_mode = "continuous_vad"
        try:
            param.self_check()
        except Exception as e:
            assert isinstance(e, OralChatClientError)

    def test_start(self):
        """测试 start 方法"""
        client = OralChatClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
        )

        param = OralChatParam(
            interact_mode="continuous_vad",
            uid="youtestuid"
        )
        _client = client.start(param)

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', '天气16K.wav')
        f = open(file_path, 'rb')

        first_frame = True
        while True:
            data = f.read(1024)
            if not data:
                client.send_msg(data, 2, _client)
                break
            if first_frame:
                client.send_msg(data, 0, _client)
                first_frame = False
            client.send_msg(data, 1, _client)
            time.sleep(0.04)

        client.stop(_client)

        # 打印返回结果
        for msg in client.stream(_client):
            pass

    @pytest.mark.asyncio
    async def test_astream(self):
        """测试 astream 异步方法"""
        client = OralChatClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
        )

        param = OralChatParam(
            interact_mode="continuous_vad",
            uid="youtestuid"
        )
        _client = client.start(param)

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', '天气16K.wav')
        f = open(file_path, 'rb')

        first_frame = True
        while True:
            data = f.read(1024)
            if not data:
                client.send_msg(data, 2, _client)
                break
            if first_frame:
                client.send_msg(data, 0, _client)
                first_frame = False
            client.send_msg(data, 1, _client)
            time.sleep(0.04)

        client.stop(_client)

        # 异步打印返回结果
        async for msg in client.astream(_client):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

