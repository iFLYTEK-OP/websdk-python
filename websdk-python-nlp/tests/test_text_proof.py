"""
公文校对客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.text_proof_client import TextProofClient


class TestTextProofClient:
    """公文校对客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = TextProofClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.status == 3
        assert client.encoding == "utf8"
        assert client.compress == "raw"
        assert client.format == "plain"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = TextProofClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            status=2,
            encoding="utf16",
            compress="gzip",
            format="json",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.status == 2
        assert client.encoding == "utf16"
        assert client.compress == "gzip"
        assert client.format == "json"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = TextProofClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'status')
        assert hasattr(client, 'encoding')
        assert hasattr(client, 'compress')
        assert hasattr(client, 'format')
    
    @patch('xfyunsdknlp.text_proof_client.TextProofClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = TextProofClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')
        
        # 调用 send 方法
        result = client.send("测试公文内容")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'
    
    def test_build_param_method(self):
        """测试 _build_param 方法"""
        client = TextProofClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 调用内部方法
        param = client._build_param("测试公文内容")
        
        # 验证参数结构
        assert "header" in param
        assert "parameter" in param
        assert "payload" in param
        assert param["header"]["app_id"] == "test_app_id"
        assert param["header"]["status"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

