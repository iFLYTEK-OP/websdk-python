"""
简历生成客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkspark.resume_generate_client import ResumeGenClient


class TestResumeGenerateClient:
    """简历生成客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = ResumeGenClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = ResumeGenClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    @patch('xfyunsdkspark.resume_generate_client.ResumeGenClient.post')
    def test_send(self, mock_send):
        """测试客户端属性"""
        client = ResumeGenClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.send('123')
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

