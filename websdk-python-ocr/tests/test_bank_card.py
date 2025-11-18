"""
银行卡识别客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkocr.bank_card_client import BankCardClient


class TestBankCardClient:
    """银行卡识别客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = BankCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.card_number_image == "0"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = BankCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            card_number_image="1",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.card_number_image == "1"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = BankCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'card_number_image')
    
    @patch('xfyunsdkocr.bank_card_client.BankCardClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = BankCardClient(
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
    
    def test_build_param_method(self):
        """测试 _build_param 方法"""
        client = BankCardClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            card_number_image="1"
        )
        
        # 调用内部方法
        param = client._build_param()
        
        # 验证参数结构
        assert "engine_type" in param
        assert param["engine_type"] == "bankcard"
        assert param["card_number_image"] == "1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

