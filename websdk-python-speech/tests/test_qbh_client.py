"""
哼唱识别客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspeech.qbh_client import QbhClient, QbhError


class TestQbhClient:
    """哼唱识别客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = QbhClient(
            app_id="test_app_id",
            secret_key="test_api_key",
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = QbhClient(
            app_id="test_app_id",
            secret_key="test_api_key",
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')

    def test_error(self):
        """测试客户端属性"""
        client = QbhClient(
            app_id="test_app_id",
            secret_key="test_api_key",
            timeout=120
        )
        try:
            client.send(None)
        except Exception as e:
            assert isinstance(e, QbhError)
        try:
            client.send(aue="lame")
        except Exception as e:
            assert isinstance(e, QbhError)
        try:
            client.send(audio_url="audio_url")
        except Exception as e:
            assert isinstance(e, QbhError)
        try:
            client.send(audio_url="audio_url")
        except Exception as e:
            assert isinstance(e, QbhError)

    @patch('xfyunsdkspeech.qbh_client.QbhClient.post')
    def test_success(self, mock_send):
        """测试 send 方法存在并可调用"""
        client = QbhClient(
            app_id="test_app_id",
            secret_key="test_api_key",
            timeout=120
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources/qbh', '一次就好16k.wav')

        result = client.send(file_path=file_path)

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

