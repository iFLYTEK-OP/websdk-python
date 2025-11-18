"""
情感分析客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.sa_client import SaClient


class TestSaClient:
    """情感分析客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = SaClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.type == "dependent"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = SaClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            type="custom_type",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.type == "custom_type"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = SaClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'type')
    
    @patch('xfyunsdknlp.sa_client.SaClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = SaClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send 方法
        result = client.send("测试文本")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

