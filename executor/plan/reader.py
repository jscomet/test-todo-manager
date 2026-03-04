"""PLAN.md 读写"""
import re
from pathlib import Path
from typing import List, Optional

class PlanReader:
    """PLAN.md 读取器"""
    
    def __init__(self, plan_file: str = "docs/PLAN.md"):
        self.plan_file = Path(plan_file)
    
    def read_tasks(self) -> List[dict]:
        """读取任务列表"""
        if not self.plan_file.exists():
            return []
        
        content = self.plan_file.read_text(encoding='utf-8')
        
        # 解析任务表格
        tasks = []
        # 匹配: | 优先级 | 任务 | 状态 | ...
        pattern = r'\|\s*([🔴🟡🟢])\s*\|\s*([^|]+?)\s*\|\s*(⏳|🔄|✅|❌)'
        matches = re.findall(pattern, content)
        
        for idx, (priority, objective, status) in enumerate(matches, 1):
            tasks.append({
                "id": f"task-{idx:03d}",
                "priority": priority,
                "objective": objective.strip(),
                "status": status
            })
        
        return tasks

class PlanWriter:
    """PLAN.md 写入器"""
    
    def __init__(self, plan_file: str = "docs/PLAN.md"):
        self.plan_file = Path(plan_file)
    
    def update_status(self, task_id: str, new_status: str):
        """更新任务状态"""
        if not self.plan_file.exists():
            return False
        
        content = self.plan_file.read_text(encoding='utf-8')
        
        # 简单替换（实际需要更精确的匹配）
        # TODO: 实现精确的状态替换
        
        self.plan_file.write_text(content, encoding='utf-8')
        return True
