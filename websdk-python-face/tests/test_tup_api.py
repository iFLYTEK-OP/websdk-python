"""
人脸特征分析客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch, mock_open
from xfyunsdkface.tup_api_client import TupApiClient, TupEnum


class TestTupEnum:
    """TupEnum 枚举测试类"""
    
    def test_enum_values(self):
        """测试枚举值"""
        assert TupEnum.AGE.get_func() == "age"
        assert TupEnum.SEX.get_func() == "sex"
        assert TupEnum.EXPRESSION.get_func() == "expression"
        assert TupEnum.FACE_SCORE.get_func() == "face_score"
    
    def test_enum_descriptions(self):
        """测试枚举描述"""
        assert TupEnum.AGE.get_desc() == "年龄分析"
        assert TupEnum.SEX.get_desc() == "性别分析"
        assert TupEnum.EXPRESSION.get_desc() == "表情分析"
        assert TupEnum.FACE_SCORE.get_desc() == "颜值分析"


class TestTupApiClient:
    """人脸特征分析客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = TupApiClient(
            app_id="test_app_id",
            api_key="test_api_key",
            tup_type=TupEnum.AGE,
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.tup_type == TupEnum.AGE
    
    def test_client_initialization_with_different_types(self):
        """测试使用不同类型初始化客户端"""
        for tup_type in [TupEnum.AGE, TupEnum.SEX, TupEnum.EXPRESSION, TupEnum.FACE_SCORE]:
            client = TupApiClient(
                app_id="test_app_id",
                api_key="test_api_key",
                tup_type=tup_type,
                api_secret="test_api_secret"
            )
            assert client.tup_type == tup_type
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = TupApiClient(
            app_id="test_app_id",
            api_key="test_api_key",
            tup_type=TupEnum.AGE,
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'tup_type')

    @patch('xfyunsdkface.tup_api_client.TupApiClient.post')
    def test_send_method_exists(self, mock_send):
        """测试 send 方法存在并可调用"""
        client = TupApiClient(
            app_id="test_app_id",
            api_key="test_api_key",
            tup_type=TupEnum.AGE,
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        result = client.send("base64_image", None, "http://mock.com")

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

