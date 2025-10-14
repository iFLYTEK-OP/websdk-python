"""
Iat Client Usage Example
"""
import os
import base64
import json
from xfyunsdkspark.spark_iat_client import SparkIatClient, SparkIatModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        'Python environment is not completely set up: required package "python-dotenv" is missing.') from None

load_dotenv()


def stream():
    """非流式生成音频示例"""
    try:
        # 初始化客户端
        client = SparkIatClient(
            app_id=os.getenv('APP_ID'),  # 替换为你的应用ID
            api_key=os.getenv('API_KEY'),  # 替换为你的API密钥
            api_secret=os.getenv('API_SECRET'),  # 替换为你的API密钥
            iat_model_enum=SparkIatModel.ZH_CN_MANDARIN,
            dwa="wpgs"
        )
        file_path = os.path.join(os.path.dirname(__file__), 'resources', 'spark_iat_cn_16k_10.pcm')
        # file_path = os.path.join(os.path.dirname(__file__), 'resources', 'spark_iat_mul_cn_16k_10.pcm')
        # file_path = os.path.join(os.path.dirname(__file__), 'resources', 'spark_iat_mul_lang_16k_10.pcm')
        f = open(file_path, 'rb')

        content_map = {}
        final_result = ''
        for chunk in client.stream(f):
            text_chunk = base64.b64decode(chunk["result"]["text"]).decode("utf-8")
            json_parse_text = json.loads(text_chunk)
            req_result = get_ws_content(json_parse_text)
            if json_parse_text['pgs'] == 'apd':
                content_map[len(content_map)] = req_result
                # logger.info(f"中间识别结果 【{req_result}】 拼接后结果==> {get_last_result(content_map)}")
                logger.info(f"拼接后结果==> {get_last_result(content_map)}")
            elif json_parse_text['pgs'] == 'rpl':
                rg = json_parse_text['rg']
                start_index = rg[0]
                end_index = rg[1]
                for i in range(start_index, end_index + 1):
                    content_map.pop(i, None)
                content_map[len(content_map)] = req_result
                # logger.info(f"中间识别结果 【{req_result}】 替换后结果==> {get_last_result(content_map)}")
                logger.info(f"替换后结果==> {get_last_result(content_map)}")
            # logger.info(f"返回结果: {text_chunk}")

    except Exception as e:
        logger.error(f"生成音频失败: {str(e)}")
        raise


def get_last_result(content_map):
    result = ''.join(content_map.values())
    return result


def get_ws_content(json_parse_text):
    req_result = ''
    ws_list = json_parse_text.get('ws', [])
    for ws in ws_list:
        cw_list = ws.get('cw', [])
        for cw in cw_list:
            req_result += cw.get('w', '')
    return req_result


if __name__ == "__main__":
    # 可以选择运行非流式或流式生成
    stream()  # 流式生成
