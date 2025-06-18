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
