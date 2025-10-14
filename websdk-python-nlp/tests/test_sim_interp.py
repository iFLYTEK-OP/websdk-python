"""
同声传译客户端单元测试
"""
import asyncio

import pytest
import os
from xfyunsdknlp.sim_interp_client import SimInterpClient, SimInterpError

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestSimInterpClient:
    """同声传译客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = SimInterpClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.language == "zh_cn"
        assert client.from_lang == "cn"
        assert client.to_lang == "en"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = SimInterpClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            vcn="x2_xiaomei",
            language="en",
            from_lang="en",
            to_lang="cn",
            domain="custom_domain",
            encoding="lame",
            sample_rate=8000,
            frame_size=640,
            request_timeout=60
        )
        assert client.vcn == "x2_xiaomei"
        assert client.language == "en"
        assert client.from_lang == "en"
        assert client.to_lang == "cn"
        assert client.domain == "custom_domain"
        assert client.encoding == "lame"
        assert client.sample_rate == 8000
        assert client.frame_size == 640
        assert client.request_timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = SimInterpClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'language')
        assert hasattr(client, 'from_lang')
        assert hasattr(client, 'to_lang')
        assert hasattr(client, 'vcn')
        assert hasattr(client, 'domain')
        assert hasattr(client, 'encoding')
    
    def test_build_param_method(self):
        """测试 _build_param 方法"""
        client = SimInterpClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 调用内部方法
        param = client._build_param()
        
        # 验证参数结构
        assert "header" in param
        assert "parameter" in param
        assert "payload" in param
        assert param["header"]["app_id"] == "test_app_id"
        assert "ist" in param["parameter"]
        assert "streamtrans" in param["parameter"]
        assert "tts" in param["parameter"]

    def test_build_error(self):
        """测试 失败  方法"""
        # 初始化客户端
        client = SimInterpClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'original.pcm')
        f = open(file_path, 'rb')
        try:
            client.stream(f)
        except Exception as e:
            assert isinstance(e, SimInterpError)

    def test_build_success(self):
        """测试 成功  方法"""
        # 初始化客户端
        client = SimInterpClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            encoding="lame"
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'original.pcm')
        f = open(file_path, 'rb')
        for chunk in client.stream(f):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

