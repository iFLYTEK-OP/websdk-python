"""
Signature utility for WebSDK
"""
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from time import mktime
import time
import uuid
from urllib.parse import urlencode, urlparse, urlunparse, quote
from wsgiref.handlers import format_date_time
from typing import Dict, Union, Any
from .log.logger import logger
from .errors import SignatureError


class VoiceCloneSignature:
    """Utility class for generating signatures"""

    @staticmethod
    def token_sign(api_key: str, timestamp: str, body: str) -> Dict[str, str]:
        """
        Generate signature for token request
        
        Args:
            api_key: The API key
            timestamp: The timestamp
            body: The request body
            
        Returns:
            Dictionary containing the signature headers
        """
        keySign = hashlib.md5((api_key + timestamp).encode('utf-8')).hexdigest()
        signature = hashlib.md5((keySign + body).encode("utf-8")).hexdigest()

        return {
            'Authorization': signature,
            'Content-Type': "application/json"
        }

    @staticmethod
    def common_sign(app_id: str, api_key: str, body: str, token: str) -> Dict[str, str]:
        """
        Generate signature for common requests
        
        Args:
            app_id: The application ID
            api_key: The API key
            body: The request body
            token: The authentication token
            
        Returns:
            Dictionary containing the signature headers
        """
        timestamp = str(int(time.time() * 1000))
        keySign = hashlib.md5(body.encode('utf-8')).hexdigest()
        signature = hashlib.md5((api_key + timestamp + keySign).encode("utf-8")).hexdigest()

        return {
            'X-Sign': signature,
            'X-Token': token,
            'X-AppId': app_id,
            'X-Time': timestamp
        }


class RtasrSignature:
    """Utility class for generating signatures"""

    @staticmethod
    def create_signed_url(api_url: str, app_id: str, api_key: str) -> str:
        ts = str(int(time.time()))
        tt = (app_id + ts).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')

        apiKey = api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return api_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa)


class Signature:
    """Utility class for generating WebSocket authentication signatures"""

    @staticmethod
    def create_signed_url(api_url: str, api_key: str, api_secret: str, method: str = "GET") -> str:
        """Generate a signed URL for API authentication

        Returns:
            str: Signed URL with authentication parameters

        Raises:
            SignatureError: If URL signing fails
        """
        try:
            # 设置url
            parsed_url = urlparse(api_url)
            host = parsed_url.netloc
            path = parsed_url.path
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))
            signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
            signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                     digestmod=hashlib.sha256).digest()
            signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
            authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                api_key, "hmac-sha256", "host date request-line", signature_sha)
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
            values = {
                "authorization": authorization,
                "host": host,
                "date": date
            }
            return api_url + "?" + urlencode(values)
        except Exception as e:
            logger.error(f"Failed to create signed URL: {str(e)}")
            raise SignatureError(f"Failed to create signed URL: {str(e)}")

    @staticmethod
    def get_signature(app_id: str, timestamp: str, api_secret: str) -> str:
        try:
            # 对app_id和时间戳进行MD5加密
            text = app_id + timestamp
            auth = hashlib.md5(text.encode('utf-8')).hexdigest()
            # 使用HMAC-SHA1算法对加密后的字符串进行加密，并将结果转换为Base64编码
            return base64.b64encode(
                hmac.new(api_secret.encode('utf-8'), auth.encode('utf-8'), hashlib.sha1).digest()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to create signed: {str(e)}")
            raise SignatureError(f"Failed to create signed: {str(e)}")

    @staticmethod
    def get_signature_header(app_id: str, api_key: str, param: str) -> Dict:
        try:
            cur_time = str(int(time.time()))
            # 使用audio_url传输音频数据时，http request body须为空。
            # 直接把音频二进制数据写入到Http Request Body时，不需要设置audio_url参数
            base64_param = base64.urlsafe_b64encode(param.encode('utf-8'))
            tt = str(base64_param, 'utf-8')
            m2 = hashlib.md5()
            m2.update((api_key + cur_time + tt).encode('utf-8'))
            checksum = m2.hexdigest()

            header = {
                "X-CurTime": cur_time,
                "X-Param": tt,
                "X-Appid": app_id,
                "X-CheckSum": checksum,
            }
            return header
        except Exception as e:
            logger.error(f"Failed to create signed header: {str(e)}")
            raise SignatureError(f"Failed to create signed header: {str(e)}")

    @staticmethod
    def get_digest_header(api_url: str, api_key: str, api_secret: str, body: str, method: str = "POST") -> Dict:
        try:
            # 设置当前时间
            date = format_date_time(mktime(datetime.now().timetuple()))
            encrypt_method = "hmac-sha256"

            m = hashlib.sha256(body.encode("utf-8")).digest()
            digest = "SHA-256=" + base64.b64encode(m).decode("utf-8")

            # 设置url
            parsed_url = urlparse(api_url)
            host = parsed_url.netloc
            path = parsed_url.path

            signature_origin = f"host: {host}\ndate: {date}\n{method} {path} HTTP/1.1\ndigest: {digest}"
            signature_sha = hmac.new(
                api_secret.encode("utf-8"),
                signature_origin.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
            sign = base64.b64encode(signature_sha).decode("utf-8")

            authorization_origin = f'api_key="{api_key}", algorithm="{encrypt_method}", headers="host date request-line digest", signature="{sign}"'
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Method": "POST",
                "Host": host,
                "Date": date,
                "Digest": digest,
                "Authorization": authorization_origin
            }
            return headers
        except Exception as e:
            logger.error(f"Failed to create signed header: {str(e)}")
            raise SignatureError(f"Failed to create signed header: {str(e)}")

    @staticmethod
    def get_auth(app_id: str, api_key: str, api_secret: str, mode_type: str = None) -> Dict:
        try:
            # 1. 获取时间
            utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')

            # 2. 控制台关键信息
            url_params = {
                "appId": app_id,
                "accessKeyId": api_key,
                "accessKeySecret": api_secret,
                "utc": utc_time,
                "uuid": str(uuid.uuid4())[:32]  # uuid有防重放的功能，如果调试，请注意更换uuid的值
            }
            if mode_type:
                url_params["modeType"] = mode_type
            params_list = sorted(url_params.items(), key=lambda e: e[0], reverse=False)
            # 还原字典
            params_str_dict = dict(params_list)
            base_string = urlencode(params_str_dict)

            # 计算 HMAC-SHA1 签名
            mac = hmac.new(api_secret.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha1)
            # 得到签名 byte[]
            sign_bytes = mac.digest()
            # 将 byte[] base64 编码
            signature = base64.b64encode(sign_bytes).decode('utf-8')

            url_params["signature"] = signature
            return url_params
        except Exception as e:
            logger.error(f"Failed to create signed header: {str(e)}")
            raise SignatureError(f"Failed to create signed header: {str(e)}")
