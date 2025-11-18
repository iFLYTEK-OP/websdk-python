"""
声音克隆客户端单元测试
"""
import json

import pytest
import os
from xfyunsdkspark.voice_clone import VoiceCloneClient, _VoiceCloneClient

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestVoiceClone:
    """声音克隆客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = VoiceCloneClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            res_id="您的声纹ID",
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = VoiceCloneClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            res_id="您的声纹ID",
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    def test_on_error(self):
        """测试客户端属性"""
        client = _VoiceCloneClient('app_id', 'api_key', 'api_secret', 'text_encoding', 'host_url')
        param = {
            "header": {
                "code": -1,
                "message": "位置的错误"
            },
            "payload": {
                "result": {
                    "status": 2
                }
            }
        }
        try:
            client.on_open(None)
        except Exception as e:
            pass
        try:
            client.on_message(None, json.dumps(param))
        except Exception as e:
            pass
        try:
            client._process_payload(None, param)
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

    def test_success(self):
        """测试 成功"""
        client = VoiceCloneClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            res_id="9f65390_ttsclone-1b6344b2-jugym",
        )
        text = "一句话复刻可以通过声纹训练合成对应的音频信息"
        client.generate(text)

    def test_success_stream(self):
        """测试 成功"""
        client = VoiceCloneClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            res_id="9f65390_ttsclone-1b6344b2-jugym",
        )
        text = "一句话复刻可以通过声纹训练合成对应的音频信息"
        for chunk in client.stream(text):
            pass

    @pytest.mark.asyncio
    async def test_astream(self):
        """测试 astream 异步方法"""
        client = VoiceCloneClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            res_id="9f65390_ttsclone-1b6344b2-jugym",
        )
        text = "一句话复刻可以通过声纹训练合成对应的音频信息"
        async for chunk in client.astream(text):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
