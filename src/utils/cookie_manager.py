import browser_cookie3
import json
import time
from typing import Dict, List
import random
from datetime import datetime, timedelta

class CookieManager:
    def __init__(self, logger):
        self.logger = logger
        self.cookies = self._load_cookies()
        self.cookie_jar = {}
        self.rotation_patterns = self._generate_rotation_patterns()
        
    def _load_cookies(self) -> Dict:
        """加载已保存的Cookie"""
        try:
            with open('data/cookies.json', 'r') as f:
                return json.load(f)
        except:
            return {}
            
    def _generate_rotation_patterns(self) -> Dict:
        """生成Cookie轮换模式"""
        return {
            'regular': {
                'interval': timedelta(minutes=30),
                'strategy': 'sequential'
            },
            'random': {
                'interval': timedelta(minutes=random.randint(15, 45)),
                'strategy': 'random'
            },
            'smart': {
                'interval': timedelta(minutes=20),
                'strategy': 'weighted'
            }
        }
        
    def extract_browser_cookies(self, domain: str) -> List[Dict]:
        """从浏览器提取Cookie"""
        cookies = []
        try:
            chrome_cookies = browser_cookie3.chrome(domain_name=domain)
            for cookie in chrome_cookies:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure
                })
        except Exception as e:
            self.logger.error(f"提取浏览器Cookie失败: {str(e)}")
        return cookies
        
    def generate_cookie_variations(self, base_cookies: List[Dict]) -> List[Dict]:
        """生成Cookie变体"""
        variations = []
        for cookie in base_cookies:
            # 创建多个相似但不完全相同的Cookie
            for _ in range(3):
                variation = cookie.copy()
                variation['value'] = self._mutate_cookie_value(cookie['value'])
                variations.append(variation)
        return variations
        
    def _mutate_cookie_value(self, value: str) -> str:
        """轻微改变Cookie值"""
        if len(value) < 5:
            return value
            
        # 保持大部分值不变，只修改一小部分
        mutation_point = random.randint(0, len(value) - 1)
        mutation_length = random.randint(1, 3)
        
        prefix = value[:mutation_point]
        suffix = value[mutation_point + mutation_length:]
        mutation = ''.join(random.choices('0123456789abcdef', k=mutation_length))
        
        return prefix + mutation + suffix 