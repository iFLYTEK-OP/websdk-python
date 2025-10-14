"""
口语客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspark.oral_client import OralClient

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestOralClient:
    """口语客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = OralClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = OralClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    def test_success(self):
        """测试客户端属性"""
        client = OralClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            encoding="raw",
            sample_rate=16000,
            vcn='x5_lingfeiyi_flow'
        )

        # 流式生成音频
        text = "我是科大讯飞超拟人, 请问有什么可以帮到您"

        for chunk in client.stream(text):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

