"""
ITR识别客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkocr.itr_ocr_client import ItrOCRClient, RecOCREnum


class TestItrOCRClient:
    """ITR识别客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = ItrOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            ocr_type=RecOCREnum.TEACH_PHOTO_PRINT
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = ItrOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            ocr_type=RecOCREnum.TEACH_PHOTO_PRINT,
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = ItrOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            ocr_type=RecOCREnum.TEACH_PHOTO_PRINT
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
    
    @patch('xfyunsdkocr.itr_ocr_client.ItrOCRClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = ItrOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            ocr_type=RecOCREnum.TEACH_PHOTO_PRINT
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')
        
        # 调用 send 方法
        result = client.send("base64_encoded_image")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

