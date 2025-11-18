"""
文本改写客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.text_rewrite_client import TextRewriteClient


class TestTextRewriteClient:
    """文本改写客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = TextRewriteClient(
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
        assert client.level == "L1"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = TextRewriteClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            level="L2",
            status=2,
            encoding="utf16",
            compress="gzip",
            format="json",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.level == "L2"
        assert client.status == 2
        assert client.encoding == "utf16"
        assert client.compress == "gzip"
        assert client.format == "json"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = TextRewriteClient(
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
        assert hasattr(client, 'level')
    
    @patch('xfyunsdknlp.text_rewrite_client.TextRewriteClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = TextRewriteClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')
        
        # 调用 send 方法
        result = client.send("测试文本改写")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'
    
    @patch('xfyunsdknlp.text_rewrite_client.TextRewriteClient.post')
    def test_send_with_custom_level(self, mock_post):
        """测试带自定义级别的 send 方法"""
        client = TextRewriteClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"header": {"code": 0}}')
        
        # 调用 send 方法
        result = client.send("测试文本改写", level="L3")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"header": {"code": 0}}'
    
    def test_build_param_method(self):
        """测试 _build_param 方法"""
        client = TextRewriteClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 调用内部方法
        param = client._build_param("测试文本改写")
        
        # 验证参数结构
        assert "header" in param
        assert "parameter" in param
        assert "payload" in param
        assert param["header"]["app_id"] == "test_app_id"
        assert param["header"]["status"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

