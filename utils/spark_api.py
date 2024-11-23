import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import ssl
import websocket
from urllib.parse import urlparse
import time
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

class SparkAPI:
    def __init__(self, app_id, api_key, api_secret):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.spark_url = "wss://spark-api.xf-yun.com/v3.1/chat"
        self.answer = ""
        
    def get_answer(self, question):
        """获取回答"""
        self.answer = ""
        ws_url = self._create_url()
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # 设置问题
        self.question = question
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return self.answer
        
    def _create_url(self):
        """生成鉴权url"""
        host = urlparse(self.spark_url).netloc
        path = urlparse(self.spark_url).path
        
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        # 拼接字符串
        signature_origin = "host: " + host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + path + " HTTP/1.1"
        
        # hmac-sha256加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(
            signature_sha
        ).decode(encoding='utf-8')
        
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha_base64}"'
        )
        
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')
        ).decode(encoding='utf-8')
        
        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        
        return self.spark_url + '?' + urlencode(v)
        
    def _on_message(self, ws, message):
        """收到消息的回调"""
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.answer += content
            if status == 2:
                ws.close()
                
    def _on_error(self, ws, error):
        """收到错误的回调"""
        print("错误:", error)
        
    def _on_close(self, ws, *args):
        """连接关闭的回调"""
        print("连接关闭")
        
    def _on_open(self, ws):
        """连接建立的回调"""
        thread.start_new_thread(self._run, (ws,))
        
    def _run(self, ws, *args):
        """发送请求"""
        data = {
            "header": {
                "app_id": self.app_id,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": "general",
                    "temperature": 0.5,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": self.question}
                    ]
                }
            }
        }
        ws.send(json.dumps(data)) 