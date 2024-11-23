import requests
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import asyncio
from dataclasses import dataclass

@dataclass
class ProxyInfo:
    ip: str
    port: int
    protocol: str
    country: str
    anonymity: str
    response_time: float
    last_checked: datetime
    fail_count: int = 0
    success_count: int = 0

class ProxyManager:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.proxies: Dict[str, ProxyInfo] = {}
        self.proxy_apis = {
            'luminati': 'http://api.luminati.io/v1/proxy',
            'proxyscrape': 'https://api.proxyscrape.com/v2/',
            'proxyrotator': 'https://api.proxyrotator.com/'
        }
        self.last_rotation = datetime.now()
        self.rotation_interval = timedelta(minutes=config.proxy.get('rotation_interval', 10))
        
    async def initialize(self):
        """初始化代理池"""
        await self._fetch_proxies_from_all_sources()
        await self._verify_proxies()
        
    async def _fetch_proxies_from_all_sources(self):
        """从多个来源获取代理"""
        tasks = []
        for source, url in self.proxy_apis.items():
            tasks.append(self._fetch_proxies(source, url))
        await asyncio.gather(*tasks)
        
    async def _fetch_proxies(self, source: str, url: str):
        """从单个来源获取代理"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        self._process_proxy_data(source, data)
        except Exception as e:
            self.logger.error(f"从{source}获取代理失败: {str(e)}")
            
    async def _verify_proxies(self):
        """验证所有代理的可用性"""
        tasks = []
        for proxy_id, proxy in self.proxies.items():
            tasks.append(self._verify_single_proxy(proxy_id, proxy))
        await asyncio.gather(*tasks)
        
    async def _verify_single_proxy(self, proxy_id: str, proxy: ProxyInfo):
        """验证单个代理的可用性"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    'https://api.ipify.org?format=json',
                    proxy=f"{proxy.protocol}://{proxy.ip}:{proxy.port}",
                    timeout=10
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['ip'] != proxy.ip:
                            proxy.anonymity = 'high'
                        proxy.response_time = time.time() - start_time
                        proxy.success_count += 1
                        proxy.last_checked = datetime.now()
                    else:
                        proxy.fail_count += 1
        except Exception:
            proxy.fail_count += 1
            
    def get_best_proxy(self) -> Optional[ProxyInfo]:
        """获取最佳代理"""
        valid_proxies = [p for p in self.proxies.values() 
                        if p.fail_count < 3 and 
                        p.response_time < 2.0 and 
                        p.anonymity == 'high']
        
        if not valid_proxies:
            return None
            
        # 根据响应时间和成功率排序
        sorted_proxies = sorted(
            valid_proxies,
            key=lambda x: (x.response_time, -x.success_count)
        )
        
        return random.choice(sorted_proxies[:5])  # 从最好的5个中随机选择
        
    def should_rotate(self) -> bool:
        """检查是否需要轮换IP"""
        return datetime.now() - self.last_rotation > self.rotation_interval
        
    def rotate_proxy(self) -> Optional[ProxyInfo]:
        """轮换到新的代理"""
        new_proxy = self.get_best_proxy()
        if new_proxy:
            self.last_rotation = datetime.now()
        return new_proxy 