"""
转写客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspeech.lfasr_client import LFasrClient, LFasrError
from xfyunsdkcore.model.lfasr_model import UploadParam

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


class TestLfasrClient:
    """转写客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = LFasrClient(
            app_id="test_app_id",
            secret_key="test_secret_key"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_secret_key"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = LFasrClient(
            app_id="test_app_id",
            secret_key="test_secret_key"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')

    def test_error(self):
        """测试客户端属性"""
        client = LFasrClient(
            app_id="test_app_id",
            secret_key="test_secret_key"
        )
        try:
            client.get_result(None)
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.get_result({})
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.upload(None, '')
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.upload({}, '')
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.upload({"fileName": '123', "fileSize": 1280}, '')
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.upload({"fileName": '123', "fileSize": 1280, "audioMode": '111'}, '')
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.upload({"fileName": '123', "fileSize": 1280, "audioMode": 'fileStream'}, None)
        except Exception as e:
            assert isinstance(e, LFasrError)
        try:
            client.upload({"fileName": '123', "fileSize": 1280, "audioMode": 'urlLink'}, None)
        except Exception as e:
            assert isinstance(e, LFasrError)

    @patch('xfyunsdkspeech.lfasr_client.LFasrClient.post')
    def test_upload(self, mock_send):
        """测试 send 方法存在并可调用"""
        client = LFasrClient(
            app_id="test_app_id",
            secret_key="test_secret_key"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources/lfasr', 'lfasr_涉政.wav')
        param = UploadParam(
            audioMode="fileStream",
            fileName="lfasr_涉政.wav",
            fileSize=os.path.getsize(file_path),
        )
        result = client.upload(param.to_dict(), file_path)

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspeech.lfasr_client.LFasrClient.post')
    def test_get_result(self, mock_send):
        """测试 send 方法存在并可调用"""
        client = LFasrClient(
            app_id="test_app_id",
            secret_key="test_secret_key"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        # 调用 send 方法
        param = {"orderId": '123'}
        result = client.get_result(param)

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
