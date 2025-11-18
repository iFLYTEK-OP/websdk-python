"""
视频合规客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.video_moderation_client import VideoModerationClient, Audio


class TestVideoModerationClient:
    """视频合规客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = VideoModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_custom_params(self):
        """测试自定义参数初始化"""
        client = VideoModerationClient(
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
        client = VideoModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
        assert hasattr(client, 'query_url')
    
    @patch('xfyunsdknlp.video_moderation_client.VideoModerationClient.post')
    def test_send_method_exists(self, mock_post):
        """测试 send 方法存在并可调用"""
        client = VideoModerationClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 创建测试视频列表
        video_list = [{"file_url": "https://test.com/video.mp4"}]
        
        # 调用 send 方法
        result = client.send(video_list)
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.video_moderation_client.VideoModerationClient.post')
    def test_query_method_exists(self, mock_post):
        """测试 query 方法存在并可调用"""
        client = VideoModerationClient(
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
        """测试 Audio 数据类（注意：这里是 Video 数据类但命名为 Audio）"""
        video = Audio(
            video_type="mp4",
            file_url="https://test.com/video.mp4",
            name="test_video"
        )
        assert video.video_type == "mp4"
        assert video.file_url == "https://test.com/video.mp4"
        assert video.name == "test_video"
        
        # 测试 to_dict 方法
        video_dict = video.to_dict()
        assert video_dict["video_type"] == "mp4"
        assert video_dict["file_url"] == "https://test.com/video.mp4"
        assert video_dict["name"] == "test_video"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

