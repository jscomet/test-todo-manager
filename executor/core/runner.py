"""执行引擎 - BabyAGI 核心循环"""
import time
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.task import Task, TaskStatus, TaskType
from core.queue import TaskQueue
from opencode.client import OpenCodeClient
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.thinking import ThinkingRecorder

class ExecutionRunner:
    """执行引擎"""
    
    def __init__(self, config: dict, queue: TaskQueue):
        self.config = config
        self.queue = queue
        self.iteration = 0
        self.running = False
        
        # 初始化组件
        opencode_config = config.get("opencode", {})
        timeout = opencode_config.get("timeout", 300)
        server_url = opencode_config.get("server_url", "http://localhost:4096")
        self.opencode = OpenCodeClient(server_url=server_url, timeout=timeout)
        self.short_memory = ShortTermMemory()
        self.long_memory = LongTermMemory()
        self.thinking = ThinkingRecorder()
    
    def run(self):
        """主循环"""
        self.running = True
        
        while self.running:
            self.iteration += 1
            print(f"\n{'='*60}")
            print(f"🔄 第 {self.iteration} 轮执行")
            print(f"{'='*60}")
            
            # 1. 获取任务
            task = self.queue.get_next()
            
            if not task:
                print("✨ 所有任务完成！")
                break
            
            print(f"📝 任务: [{task.priority}] {task.objective[:50]}...")
            
            # 2. 加载记忆
            context = self._load_context(task)
            print(f"💾 加载上下文: {len(context['recent_thinking'])} 个思考记录")
            
            # 3. 构建 Prompt
            prompt = self._build_prompt(task, context)
            
            # 4. 执行
            result = self._execute_task(task, prompt)
            
            # 5. 处理结果
            if result["success"]:
                self._handle_success(task, result)
            else:
                self._handle_failure(task, result)
            
            # 6. 保存记忆
            self._save_memory(task, result)
            
            # 7. 休眠
            interval = self.config.get("executor", {}).get("poll_interval", 5)
            print(f"⏳ 等待 {interval} 秒...")
            time.sleep(interval)
    
    def _load_context(self, task: Task) -> dict:
        """加载上下文记忆"""
        context = self.short_memory.load()
        
        # 加载最近 2 个思考记录
        recent_thinking = self.short_memory.get_recent_thinking(2)
        context["recent_thinking"] = recent_thinking
        
        # 加载相关经验
        keyword = task.objective.split()[0] if task.objective else ""
        relevant = self.long_memory.find_relevant(keyword)
        context["relevant_experiences"] = relevant
        
        return context
    
    def _build_prompt(self, task: Task, context: dict) -> str:
        """构建 Prompt"""
        # 读取 Prompt 模板
        prompt_file = Path(__file__).parent.parent / "prompts" / f"{task.task_type.value}.txt"
        
        if not prompt_file.exists():
            # 默认使用 coder prompt
            prompt_file = Path(__file__).parent.parent / "prompts" / "coder.txt"
        
        template = prompt_file.read_text(encoding='utf-8')
        
        # 构建上下文字符串
        context_str = ""
        if context.get("recent_thinking"):
            context_str += "最近完成的类似任务:\n"
            for thinking in context["recent_thinking"]:
                context_str += f"- {thinking}\n"
        
        if context.get("relevant_experiences"):
            context_str += "\n相关经验:\n"
            for exp in context["relevant_experiences"][:2]:
                context_str += f"- {exp.get('pattern', '')}: {exp.get('solution', '')}\n"
        
        # 渲染模板
        prompt = template.format(
            objective=task.objective,
            context=context_str
        )
        
        return prompt
    
    def _execute_task(self, task: Task, prompt: str) -> dict:
        """执行单个任务"""
        print(f"🤖 调用 OpenCode 执行任务...")
        
        # 更新状态为执行中
        task.status = TaskStatus.EXECUTING
        self.queue.update_status(task.id, TaskStatus.EXECUTING)
        
        # 调用 OpenCode
        result = self.opencode.execute(prompt)
        
        print(f"   执行结果: {'成功' if result['success'] else '失败'}")
        if result.get("error"):
            print(f"   错误: {result['error'][:100]}...")
        
        return result
    
    def _handle_success(self, task: Task, result: dict):
        """处理成功"""
        print("✅ 任务完成")
        
        # 更新队列状态
        self.queue.update_status(task.id, TaskStatus.COMPLETED)
        
        # 保存思考记录
        self.thinking.save(task, result["output"])
        
        # 记录成功经验
        self.long_memory.record(
            pattern=task.objective[:50],
            solution=result["output"][:200],
            success=True
        )
    
    def _handle_failure(self, task: Task, result: dict):
        """处理失败"""
        print("❌ 任务失败")
        task.attempts += 1
        
        max_attempts = self.config.get("executor", {}).get("max_attempts", 3)
        
        if task.attempts < max_attempts:
            print(f"   将在下一轮重试 ({task.attempts}/{max_attempts})")
            
            # 生成修复任务
            repair_task = Task(
                id=f"repair-{task.id}-{task.attempts}",
                objective=f"修复: {task.objective}",
                task_type=TaskType.REPAIR,
                priority="🔴",
                context={"error": result.get("error", ""), "parent_id": task.id}
            )
            self.queue.add(repair_task)
            print(f"   生成修复任务: {repair_task.id}")
        else:
            print(f"   超过最大重试次数，标记为失败")
            self.queue.update_status(task.id, TaskStatus.FAILED)
        
        # 记录失败经验
        self.long_memory.record(
            pattern=task.objective[:50],
            solution=result.get("error", "")[:200],
            success=False
        )
    
    def _save_memory(self, task: Task, result: dict):
        """保存记忆"""
        # 更新短期记忆
        self.short_memory.save({
            "current_task": task.id,
            "last_thinking": f"thinking/task-{task.id}.md",
            "timestamp": datetime.now().isoformat()
        })
    
    def save_state(self):
        """保存状态"""
        self.short_memory.save({
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat()
        })
