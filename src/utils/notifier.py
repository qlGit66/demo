from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from plyer import notification
import requests
import json
from datetime import datetime

class Notifier:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.notification_history = []
        
    def notify(self, title, message, level="info", methods=None):
        """统一的通知接口"""
        if methods is None:
            methods = ["desktop", "email"] if level == "error" else ["desktop"]
            
        notification_record = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "level": level,
            "methods": []
        }
        
        for method in methods:
            try:
                if method == "desktop" and self.config.notification['desktop']:
                    self.send_desktop(title, message)
                    notification_record["methods"].append("desktop")
                elif method == "email" and self.config.notification['email']:
                    self.send_email(title, message)
                    notification_record["methods"].append("email")
                elif method == "telegram" and self.config.notification['telegram']:
                    self.send_telegram(title, message)
                    notification_record["methods"].append("telegram")
            except Exception as e:
                self.logger.error(f"发送{method}通知失败: {str(e)}")
                
        self.notification_history.append(notification_record)
        self._save_notification_history()
        
    def send_desktop(self, title, message):
        """发送桌面通知"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,
                timeout=10
            )
        except Exception as e:
            raise Exception(f"发送桌面通知失败: {str(e)}")
            
    def send_email(self, subject, content):
        """发送邮件通知"""
        if not self.config.email['enabled']:
            return
            
        try:
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = self.config.email['sender']
            msg['To'] = ', '.join(self.config.email['receivers'])
            
            msg.attach(MIMEText(content, 'plain'))
            
            with smtplib.SMTP(self.config.email['smtp_server'], self.config.email['port']) as server:
                server.starttls()
                server.login(
                    self.config.email['username'],
                    self.config.email['password']
                )
                server.send_message(msg)
        except Exception as e:
            raise Exception(f"发送邮件失败: {str(e)}")
            
    def send_telegram(self, title, message):
        """发送Telegram通知"""
        if not hasattr(self.config, 'telegram') or not self.config.telegram['enabled']:
            return
            
        try:
            bot_token = self.config.telegram['bot_token']
            chat_id = self.config.telegram['chat_id']
            text = f"*{title}*\n{message}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"发送Telegram通知失败: {str(e)}")
            
    def _save_notification_history(self):
        """保存通知历史"""
        try:
            with open('data/notification_history.json', 'w', encoding='utf-8') as f:
                json.dump(self.notification_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存通知历史失败: {str(e)}")