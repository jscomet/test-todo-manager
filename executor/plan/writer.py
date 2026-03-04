"""PLAN.md 写入器"""
import re
from pathlib import Path

class PlanWriter:
    """PLAN.md 写入器"""
    
    def __init__(self, plan_file: str = "docs/PLAN.md"):
        self.plan_file = Path(plan_file)
    
    def update_status(self, task_id: str, new_status: str) -> bool:
        """更新任务状态"""
        if not self.plan_file.exists():
            print(f"⚠️ PLAN.md 不存在: {self.plan_file}")
            return False
        
        try:
            content = self.plan_file.read_text(encoding='utf-8')
            
            # 简单实现：找到第一个待开始的任务并更新
            # 实际应该根据 task_id 精确定位
            
            # 替换第一个 ⏳ 待开始
            if new_status == "🔄 进行中":
                content = content.replace("| ⏳ 待开始 |", "| 🔄 进行中 |", 1)
            elif new_status == "✅ 已完成":
                content = content.replace("| 🔄 进行中 |", "| ✅ 已完成 |", 1)
            elif new_status == "❌ 失败":
                content = content.replace("| 🔄 进行中 |", "| ❌ 失败 |", 1)
            
            self.plan_file.write_text(content, encoding='utf-8')
            return True
            
        except Exception as e:
            print(f"⚠️ 更新 PLAN.md 失败: {e}")
            return False
