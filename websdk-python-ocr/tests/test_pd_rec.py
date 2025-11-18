"""
PD识别客户端单元测试
"""
import pytest
import os
import base64
from xfyunsdkocr.pd_rec_client import PDRecClient, PDRecError

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestPdRecClient:
    """PD识别客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = PDRecClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"

    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = PDRecClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
        )
        assert client.host_url == "https://custom.url"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = PDRecClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    def test_client_error(self):
        """测试客户端属性"""
        client = PDRecClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        # 获取识别文件路径
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'pdrec.jpg')
        with open(file_path, "rb") as file:
            encoded_string = base64.b64encode(file.read())
        # 发送请求
        try:
            client.generate(encoded_string.decode("utf-8"), "1", "jpg")
        except Exception as e:
            assert isinstance(e, PDRecError)

    def test_client_success(self):
        """测试客户端属性"""
        client = PDRecClient(
            app_id=os.getenv('APP_ID'),
            api_key=os.getenv('API_KEY'),
            api_secret=os.getenv('API_SECRET'),
        )
        # 获取识别文件路径
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'pdrec.jpg')
        with open(file_path, "rb") as file:
            encoded_string = base64.b64encode(file.read())
        # 发送请求
        client.generate(encoded_string.decode("utf-8"), "1", "jpg")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

