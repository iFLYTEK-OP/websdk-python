"""
星火语音转写客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspark.spark_iat_client import SparkIatClient, SparkIatModel

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestSparkIatClient:
    """星火语音转写客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = SparkIatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            iat_model_enum=SparkIatModel.ZH_CN_MANDARIN,
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = SparkIatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            iat_model_enum=SparkIatModel.ZH_CN_MANDARIN,
            language="en",
            domain="custom_domain"
        )
        assert client.language == "en"
        assert client.domain == "custom_domain"
        assert client.iat_model_enum == SparkIatModel.ZH_CN_MANDARIN

    def test_client_attributes(self):
        """测试客户端属性"""
        client = SparkIatClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            iat_model_enum=SparkIatModel.ZH_CN_MANDARIN,
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'language')
        assert hasattr(client, 'domain')

    def test_success(self):
        """测试 成功请求"""
        client = SparkIatClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            iat_model_enum=SparkIatModel.ZH_CN_MANDARIN,
            dwa="wpgs"
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'spark_iat_cn_16k_10.pcm')
        # file_path = os.path.join(os.path.dirname(__file__), 'resources', 'spark_iat_mul_cn_16k_10.pcm')
        # file_path = os.path.join(os.path.dirname(__file__), 'resources', 'spark_iat_mul_lang_16k_10.pcm')
        f = open(file_path, 'rb')

        for chunk in client.stream(f):
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

