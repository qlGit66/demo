import random
import time
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
import json
import os
from datetime import datetime, timedelta
import requests

class AntiDetection:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.user_agent = UserAgent()
        self.proxy_list = self._load_proxies()
        self.current_proxy = None
        self.last_action_time = datetime.now()
        self.action_patterns = self._load_action_patterns()
        
    def setup_browser(self) -> webdriver.Chrome:
        """配置反检测的浏览器"""
        options = Options()
        
        # 基础反检测设置
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 随机User-Agent
        options.add_argument(f'user-agent={self.user_agent.random}')
        
        # 添加代理（如果启用）
        if self.config.proxy['enabled']:
            self.current_proxy = self._get_best_proxy()
            if self.current_proxy:
                options.add_argument(f'--proxy-server={self.current_proxy}')
        
        # 添加随机分辨率
        resolution = self._get_random_resolution()
        options.add_argument(f'--window-size={resolution["width"]},{resolution["height"]}')
        
        # 创建浏览器实例
        driver = webdriver.Chrome(options=options)
        
        # 注入反检测JavaScript
        self._inject_anti_detection_js(driver)
        
        return driver
    
    def _inject_anti_detection_js(self, driver):
        """注入反检测的JavaScript代码"""
        js_script = """
        // 覆盖WebDriver属性
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 添加随机的插件数据
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                }
            ]
        });
        
        // 模拟正常的性能数据
        window.performance = {
            memory: {
                jsHeapSizeLimit: 2172649472,
                totalJSHeapSize: 2172649472,
                usedJSHeapSize: 2172649472
            }
        };
        """
        try:
            driver.execute_script(js_script)
        except Exception as e:
            self.logger.error(f"注入反检测JS失败: {str(e)}")
    
    def simulate_human_behavior(self, driver, element=None):
        """模拟人类行为"""
        try:
            # 确保操作间隔合理
            self._ensure_natural_interval()
            
            # 随机鼠标移动
            self._random_mouse_movement(driver)
            
            if element:
                # 模拟真实点击
                self._natural_click(driver, element)
            
            # 随机滚动
            self._random_scroll(driver)
            
            # 更新最后操作时间
            self.last_action_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"模拟人类行为失败: {str(e)}")
    
    def _ensure_natural_interval(self):
        """确保操作间隔符合人类习惯"""
        elapsed = (datetime.now() - self.last_action_time).total_seconds()
        if elapsed < 1:  # 如果间隔太短
            sleep_time = random.uniform(1, 3)
            time.sleep(sleep_time)
    
    def _random_mouse_movement(self, driver):
        """随机鼠标移动"""
        try:
            actions = ActionChains(driver)
            
            # 生成随机的中间点
            points = self._generate_natural_points(
                start=(0, 0),
                end=(random.randint(100, 700), random.randint(100, 500)),
                points_count=random.randint(3, 7)
            )
            
            # 执行移动
            for point in points:
                actions.move_by_offset(point[0], point[1])
                sleep_time = random.uniform(0.1, 0.3)
                time.sleep(sleep_time)
            
            actions.perform()
            
        except Exception as e:
            self.logger.error(f"随机鼠标移动失败: {str(e)}")
    
    def _natural_click(self, driver, element):
        """模拟自然点击"""
        try:
            # 获取元素位置
            location = element.location
            size = element.size
            
            # 计算点击位置（略微偏离中心）
            offset_x = random.randint(-size['width']//4, size['width']//4)
            offset_y = random.randint(-size['height']//4, size['height']//4)
            
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            
            # 随机的短暂停顿
            time.sleep(random.uniform(0.1, 0.3))
            
            actions.click()
            actions.perform()
            
        except Exception as e:
            self.logger.error(f"自然点击失败: {str(e)}")
    
    def _random_scroll(self, driver):
        """随机滚动页面"""
        try:
            # 获取页面高度
            page_height = driver.execute_script("return document.body.scrollHeight")
            
            # 生成随机滚动距离
            scroll_distance = random.randint(100, min(500, page_height))
            
            # 平滑滚动
            current_scroll = 0
            while current_scroll < scroll_distance:
                step = random.randint(20, 50)
                driver.execute_script(f"window.scrollBy(0, {step})")
                current_scroll += step
                time.sleep(random.uniform(0.1, 0.2))
                
        except Exception as e:
            self.logger.error(f"随机滚动失败: {str(e)}")
    
    def _generate_natural_points(self, start, end, points_count):
        """生成自然的鼠标移动路径点"""
        points = []
        for i in range(points_count):
            t = i / (points_count - 1)
            # 使用贝塞尔曲线生成更自然的路径
            x = start[0] + (end[0] - start[0]) * t + random.randint(-20, 20)
            y = start[1] + (end[1] - start[1]) * t + random.randint(-20, 20)
            points.append((x, y))
        return points
    
    def _load_proxies(self) -> List[str]:
        """加载代理列表"""
        proxy_file = 'data/proxies.json'
        try:
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"加载代理列表失败: {str(e)}")
            return []
    
    def _get_best_proxy(self) -> Optional[str]:
        """获取最佳代理"""
        if not self.proxy_list:
            return None
            
        working_proxies = []
        for proxy in self.proxy_list:
            if self._test_proxy(proxy):
                working_proxies.append(proxy)
                
        return random.choice(working_proxies) if working_proxies else None
    
    def _test_proxy(self, proxy: str) -> bool:
        """测试代理是否可用"""
        try:
            response = requests.get(
                'https://www.baidu.com',
                proxies={'http': proxy, 'https': proxy},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def _get_random_resolution(self) -> Dict:
        """获取随机的屏幕分辨率"""
        resolutions = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
            {"width": 1280, "height": 720}
        ]
        return random.choice(resolutions)
    
    def _load_action_patterns(self) -> Dict:
        """加载行为模式"""
        return {
            "typing_speed": {
                "min": 100,  # 最小字符间隔（毫秒）
                "max": 300   # 最大字符间隔（毫秒）
            },
            "mouse_speed": {
                "min": 500,  # 最小移动速度（像素/秒）
                "max": 1500  # 最大移动速度（像素/秒）
            },
            "scroll_patterns": [
                {"distance": 100, "speed": "slow"},
                {"distance": 300, "speed": "medium"},
                {"distance": 500, "speed": "fast"}
            ]
        } 