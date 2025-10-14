"""
星火智能体客户端单元测试
"""
import pytest
import os, io
from typing import Iterator
from unittest.mock import Mock, patch
from xfyunsdkspark.agent_client import AgentClient, AgentChatParam, AgentEndpoint, AgentResumeParam, AgentClientError


class TestAgentClient:
    """星火智能体客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    def test_agent_endpoint_enum(self):
        """测试 AgentEndpoint 枚举"""
        assert AgentEndpoint.COMPLETIONS.description == "执行工作流"
        assert AgentEndpoint.RESUME.description == "恢复运行工作流"
        assert AgentEndpoint.UPLOAD_FILE.description == "文件上传"
        assert "xingchen-api" in AgentEndpoint.COMPLETIONS.url
        assert AgentEndpoint.COMPLETIONS.method == "POST"

    def test_agent_chat_param_creation(self):
        """测试 AgentChatParam 创建"""
        param = AgentChatParam(
            flow_id="test_flow",
            parameters={"key": "value"}
        )
        assert param.flow_id == "test_flow"
        assert param.parameters == {"key": "value"}

    @patch('xfyunsdkspark.agent_client.AgentClient.sse_post')
    def test_completions_sse(self, mock_send):

        param = AgentChatParam(
            flow_id="7351431612989308928",
            parameters={"AGENT_USER_INPUT": "今天天气怎么样"},
            stream=True
        )
        """测试 completions 方法"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟 a_subscribe 返回的异步生成器
        def async_generator() -> Iterator[str]:
            yield {"data": "transcript1"}
            yield {"data": "transcript2"}
            yield {"other": "ignored"}

        # 模拟返回值
        mock_send.return_value = async_generator()
        # 调用 send 方法
        for chunk in client.completion(param):
            pass
        # 验证方法被调用
        mock_send.assert_called_once()

    @patch('xfyunsdkspark.agent_client.AgentClient.post')
    def test_completions(self, mock_send):
        """测试 completions 方法"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        param = AgentChatParam(
            flow_id="7351431612989308928",
            parameters = {"AGENT_USER_INPUT": "今天天气怎么样"},
            stream=False
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.completion(param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.agent_client.AgentClient.sse_post')
    def test_resume(self, mock_send):
        """测试 completions 方法"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        resume_param = AgentResumeParam(
            event_id="工作流ID",
            event_type="事件类型",
            content="回复内容",
        )

        # 模拟 a_subscribe 返回的异步生成器
        def async_generator() -> Iterator[str]:
            yield {"data": "transcript1"}
            yield {"data": "transcript2"}
            yield {"other": "ignored"}

        # 模拟返回值
        mock_send.return_value = async_generator()
        # 调用 send 方法
        for chunk in client.resume(resume_param):
            pass
        # 验证方法被调用
        mock_send.assert_called_once()

    @patch('xfyunsdkspark.agent_client.AgentClient.post')
    def test_upload(self, mock_send):
        """测试 completions 方法"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'ocr.jpg')
        result = client.upload(file_path)

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.agent_client.AgentClient.post')
    def test_error(self, mock_send):
        """测试 completions 方法"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'ocr.jpg')
        result = client.upload(file_path)

        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.agent_client.AgentClient.post')
    def test_error_upload(self, mock_send):
        """测试 completions 方法"""
        client = AgentClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'ocr1.jpg')

        try:
            client._prepare_file_for_upload(file_path,  'ocr1.jpg')
        except Exception as e:
            assert isinstance(e, FileNotFoundError)

        try:
            client._prepare_file_for_upload(b'1212321321', None)
        except Exception as e:
            assert isinstance(e, ValueError)

        client._prepare_file_for_upload(b'1212321321', '123.jpg')

        try:
            client._prepare_file_for_upload(None, None)
        except Exception as e:
            assert isinstance(e, ValueError)

        file_obj = io.BytesIO(b"streamed data")
        try:
            client._prepare_file_for_upload(file_obj, None)
        except Exception as e:
            assert isinstance(e, ValueError)

        client._prepare_file_for_upload(file_obj, '123.jpg')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
