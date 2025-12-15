# api/index.py - Vercel Serverless Function for DingTalk Bot
from http.server import BaseHTTPRequestHandler
import json
import time

class handler(BaseHTTPRequestHandler):
    # Vercel 要求必须使用 'do_' 方法，且不能定义 __init__
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({
                'status': 'ok',
                'service': 'dingtalk-bot-on-vercel'
            })
            self.wfile.write(response.encode())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/webhook':
            try:
                # 1. 读取请求数据
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                # 2. 处理命令
                content = data.get('text', {}).get('content', '').strip().lower()
                sender = data.get('senderStaffId', 'unknown')

                if content == 'help':
                    reply = "🤖 命令: help, ping, time, echo <消息>"
                elif content == 'ping':
                    reply = '🏓 Pong!'
                elif content == 'time':
                    reply = f'⏰ {time.strftime("%Y-%m-%d %H:%M:%S")}'
                elif content.startswith('echo '):
                    reply = f'📢 {content[5:]}'
                else:
                    reply = f'收到: {content}'

                # 3. 构建钉钉响应
                response = {
                    'msgtype': 'text',
                    'text': {'content': reply}
                }
                if sender != 'unknown':
                    response['at'] = {'atUserIds': [sender]}

                # 4. 发送响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_error(404)