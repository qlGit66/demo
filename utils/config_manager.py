import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_file = Path('data/config.json')
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def save_config(self, config):
        """保存配置"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    def get_login_info(self):
        """获取登录信息"""
        return self.config.get('login', {})
        
    def save_login_info(self, username, password):
        """保存登录信息"""
        self.config['login'] = {
            'username': username,
            'password': password
        }
        self.save_config(self.config)
        
    def get_all_config(self):
        """获取所有配置"""
        return {
            'login': self.config.get('login', {}),
            'token': self.config.get('token'),
            'ai_config': self.config.get('ai_config', {})
        }