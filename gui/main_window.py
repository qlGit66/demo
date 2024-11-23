from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QLabel, QTextEdit, QMessageBox)
from utils.config_manager import ConfigManager
from core.auto_answer import ChaoXingAutoAnswer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('超星自动答题')
        self.setFixedSize(400, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 超星账号密码
        username_layout = QHBoxLayout()
        username_label = QLabel('超星账号:')
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        password_layout = QHBoxLayout()
        password_label = QLabel('超星密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # 星火配置
        xunfei_label = QLabel('星火配置:')
        layout.addWidget(xunfei_label)
        
        app_id_layout = QHBoxLayout()
        app_id_label = QLabel('APPID:')
        self.app_id_input = QLineEdit()
        app_id_layout.addWidget(app_id_label)
        app_id_layout.addWidget(self.app_id_input)
        
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel('APIKey:')
        self.api_key_input = QLineEdit()
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        
        api_secret_layout = QHBoxLayout()
        api_secret_label = QLabel('APISecret:')
        self.api_secret_input = QLineEdit()
        api_secret_layout.addWidget(api_secret_label)
        api_secret_layout.addWidget(self.api_secret_input)
        
        # 题库Token（可选）
        token_layout = QHBoxLayout()
        token_label = QLabel('题库Token(可选):')
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('不填则使用AI答题')
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        
        # 开始按钮
        self.start_button = QPushButton('开始答题')
        self.start_button.clicked.connect(self.start_answering)
        
        # 日志显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # 添加所有组件
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addLayout(app_id_layout)
        layout.addLayout(api_key_layout)
        layout.addLayout(api_secret_layout)
        layout.addLayout(token_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.log_display)
        
        # 加载保存的配置
        config = self.config_manager.get_all_config()
        login_info = config['login']
        if login_info:
            self.username_input.setText(login_info.get('username', ''))
            self.password_input.setText(login_info.get('password', ''))
            
        ai_config = config.get('ai_config', {})
        if ai_config:
            self.app_id_input.setText(ai_config.get('app_id', ''))
            self.api_key_input.setText(ai_config.get('api_key', ''))
            self.api_secret_input.setText(ai_config.get('api_secret', ''))
            
        if config.get('token'):
            self.token_input.setText(config['token'])
        
    def start_answering(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        app_id = self.app_id_input.text().strip()
        api_key = self.api_key_input.text().strip()
        api_secret = self.api_secret_input.text().strip()
        token = self.token_input.text().strip()
        
        # 验证必填项
        if not all([username, password]):
            QMessageBox.warning(self, '警告', '请填写超星账号和密码！')
            return
            
        if not all([app_id, api_key, api_secret]) and not token:
            QMessageBox.warning(self, '警告', '请填写星火配置或题库Token！')
            return
            
        self.start_button.setEnabled(False)
        self.log_display.clear()
        
        # 保存配置
        self.config_manager.save_all_config(
            username=username,
            password=password,
            app_id=app_id,
            api_key=api_key,
            api_secret=api_secret,
            token=token
        )
        
        # 创建自动答题实例
        auto_answer = ChaoXingAutoAnswer(
            chaoxing_token=token,
            app_id=app_id,
            api_key=api_key,
            api_secret=api_secret
        )
        
        # 尝试登录
        self.log_display.append("正在启动浏览器...")
        if not auto_answer.login(username, password):
            QMessageBox.warning(self, '错误', '登录失败！')
            self.start_button.setEnabled(True)
            return
            
        # 开始答题
        try:
            self.log_display.append("开始自动答题...")
            if auto_answer.answer_all_questions():
                QMessageBox.information(self, '完成', '答题完成！')
            else:
                QMessageBox.warning(self, '错误', '答题过程出现错误')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'发生错误: {str(e)}')
        finally:
            self.start_button.setEnabled(True) 