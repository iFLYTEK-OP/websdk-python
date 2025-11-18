"""
词库客户端单元测试
"""
import pytest
from unittest.mock import Mock, patch
from xfyunsdknlp.wordlib_client import WordLibClient, WordLibEnum


class TestWordLibClient:
    """词库客户端测试类"""
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert client.app_id == "test_app_id"
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_client_attributes(self):
        """测试客户端属性"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        assert hasattr(client, 'app_id')
        assert hasattr(client, 'api_key')
        assert hasattr(client, 'api_secret')
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_create_lib_black(self, mock_post):
        """测试创建黑名单词库"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 create_lib 方法创建黑名单
        result = client.create_lib("测试词库", category="pornDetection", is_white=False)
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_create_lib_white(self, mock_post):
        """测试创建白名单词库"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 create_lib 方法创建白名单
        result = client.create_lib("测试词库", is_white=True)
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_create_lib_without_category_raises_error(self):
        """测试创建黑名单时不提供分类抛出错误"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 验证抛出 ValueError
        with pytest.raises(ValueError, match="请指定词库策略"):
            client.create_lib("测试词库", is_white=False)
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_add_word(self, mock_post):
        """测试添加词条"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 add_word 方法
        result = client.add_word("lib_id_123", ["词条1", "词条2"])
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_del_word(self, mock_post):
        """测试删除词条"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 del_word 方法
        result = client.del_word("lib_id_123", ["词条1", "词条2"])
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_detail(self, mock_post):
        """测试查询词条明细"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 detail 方法
        result = client.detail("lib_id_123", return_word=True)
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_list_lib(self, mock_post):
        """测试查询所有词库"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 list_lib 方法
        result = client.list_lib()
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    @patch('xfyunsdknlp.wordlib_client.WordLibClient.post')
    def test_delete_lib(self, mock_post):
        """测试删除词库"""
        client = WordLibClient(
            app_id="test_app_id",
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        # 模拟返回值
        mock_post.return_value.configure_mock(text='{"code": 0}')
        
        # 调用 delete_lib 方法
        result = client.delete_lib("lib_id_123")
        
        # 验证方法被调用
        mock_post.assert_called_once()
        assert result == '{"code": 0}'
    
    def test_wordlib_enum(self):
        """测试 WordLibEnum 枚举类型"""
        assert WordLibEnum.CREATE_BLACK.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/createBlack"
        assert WordLibEnum.CREATE_WHITE.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/createWhite"
        assert WordLibEnum.ADD_WORD.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/addWord"
        assert WordLibEnum.INFO.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/info"
        assert WordLibEnum.DEL_WORD.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/delWord"
        assert WordLibEnum.LIST.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/list"
        assert WordLibEnum.DEL_LIB.get_url() == "https://audit.iflyaisol.com/audit_res/v1/wordLib/delete"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

