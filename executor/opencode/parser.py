"""OpenCode 结果解析器"""
import re
from typing import Dict, List

class ResultParser:
    """结果解析器"""
    
    @staticmethod
    def parse(output: str) -> Dict:
        """解析 OpenCode 输出"""
        result = {
            "success": True,
            "files_changed": [],
            "tests_passed": None,
            "git_committed": False,
            "summary": ""
        }
        
        if not output:
            return result
        
        # 检测文件变更
        file_patterns = [
            r'创建文件[:：]\s*(\S+)',
            r'修改文件[:：]\s*(\S+)',
            r'edit\s+(\S+)',
            r'write\s+(\S+)'
        ]
        for pattern in file_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            result["files_changed"].extend(matches)
        
        # 检测测试结果
        if 'pytest' in output or 'test' in output.lower():
            if 'passed' in output.lower() or '通过' in output:
                result["tests_passed"] = True
            elif 'failed' in output.lower() or '失败' in output:
                result["tests_passed"] = False
        
        # 检测 Git 提交
        if 'git commit' in output.lower() or 'committed' in output.lower():
            result["git_committed"] = True
        
        # 提取总结（最后 500 字符）
        lines = output.strip().split('\n')
        result["summary"] = '\n'.join(lines[-10:]) if len(lines) > 10 else output
        
        return result
    
    @staticmethod
    def extract_error(error_output: str) -> str:
        """提取错误信息"""
        if not error_output:
            return ""
        
        # 提取关键错误信息
        lines = error_output.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception', '错误', '失败']):
                return line.strip()
        
        return error_output[:200]
