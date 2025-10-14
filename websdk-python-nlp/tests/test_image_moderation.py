"""
图片合规客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.imagde_moderation_client import ImageModerationClient
from xfyunsdkcore.errors import ModerationError


class TestImageModerationClient:
    """图片合规客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = ImageModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = ImageModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            biz_type="custom_biz",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.biz_type == "custom_biz"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = ImageModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'biz_type')
    
    @patch('xfyunsdknlp.imagde_moderation_client.ImageModerationClient.post')
    def test_send_with_base64(self, mock_post):
        """测试使用 base64 发送图片"""
        client = ImageModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send 方法
        result = client.send(image_base64="base64_encoded_image")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.imagde_moderation_client.ImageModerationClient.post')
    def test_send_with_url(self, mock_post):
        """测试使用 URL 发送图片"""
        client = ImageModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send 方法
        result = client.send(image_url="https://test.com/image.jpg")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_send_without_image_raises_error(self):
        """测试不提供图片信息时抛出错误"""
        client = ImageModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 验证抛出 ModerationError
        with pytest.raises(ModerationError, match="图片信息不能为空"):
            client.send()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

