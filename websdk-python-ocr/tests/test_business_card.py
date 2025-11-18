"""
名片识别客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkocr.business_card_client import BusinessCardClient


class TestBusinessCardClient:
    """名片识别客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = BusinessCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.pic_required == "0"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = BusinessCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            pic_required="1",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.pic_required == "1"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = BusinessCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'pic_required')
    
    @patch('xfyunsdkocr.business_card_client.BusinessCardClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = BusinessCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send 方法
        result = client.send("base64_encoded_image")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdkocr.business_card_client.BusinessCardClient.post')
    def test_send_with_optional_params(self, mock_post):
        """测试带可选参数的 send 方法"""
        client = BusinessCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send 方法
        result = client.send("base64_encoded_image", imei="123456", osid="android", ua="test_ua")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_build_param_method(self):
        """测试 _build_param 方法"""
        client = BusinessCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            pic_required="1"
        )
        
        # 调用内部方法
        param = client._build_param("123456", "android", "test_ua")
        
        # 验证参数结构
        assert "engine_type" in param
        assert param["engine_type"] == "business_card"
        assert param["pic_required"] == "1"
        assert param["imei"] == "123456"
        assert param["osid"] == "android"
        assert param["ua"] == "test_ua"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

