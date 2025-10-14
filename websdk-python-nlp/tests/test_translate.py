"""
机器翻译客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.translate_client import TranslateClient, TranslateEnum


class TestTranslateClient:
    """机器翻译客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = TranslateClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.trans_from == "cn"
        assert client.trans_to == "en"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = TranslateClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            trans_from="en",
            trans_to="jp",
            res_id="test_res",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.trans_from == "en"
        assert client.trans_to == "jp"
        assert client.res_id == "test_res"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = TranslateClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'trans_from')
        assert hasattr(client, 'trans_to')
        assert hasattr(client, 'res_id')
    
    @patch('xfyunsdknlp.translate_client.TranslateClient.post')
    def test_send_ist_method(self, mock_post):
        """测试 send_ist 方法"""
        client = TranslateClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send_ist 方法
        result = client.send_ist("测试文本")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.translate_client.TranslateClient.post')
    def test_send_niu_trans_method(self, mock_post):
        """测试 send_niu_trans 方法"""
        client = TranslateClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send_niu_trans 方法
        result = client.send_niu_trans("测试文本")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.translate_client.TranslateClient.post')
    def test_send_ist_v2_method(self, mock_post):
        """测试 send_ist_v2 方法"""
        client = TranslateClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 send_ist_v2 方法
        result = client.send_ist_v2("测试文本")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_translate_enum(self):
        """测试 TranslateEnum 枚举类型"""
        assert TranslateEnum.IST.get_url() == "https://itrans.xfyun.cn/v2/its"
        assert TranslateEnum.IST_V2.get_url() == "https://itrans.xf-yun.com/v1/its"
        assert TranslateEnum.NIU_TRANS.get_url() == "https://ntrans.xfyun.cn/v2/ots"
        assert TranslateEnum.IST.get_desc() == "自研翻译"
        assert TranslateEnum.IST_V2.get_desc() == "自研机器翻译（新）"
        assert TranslateEnum.NIU_TRANS.get_desc() == "小牛翻译"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

