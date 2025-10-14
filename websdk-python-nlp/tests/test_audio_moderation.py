"""
音频合规客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.audio_moderation_client import AudioModerationClient, Audio


class TestAudioModerationClient:
    """音频合规客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = AudioModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = AudioModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret",
            host_url="https://custom.url",
            query_url="https://custom.query.url",
            notify_url="https://notify.url",
            timeout=60
        )
        assert client.host_url == "https://custom.url"
        assert client.query_url == "https://custom.query.url"
        assert client.notify_url == "https://notify.url"
        assert client.timeout == 60
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = AudioModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'query_url')
    
    @patch('xfyunsdknlp.audio_moderation_client.AudioModerationClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = AudioModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 创建测试音频列表
        audio_list = [{"file_url": "https://test.com/audio.mp3"}]
        
        # 调用 send 方法
        result = client.send(audio_list)
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.audio_moderation_client.AudioModerationClient.post')
    def test_query_method_exists(self, mock_post):
        """测试 query 方法存在并可调用"""
        client = AudioModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 query 方法
        result = client.query("test_request_id")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_audio_dataclass(self):
        """测试 Audio 数据类"""
        audio = Audio(
            audio_type="mp3",
            file_url="https://test.com/audio.mp3",
            name="test_audio"
        )
        assert audio.audio_type == "mp3"
        assert audio.file_url == "https://test.com/audio.mp3"
        assert audio.name == "test_audio"
        
        # 测试 to_dict 方法
        audio_dict = audio.to_dict()
        assert audio_dict["audio_type"] == "mp3"
        assert audio_dict["file_url"] == "https://test.com/audio.mp3"
        assert audio_dict["name"] == "test_audio"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

