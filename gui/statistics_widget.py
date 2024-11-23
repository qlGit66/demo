from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class StatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 使用文本方式显示统计信息
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        layout.addWidget(self.stats_display)
        
    def update_statistics(self, stats):
        """更新统计数据"""
        stats_text = f"""
        答题统计：
        总题数：{stats.get('total_questions', 0)}
        正确数：{stats.get('correct_answers', 0)}
        正确率：{stats.get('accuracy_rate', 0):.2%}
        
        题型分布：
        {self._format_question_types(stats.get('question_types', {}))}
        """
        self.stats_display.setText(stats_text)
        
    def _format_question_types(self, types):
        return '\n'.join([f"{k}: {v}" for k, v in types.items()]) 