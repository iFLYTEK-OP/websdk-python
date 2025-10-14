"""
通用文字识别客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdkocr.general_words_client import WordOCRClient, WordOCREnum


class TestWordOCRClient:
    """通用文字识别客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = WordOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.language == "cn|en"
        assert client.location == "false"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = WordOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            language="en",
            location="true",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.language == "en"
        assert client.location == "true"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = WordOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'language')
        assert hasattr(client, 'location')
    
    @patch('xfyunsdkocr.general_words_client.WordOCRClient.post')
    def test_general_method_exists(self, mock_post):
        """测试 general 方法存在并可调用"""
        client = WordOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 general 方法
        result = client.general("base64_encoded_image")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdkocr.general_words_client.WordOCRClient.post')
    def test_handwriting_method_exists(self, mock_post):
        """测试 handwriting 方法存在并可调用"""
        client = WordOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 handwriting 方法
        result = client.handwriting("base64_encoded_image")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_build_param_method(self):
        """测试 _build_param 方法"""
        client = WordOCRClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            language="en",
            location="true"
        )
        
        # 调用内部方法
        param = client._build_param()
        
        # 验证参数结构
        assert "language" in param
        assert "location" in param
        assert param["language"] == "en"
        assert param["location"] == "true"
    
    def test_word_ocr_enum(self):
        """测试 WordOCREnum 枚举类型"""
        assert WordOCREnum.GENERAL.get_url() == "https://webapi.xfyun.cn/v1/service/v1/ocr/general"
        assert WordOCREnum.HANDWRITING.get_url() == "https://webapi.xfyun.cn/v1/service/v1/ocr/handwriting"
        assert WordOCREnum.GENERAL.get_method() == "POST"
        assert WordOCREnum.HANDWRITING.get_method() == "POST"
        assert WordOCREnum.GENERAL.get_desc() == "印刷文字识别"
        assert WordOCREnum.HANDWRITING.get_desc() == "手写文字识别"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

