"""
声音训练客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspark.voice_train import VoiceTrainClient, CreateTaskRequest, AudioAddRequest


class TestVoiceTrain:
    """声音训练客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')

    @patch('xfyunsdkspark.voice_train.VoiceTrainClient.post')
    def test_train_text(self, mock_send):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.train_text(text_id=5001, async_mode=False)
        # 验证方法被调用
        # mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.voice_train.VoiceTrainClient.post')
    def test_create_task(self, mock_send):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )

        create_request = CreateTaskRequest(
            taskName="task-03",
            sex=2,  # 1: 男声, 2: 女声
            ageGroup=2,  # 1: 儿童, 2: 青年, 3: 中年, 4: 老年
            language="cn",  # 中文
            resourceName="中文女发音人",
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.create_task(create_request)
        # 验证方法被调用
        # mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.voice_train.VoiceTrainClient.post')
    def test_audio_add(self, mock_send):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )

        audio_request = AudioAddRequest(
            taskId='123',
            textId=5001,
            textSegId=1,
            audioUrl="https开头,wav|mp3|m4a|pcm文件结尾的URL地址"
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.audio_add(audio_request)
        # 验证方法被调用
        # mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.voice_train.VoiceTrainClient.post')
    def test_submit(self, mock_send):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.submit('123')
        # 验证方法被调用
        # mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.voice_train.VoiceTrainClient.post')
    def test_submit_with_audio(self, mock_send):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'train.mp3')
        local_audio_request = AudioAddRequest(
            taskId='123',
            textId=5001,
            textSegId=1,
            files=file_path
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.submit_with_audio(local_audio_request)
        # 验证方法被调用
        # mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.voice_train.VoiceTrainClient.post')
    def test_result(self, mock_send):
        """测试客户端属性"""
        client = VoiceTrainClient(
            app_id="test_app_id",
            api_key="test_api_key",
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.result('123')
        # 验证方法被调用
        # mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

