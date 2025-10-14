"""
通用识别客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkocr.rec_ocr_client import RecOCRClient, RecOCREnum


class TestRecOCRClient:
    """通用识别客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = RecOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert RecOCREnum.CURRENCY.get_desc() == "物体识别"
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = RecOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = RecOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
    
    @patch('xfyunsdkocr.rec_ocr_client.RecOCRClient.post')
    def test_place(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = RecOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')
        
        # 调用 send 方法
        result = client.scene("base64_encoded_image", "1")

        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkocr.rec_ocr_client.RecOCRClient.post')
    def test_scene(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = RecOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        result = client.place("base64_encoded_image", "1")

        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkocr.rec_ocr_client.RecOCRClient.post')
    def test_currency(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = RecOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        result = client.currency("base64_encoded_image", "1")

        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

