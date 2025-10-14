"""
AI PPT客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspark.ai_ppt import AIPPTClient, PPTSearch, PPTCreate


class TestAiPPT:
    """AI PPT客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')

    @patch('xfyunsdkspark.ai_ppt.AIPPTClient.post')
    def test_list(self, mock_send):
        """测试 list 方法"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.list(PPTSearch())
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.ai_ppt.AIPPTClient.post')
    def test_create(self, mock_send):
        """测试 list 方法"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'aipptv2.pdf')
        ppt_create = PPTCreate(
            query="根据提供的文件生成ppt",
            fileName="aipptv2.pdf",
            file=file_path
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.create(ppt_create)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.ai_ppt.AIPPTClient.post')
    def test_create_outline(self, mock_send):
        """测试 list 方法"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        create_outline = PPTCreate(
            query="生成一个介绍科大讯飞的大纲"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.create_outline(create_outline)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.ai_ppt.AIPPTClient.post')
    def test_create_outline_by_doc(self, mock_send):
        """测试 list 方法"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        file_path = os.path.join(os.path.dirname(__file__), '../example/resources', 'aipptv2.pdf')
        doc_param = PPTCreate(
            query="生成一个随机的大纲",
            fileName="aipptv2.pdf",
            file=file_path
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.create_outline_by_doc(doc_param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.ai_ppt.AIPPTClient.post')
    def test_create_ppt_by_outline(self, mock_send):
        """测试 list 方法"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        ppt_param = PPTCreate(
            query="生成一个介绍科大讯飞的ppt",
            outline={"title": "介绍科大讯飞"},
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.create_ppt_by_outline(ppt_param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.ai_ppt.AIPPTClient.get')
    def test_progress(self, mock_send):
        """测试 list 方法"""
        client = AIPPTClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        result = client.progress('123')
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
