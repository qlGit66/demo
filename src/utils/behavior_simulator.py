import numpy as np
from typing import List, Tuple, Dict
import random
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class BehaviorSimulator:
    def __init__(self, logger):
        self.logger = logger
        self.behavior_patterns = self._load_behavior_patterns()
        self.current_pattern = None
        self.last_action_time = datetime.now()
        
    def _load_behavior_patterns(self) -> Dict:
        """加载行为模式"""
        return {
            'typing': {
                'speed_variations': self._generate_typing_patterns(),
                'error_rate': random.uniform(0.01, 0.05),
                'correction_behavior': self._generate_correction_patterns()
            },
            'mouse': {
                'movement_patterns': self._generate_mouse_patterns(),
                'click_patterns': self._generate_click_patterns(),
                'scroll_patterns': self._generate_scroll_patterns()
            },
            'page_interaction': {
                'reading_patterns': self._generate_reading_patterns(),
                'navigation_patterns': self._generate_navigation_patterns()
            }
        }
        
    def simulate_typing(self, driver, element, text: str):
        """模拟真实的打字行为"""
        pattern = self.behavior_patterns['typing']
        
        for char in text:
            # 随机打字错误
            if random.random() < pattern['error_rate']:
                wrong_char = random.choice('qwertyuiop[]asdfghjkl;zxcvbnm,./')
                element.send_keys(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))
                element.send_keys(Keys.BACKSPACE)
                
            # 模拟按键时间变化
            typing_speed = random.gauss(
                pattern['speed_variations']['mean'],
                pattern['speed_variations']['std']
            )
            element.send_keys(char)
            time.sleep(max(0.05, typing_speed))
            
            # 随机暂停
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 1.5))
                
    def simulate_natural_mouse_movement(self, driver, target_element):
        """模拟自然的鼠标移动"""
        pattern = self.behavior_patterns['mouse']['movement_patterns']
        
        # 获取当前鼠标位置
        current_pos = self._get_current_mouse_position(driver)
        target_pos = self._get_element_center(target_element)
        
        # 生成贝塞尔曲线路径点
        points = self._generate_bezier_curve(
            current_pos,
            target_pos,
            control_points=random.randint(2, 4)
        )
        
        # 执行移动
        actions = ActionChains(driver)
        for point in points:
            actions.move_by_offset(point[0] - current_pos[0], point[1] - current_pos[1])
            current_pos = point
            
            # 随机速度变化
            sleep_time = random.gauss(
                pattern['speed']['mean'],
                pattern['speed']['std']
            )
            time.sleep(max(0.01, sleep_time))
            
        actions.perform()
        
    def _generate_bezier_curve(self, start: Tuple[int, int], 
                             end: Tuple[int, int], 
                             control_points: int) -> List[Tuple[int, int]]:
        """生成贝塞尔曲线路径"""
        points = [start]
        
        # 生成控制点
        controls = []
        for _ in range(control_points):
            x = random.randint(min(start[0], end[0]), max(start[0], end[0]))
            y = random.randint(min(start[1], end[1]), max(start[1], end[1]))
            controls.append((x, y))
            
        controls.append(end)
        
        # 生成曲线点
        t_points = np.linspace(0, 1, 50)
        for t in t_points:
            point = self._bezier_point(t, [start] + controls)
            points.append(point)
            
        return points
        
    def _bezier_point(self, t: float, points: List[Tuple[int, int]]) -> Tuple[int, int]:
        """计算贝塞尔曲线上的点"""
        n = len(points) - 1
        x = sum(self._bernstein(n, i, t) * points[i][0] for i in range(n + 1))
        y = sum(self._bernstein(n, i, t) * points[i][1] for i in range(n + 1))
        return (int(x), int(y))
        
    def _bernstein(self, n: int, i: int, t: float) -> float:
        """计算伯恩斯坦多项式"""
        return self._comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
        
    def _comb(self, n: int, k: int) -> int:
        """计算组合数"""
        if k > n:
            return 0
        if k == 0 or k == n:
            return 1
        return self._comb(n - 1, k - 1) + self._comb(n - 1, k) 