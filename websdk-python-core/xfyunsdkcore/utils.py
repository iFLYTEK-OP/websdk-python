import base64
import hashlib
import hmac
import json
import time
from typing import Any, Optional


class StringUtils:
    """String utility class"""

    @staticmethod
    def is_null_or_empty(value: Optional[str]) -> bool:
        """Check if a string is null or empty"""
        if value is None:
            return True
        return value == ""

    @staticmethod
    def unit_byte_array(byte1: bytes, byte2: bytes) -> bytes:
        """Concatenate two byte arrays"""
        return byte1 + byte2


class JsonUtils:
    """JSON utility class"""

    @staticmethod
    def to_json(obj: Any) -> str:
        """Convert object to JSON string"""
        return json.dumps(obj, separators=(',', ':'))

    @staticmethod
    def from_json(json_str: str, cls: type) -> Any:
        """Convert JSON string to object"""
        return json.loads(json_str)

    @classmethod
    def remove_none_values(cls, obj):
        """
        递归地移除对象中所有值为 None 的键值对。

        Args:
            obj: 可以是字典、列表、基本数据类型等。

        Returns:
            处理后的对象，其中所有层级的 None 值（作为字典的值）都已被移除。
        """
        if isinstance(obj, dict):
            # 如果是字典，递归处理其每个值，并过滤掉值为 None 的项
            return {
                k: cls.remove_none_values(v)
                for k, v in obj.items()
                if v is not None  # 这里过滤掉值为 None 的键
            }
        elif isinstance(obj, list):
            # 如果是列表，递归处理列表中的每个元素
            return [cls.remove_none_values(item) for item in obj]
        else:
            # 对于其他类型（str, int, float, bool, 或者已经是 None 但作为列表元素等情况），直接返回
            # 注意：这里不会移除列表中的 None 元素，只移除字典中 *作为值* 的 None。
            # 如果你也想移除列表中的 None 元素，可以在列表推导式里加 `if item is not None`
            return obj


class CryptTools:
    """Encryption and decryption tools"""

    HMAC_SHA1 = "HmacSHA1"
    HMAC_SHA256 = "HmacSHA256"

    @staticmethod
    def hmac_encrypt(encrypt_type: str, plain_text: str, encrypt_key: str) -> str:
        """
        HMAC encryption
        
        Args:
            encrypt_type: Encryption type
            plain_text: Plain text
            encrypt_key: Encryption key
            
        Returns:
            Encrypted string
        """
        try:
            data = encrypt_key.encode('utf-8')
            text = plain_text.encode('utf-8')

            if encrypt_type == CryptTools.HMAC_SHA1:
                mac = hmac.new(data, text, hashlib.sha1)
            elif encrypt_type == CryptTools.HMAC_SHA256:
                mac = hmac.new(data, text, hashlib.sha256)
            else:
                raise ValueError(f"Unsupported encryption type: {encrypt_type}")

            digest = mac.digest()
            return base64.b64encode(digest).decode('utf-8')
        except Exception as e:
            raise Exception(f"Signature exception: {str(e)}")

    @staticmethod
    def md5_encrypt(pstr: str) -> str:
        """
        MD5 encryption
        
        Args:
            pstr: String to encrypt
            
        Returns:
            Encrypted string
        """
        try:
            m = hashlib.md5()
            m.update(pstr.encode('utf-8'))
            return m.hexdigest()
        except Exception as e:
            raise Exception(f"MD5 encryption exception: {str(e)}")

    @staticmethod
    def base64_encode(plain_text: str) -> str:
        """
        BASE64 encoding
        
        Args:
            plain_text: Plain text
            
        Returns:
            Encoded string
        """
        return base64.b64encode(plain_text.encode('utf-8')).decode('utf-8')

    @staticmethod
    def get_current_time_millis() -> int:
        """
        Get current time in milliseconds
        
        Returns:
            Current time in milliseconds
        """
        return int(time.time() * 1000)
