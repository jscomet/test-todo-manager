"""结果解析器 - 解析 OpenCode XML 输出"""
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ParsedResult:
    """解析后的结果"""
    status: str                    # success | failed
    summary: str
    files_changed: List[str]
    tests_passed: Optional[bool]
    test_details: str
    git_committed: bool
    commit_hash: Optional[str]
    notes: str
    raw_xml: str


class ResultParser:
    """XML 结果解析器"""
    
    @staticmethod
    def parse(output: str) -> ParsedResult:
        """
        解析 OpenCode 输出的 XML 结果
        
        Args:
            output: OpenCode 的完整输出
            
        Returns:
            ParsedResult: 解析后的结构化结果
        """
        # 提取 XML 部分
        xml_match = re.search(r'<result>.*?</result>', output, re.DOTALL)
        
        if not xml_match:
            # 没有 XML 格式输出，尝试从文本推断
            return ResultParser._parse_fallback(output)
        
        xml_content = xml_match.group(0)
        
        try:
            root = ET.fromstring(xml_content)
            
            # 解析基本信息
            status = ResultParser._get_text(root, 'status', 'unknown')
            summary = ResultParser._get_text(root, 'summary', '')
            notes = ResultParser._get_text(root, 'notes', '')
            
            # 解析文件列表
            files_changed = []
            files_elem = root.find('files_changed')
            if files_elem is not None:
                for file_elem in files_elem.findall('file'):
                    if file_elem.text:
                        files_changed.append(file_elem.text.strip())
            
            # 解析测试信息
            tests_passed = None
            test_details = ''
            tests_elem = root.find('tests')
            if tests_elem is not None:
                passed_text = ResultParser._get_text(tests_elem, 'passed', '')
                tests_passed = passed_text.lower() == 'true' if passed_text else None
                test_details = ResultParser._get_text(tests_elem, 'details', '')
            
            # 解析 Git 信息
            git_committed = False
            commit_hash = None
            git_elem = root.find('git')
            if git_elem is not None:
                committed_text = ResultParser._get_text(git_elem, 'committed', '')
                git_committed = committed_text.lower() == 'true' if committed_text else False
                commit_hash = ResultParser._get_text(git_elem, 'commit_hash') or None
            
            return ParsedResult(
                status=status,
                summary=summary,
                files_changed=files_changed,
                tests_passed=tests_passed,
                test_details=test_details,
                git_committed=git_committed,
                commit_hash=commit_hash,
                notes=notes,
                raw_xml=xml_content
            )
            
        except ET.ParseError as e:
            # XML 解析失败，使用 fallback
            return ResultParser._parse_fallback(output, error=str(e))
    
    @staticmethod
    def _get_text(parent: ET.Element, tag: str, default: str = '') -> str:
        """安全获取子元素文本"""
        elem = parent.find(tag)
        return elem.text.strip() if elem is not None and elem.text else default
    
    @staticmethod
    def _parse_fallback(output: str, error: str = None) -> ParsedResult:
        """
        当 XML 解析失败时的 fallback 解析
        
        从文本中推断关键信息
        """
        # 推断状态
        status = 'success' if 'success' in output.lower() or '完成' in output else 'unknown'
        
        # 推断测试状态
        tests_passed = None
        if 'pytest' in output or 'test' in output.lower():
            if 'passed' in output.lower() or '通过' in output:
                tests_passed = True
            elif 'failed' in output.lower() or '失败' in output:
                tests_passed = False
        
        # 推断 Git 提交
        git_committed = 'git commit' in output.lower() or 'committed' in output.lower()
        
        # 提取 commit hash
        commit_hash = None
        hash_match = re.search(r'commit\s+([a-f0-9]{7,40})', output, re.IGNORECASE)
        if hash_match:
            commit_hash = hash_match.group(1)
        
        # 提取摘要（最后 500 字符）
        summary = output.strip()[-500:] if len(output.strip()) > 500 else output.strip()
        
        notes = f"XML 解析失败，使用 fallback 推断"
        if error:
            notes += f" (错误: {error})"
        
        return ParsedResult(
            status=status,
            summary=summary,
            files_changed=[],
            tests_passed=tests_passed,
            test_details='',
            git_committed=git_committed,
            commit_hash=commit_hash,
            notes=notes,
            raw_xml=output[-1000:]  # 保留最后 1000 字符
        )
    
    @staticmethod
    def parse_planner_tasks(output: str) -> List[Dict]:
        """
        专门解析 planner 类型的子任务列表
        
        Returns:
            List[Dict]: 子任务列表
        """
        xml_match = re.search(r'<result>.*?</result>', output, re.DOTALL)
        
        if not xml_match:
            return []
        
        try:
            root = ET.fromstring(xml_match.group(0))
            tasks = []
            
            tasks_elem = root.find('tasks')
            if tasks_elem is not None:
                for task_elem in tasks_elem.findall('task'):
                    task = {
                        'id': ResultParser._get_text(task_elem, 'id', ''),
                        'objective': ResultParser._get_text(task_elem, 'objective', ''),
                        'type': ResultParser._get_text(task_elem, 'type', 'coder'),
                        'priority': ResultParser._get_text(task_elem, 'priority', '🟡'),
                        'estimated_hours': ResultParser._get_text(task_elem, 'estimated_hours', '1.0'),
                        'dependencies': ResultParser._get_text(task_elem, 'dependencies', 'none'),
                        'acceptance_criteria': ResultParser._get_text(task_elem, 'acceptance_criteria', '')
                    }
                    tasks.append(task)
            
            return tasks
            
        except ET.ParseError:
            return []