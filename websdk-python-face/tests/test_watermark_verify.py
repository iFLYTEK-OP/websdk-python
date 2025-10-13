"""
人脸水印照比对客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkface.watermark_verify_client import WatermarkVerifyClient


class TestWatermarkVerifyClient:
    """人脸水印照比对客户端测试类"""
    
    def test_client_initialization_with_defaults(self):
        """测试使用默认参数初始化客户端"""
        client = WatermarkVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_initialization_with_params(self):
        """测试使用自定义参数初始化客户端"""
        client = WatermarkVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            auto_rotate=True
        )
        assert client.auto_rotate == True
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = WatermarkVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'auto_rotate')
    
    def test_client_has_required_methods(self):
        """测试客户端有必要的方法"""
        client = WatermarkVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'send')
        assert callable(getattr(client, 'send', None))
    
    def test_client_type(self):
        """测试客户端类型"""
        client = WatermarkVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert isinstance(client, WatermarkVerifyClient)

    @patch('xfyunsdkface.watermark_verify_client.WatermarkVerifyClient.post')
    def test_send_method_exists(self, mock_send):
        """测试 send 方法存在并可调用"""
        client = WatermarkVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        result = client.send("base64_image", "jpg")

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

