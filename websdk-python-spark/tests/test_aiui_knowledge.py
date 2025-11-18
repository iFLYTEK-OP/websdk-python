"""
AIUI 个性化知识库客户端单元测试
"""
import pytest
import os
from unittest.mock import Mock, patch
from xfyunsdkspark.aiui_knowledge_client import AiUiKnowledgeClient
from xfyunsdkcore.model.aiui_knowledge_model import (
    AiUiCreate,
    AiUiUpload,
    AiUiDelete,
    AiUiLink,
    AiUiSearch,
    AiUiFileInfo
)


class TestAiUiKnowledge:
    """AI PPT客户端测试类"""

    def test_client_initialization(self):
        """测试客户端初始化"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password",
        )
        assert client.app_id == "test_app_id"
        assert client.api_secret == "test_api_password"

    def test_client_attributes(self):
        """测试客户端属性"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password",
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_secret')

    @patch('xfyunsdkspark.aiui_knowledge_client.AiUiKnowledgeClient.post')
    def test_create(self, mock_send):
        """测试 create 方法"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        param = AiUiCreate()
        try:
            client.create(param)
        except ValueError as e:
            assert str(e) == 'uid不能为空'

        param.uid = 1231213
        try:
            client.create(param)
        except ValueError as e:
            assert str(e) == '知识库名称不能为空'

        param.name = '测试知识库'
        result = client.create(param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.aiui_knowledge_client.AiUiKnowledgeClient.post')
    def test_upload(self, mock_send):
        """测试 upload 方法"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        param = AiUiUpload()
        try:
            client.upload(param)
        except ValueError as e:
            assert str(e) == 'uid不能为空'

        param.uid = 1231213
        try:
            client.upload(param)
        except ValueError as e:
            assert str(e) == 'groupId不能为空'

        param.groupId = '123'
        try:
            client.upload(param)
        except ValueError as e:
            assert str(e) == 'files和fileList不能同时为空'

        file_path1 = os.path.join(os.path.dirname(__file__), '../example/resources', 'aiuiknowledge.txt')
        file_url1 = "https://oss-beijing-m8.openstorage.cn/knowledge-origin-test/knowledge/file/123123213/7741/a838a943/20250910163419/aiuiknowledge.txt"
        fileInfo = AiUiFileInfo(
            fileName="aiuiknowledge.txt",
            filePath=file_url1,
            fileSize=43
        )
        param.fileList = [fileInfo]
        client.upload(param)

        param.files = [file_path1]
        client.upload(param)

    @patch('xfyunsdkspark.aiui_knowledge_client.AiUiKnowledgeClient.request')
    def test_delete(self, mock_send):
        """测试 create 方法"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        param = AiUiDelete()
        try:
            client.delete(param)
        except ValueError as e:
            assert str(e) == 'uid不能为空'

        param.uid = 1231213
        result = client.delete(param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.aiui_knowledge_client.AiUiKnowledgeClient.get')
    def test_list(self, mock_send):
        """测试 list 方法"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        param = AiUiSearch()
        try:
            client.list(param)
        except ValueError as e:
            assert str(e) == 'uid不能为空'

        param.uid = 1231213
        try:
            client.list(param)
        except ValueError as e:
            assert str(e) == 'sceneName不能为空'

        param.sceneName = 'sos_app'
        try:
            client.list(param)
        except ValueError as e:
            assert str(e) == 'appId不能为空'

        param.appId = '123'
        result = client.list(param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'

    @patch('xfyunsdkspark.aiui_knowledge_client.AiUiKnowledgeClient.post')
    def test_link(self, mock_send):
        """测试 link 方法"""
        client = AiUiKnowledgeClient(
            app_id="test_app_id",
            api_password="test_api_password"
        )

        # 模拟返回值
        mock_send.return_value.configure_mock(text='{"header": {"code": 0}}')
        # 调用 send 方法
        param = AiUiLink()
        try:
            client.link(param)
        except ValueError as e:
            assert str(e) == 'uid不能为空'

        param.uid = 1231213
        try:
            client.link(param)
        except ValueError as e:
            assert str(e) == 'sceneName不能为空'

        param.sceneName = 'sos_app'
        try:
            client.link(param)
        except ValueError as e:
            assert str(e) == 'appId不能为空'

        param.appId = '123'
        result = client.link(param)
        # 验证方法被调用
        mock_send.assert_called_once()
        assert result == '{"header": {"code": 0}}'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
