"""
人脸验证客户端单元测试
"""
import pytest
from unittest.mock import patch
from xfyunsdkface.face_verify_client import FaceVerifyClient


class TestFaceVerifyClient:
    """人脸验证客户端测试类"""
    
    def test_client_initialization_with_defaults(self):
        """测试使用默认参数初始化客户端"""
        client = FaceVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_initialization_with_params(self):
        """测试使用自定义参数初始化客户端"""
        client = FaceVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            get_image=True,
            auto_rotate=True
        )
        assert client.get_image == True
        assert client.auto_rotate == True
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = FaceVerifyClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'get_image')
        assert hasattr(client, 'auto_rotate')

    @patch('xfyunsdkface.face_verify_client.FaceVerifyClient.post')
    def test_send_method_exists(self, mock_send):
        """测试 send 方法存在并可调用"""
        client = FaceVerifyClient(
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

