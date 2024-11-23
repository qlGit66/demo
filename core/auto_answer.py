from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service
import logging
import os

class ChaoXingAutoAnswer:
    def __init__(self, browser_type='chrome', chaoxing_token=None, app_id=None, api_key=None, api_secret=None):
        try:
            # 根据浏览器类型初始化
            if browser_type.lower() == 'chrome':
                self.init_chrome()
            elif browser_type.lower() == 'edge':
                self.init_edge()
            elif browser_type.lower() == 'qqbrowser':
                self.init_qqbrowser()
            else:
                raise ValueError(f"不支持的浏览器类型: {browser_type}")
                
        except Exception as e:
            logging.error(f"初始化浏览器失败: {str(e)}")
            self.driver = None
            
        self.answer_bank = self._load_answer_bank()
        self.chaoxing_token = chaoxing_token
        self.token_usage = {
            'remaining': None,
            'warning_threshold': 50,
            'last_check': None
        }
        
    def init_chrome(self):
        """初始化Chrome浏览器"""
        try:
            options = ChromeOptions()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=options)
            logging.info("成功连接到Chrome浏览器")
        except:
            logging.info("未找到已打开的Chrome浏览器")
            self.show_browser_guide('chrome')
            
    def init_edge(self):
        """初始化Edge浏览器"""
        try:
            options = EdgeOptions()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Edge(options=options)
            logging.info("成功连接到Edge浏览器")
        except:
            logging.info("未找到已打开的Edge浏览器")
            self.show_browser_guide('edge')
            
    def init_qqbrowser(self):
        """初始化QQ浏览器"""
        try:
            options = ChromeOptions()  # QQ浏览器基于Chromium
            options.binary_location = r"C:\Program Files\Tencent\QQBrowser\QQBrowser.exe"  # QQ浏览器路径
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(options=options)
            logging.info("成功连接到QQ浏览器")
        except:
            logging.info("未找到已打开的QQ浏览器")
            self.show_browser_guide('qqbrowser')
            
    def show_browser_guide(self, browser_type):
        """显示浏览器启动指南"""
        guides = {
            'chrome': r"""
            Chrome浏览器启动步骤：
            1. 找到Chrome浏览器快捷方式
            2. 右键 -> 属性
            3. 在"目标"后添加：--remote-debugging-port=9222
            4. 示例：C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222
            """,
            
            'edge': r"""
            Edge浏览器启动步骤：
            1. 找到Edge浏览器快捷方式
            2. 右键 -> 属性
            3. 在"目标"后添加：--remote-debugging-port=9222
            4. 示例：C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --remote-debugging-port=9222
            """,
            
            'qqbrowser': r"""
            QQ浏览器启动步骤：
            1. 找到QQ浏览器快捷方式
            2. 右键 -> 属性
            3. 在"目标"后添加：--remote-debugging-port=9222
            4. 示例：C:\Program Files\Tencent\QQBrowser\QQBrowser.exe --remote-debugging-port=9222
            """
        }
        
        guide = guides.get(browser_type, "不支持的浏览器类型")
        logging.info(guide)
        return guide