import json
import os
from datetime import datetime
from typing import Dict, Optional
import hashlib

class QuestionBank:
    def __init__(self, logger):
        self.logger = logger
        self.bank_file = 'data/question_bank.json'
        self.bank = self._load_bank()
        
    def _load_bank(self) -> Dict:
        """加载题库"""
        if not os.path.exists(self.bank_file):
            return {
                "metadata": {
                    "last_update": datetime.now().isoformat(),
                    "total_questions": 0,
                    "correct_rate": 0.0
                },
                "questions": {}
            }
            
        try:
            with open(self.bank_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载题库失败: {str(e)}")
            return {"metadata": {}, "questions": {}}
            
    def save_bank(self):
        """保存题库"""
        try:
            os.makedirs(os.path.dirname(self.bank_file), exist_ok=True)
            with open(self.bank_file, 'w', encoding='utf-8') as f:
                json.dump(self.bank, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存题库失败: {str(e)}")
            
    def add_question(self, question_text: str, answer: str, 
                    question_type: str, source: str, is_correct: Optional[bool] = None):
        """添加题目到题库"""
        question_id = self._generate_question_id(question_text)
        
        self.bank["questions"][question_id] = {
            "text": question_text,
            "answer": answer,
            "type": question_type,
            "source": source,
            "is_correct": is_correct,
            "timestamp": datetime.now().isoformat(),
            "usage_count": 1,
            "correct_count": 1 if is_correct else 0
        }
        
        self._update_metadata()
        self.save_bank()
        
    def update_question(self, question_id: str, is_correct: bool):
        """更新题目状态"""
        if question_id in self.bank["questions"]:
            question = self.bank["questions"][question_id]
            question["usage_count"] += 1
            if is_correct:
                question["correct_count"] += 1
            question["is_correct"] = is_correct
            question["last_used"] = datetime.now().isoformat()
            
            self._update_metadata()
            self.save_bank()
            
    def _generate_question_id(self, question_text: str) -> str:
        """生成题目ID"""
        return hashlib.md5(question_text.encode()).hexdigest()
        
    def _update_metadata(self):
        """更新题库元数据"""
        total_questions = len(self.bank["questions"])
        total_correct = sum(
            1 for q in self.bank["questions"].values() 
            if q.get("is_correct") is True
        )
        
        self.bank["metadata"].update({
            "last_update": datetime.now().isoformat(),
            "total_questions": total_questions,
            "correct_rate": total_correct / total_questions if total_questions > 0 else 0
        })
        
    def get_answer(self, question_text: str) -> Optional[Dict]:
        """查找题目答案"""
        question_id = self._generate_question_id(question_text)
        return self.bank["questions"].get(question_id)
        
    def generate_report(self) -> Dict:
        """生成题库报告"""
        questions = self.bank["questions"]
        return {
            "total_questions": len(questions),
            "correct_rate": self.bank["metadata"]["correct_rate"],
            "question_types": self._count_question_types(),
            "source_distribution": self._count_sources(),
            "recent_questions": self._get_recent_questions(10)
        }
        
    def _count_question_types(self) -> Dict:
        """统计题目类型分布"""
        type_count = {}
        for q in self.bank["questions"].values():
            q_type = q.get("type", "unknown")
            type_count[q_type] = type_count.get(q_type, 0) + 1
        return type_count
        
    def _count_sources(self) -> Dict:
        """统计答案来源分布"""
        source_count = {}
        for q in self.bank["questions"].values():
            source = q.get("source", "unknown")
            source_count[source] = source_count.get(source, 0) + 1
        return source_count
        
    def _get_recent_questions(self, limit: int) -> list:
        """获取最近的题目"""
        questions = list(self.bank["questions"].values())
        questions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return questions[:limit] 