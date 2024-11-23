from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLineEdit, QLabel, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from ..auto_answer import ChaoXingAutoAnswer

class AnswerThread(QThread):
    """答题线程"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, username, password, chaoxing_token, openai_api_key):
        super().__init__()
        self.username = username
        self.password = password
        self.chaoxing_token = chaoxing_token
        self.openai_api_key = openai_api_key
        
    def run(self):
        try:
            auto_answer = ChaoXingAutoAnswer(
                chaoxing_token=self.chaoxing_token,
                openai_api_key=self.openai_api_key
            )
            
            # 登录
            self.progress_signal.emit("正在登录...")
            if not auto_answer.login(self.username, self.password):
                self.finished_signal.emit(False, "登录失败")
                return
                
            # 开始答题
            self.progress_signal.emit("开始答题...")
            result = auto_answer.answer_all_questions()
            
            if result:
                self.finished_signal.emit(True, "答题完成！")
            else:
                self.finished_signal.emit(False, "答题过程出现错误")
                
        except Exception as e:
            self.finished_signal.emit(False, f"发生错误: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('超星自动答题')
        self.setFixedSize(400, 500)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 账号输入
        username_layout = QHBoxLayout()
        username_label = QLabel('账号:')
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Token输入（可选）
        token_layout = QHBoxLayout()
        token_label = QLabel('题库Token(可选):')
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText('不填则使用AI答题')
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        
        # 星火API密钥输入
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel('星火API密钥:')
        self.api_key_input = QLineEdit()
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        
        # 添加获取API密钥的帮助链接
        help_label = QLabel('<a href="https://dashscope.console.aliyun.com/">点击获取星火API密钥</a>')
        help_label.setOpenExternalLinks(True)
        api_key_layout.addWidget(help_label)
        
        # 开始按钮
        self.start_button = QPushButton('开始答题')
        self.start_button.clicked.connect(self.start_answering)
        
        # 日志显示
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # 添加所有组件
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addLayout(token_layout)
        layout.addLayout(api_key_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.log_display)
        
        # 状态栏
        self.statusBar().showMessage('就绪')
        
    def start_answering(self):
        """开始答题"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        token = self.token_input.text().strip()
        api_key = self.api_key_input.text().strip()
        
        if not all([username, password, api_key]):
            QMessageBox.warning(self, '警告', '请填写账号、密码和OpenAI API密钥！')
            return
            
        # 创建并启动答题线程
        self.answer_thread = AnswerThread(
            username=username,
            password=password,
            chaoxing_token=token if token else None,
            openai_api_key=api_key
        )
        self.answer_thread.progress_signal.connect(self.update_progress)
        self.answer_thread.finished_signal.connect(self.on_answering_finished)
        self.answer_thread.start()
        
    def update_progress(self, message):
        """更新进度信息"""
        self.log_display.append(message)
        self.statusBar().showMessage(message)
        
    def on_answering_finished(self, success, message):
        """答题完成回调"""
        self.start_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, '完成', message)
        else:
            QMessageBox.warning(self, '错误', message)
            
        self.statusBar().showMessage(message) 