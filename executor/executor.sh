#!/bin/bash
# BabyAGI Task Executor - BabyAGI 风格任务执行器
# 功能：无限循环获取任务 → opencode执行 → 测试 → Git提交 → 更新任务状态

set -e  # 遇到错误立即退出

# ==================== 配置 ====================
PROJECT_DIR="/root/.openclaw/workspace/test/todo-manager"
TASKS_FILE="$PROJECT_DIR/tasks.json"
LOG_FILE="$PROJECT_DIR/execution.log"
LOCK_FILE="/tmp/babyagi-executor.lock"

cd "$PROJECT_DIR"

# ==================== 颜色输出 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

# ==================== 任务管理 ====================

# 获取所有任务
get_all_tasks() {
    if [ -f "$TASKS_FILE" ]; then
        cat "$TASKS_FILE"
    else
        echo "[]"
    fi
}

# 获取待完成任务数量
count_pending() {
    local tasks=$(get_all_tasks)
    echo "$tasks" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
pending = [t for t in tasks if not t.get('done', False)]
print(len(pending))
"
}

# 获取下一个待完成任务
get_next_task() {
    local tasks=$(get_all_tasks)
    echo "$tasks" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for t in tasks:
    if not t.get('done', False):
        print(json.dumps(t))
        break
"
}

# 获取任务字段
get_task_field() {
    local task="$1"
    local field="$2"
    echo "$task" | python3 -c "
import sys, json
task = json.load(sys.stdin)
print(task.get('$field', ''))
"
}

# 标记任务完成
mark_done() {
    local task_id="$1"
    local tasks=$(get_all_tasks)
    echo "$tasks" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for t in tasks:
    if t.get('id') == $task_id:
        t['done'] = True
        t['completed_at'] = '$(date '+%Y-%m-%d %H:%M:%S')'
        break
json.dump(tasks, sys.stdout, indent=2)
" > "$TASKS_FILE.tmp"
    mv "$TASKS_FILE.tmp" "$TASKS_FILE"
}

# 删除任务
delete_task() {
    local task_id="$1"
    local tasks=$(get_all_tasks)
    echo "$tasks" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
tasks = [t for t in tasks if t.get('id') != $task_id]
# 重新编号
for i, t in enumerate(tasks, 1):
    t['id'] = i
json.dump(tasks, sys.stdout, indent=2)
" > "$TASKS_FILE.tmp"
    mv "$TASKS_FILE.tmp" "$TASKS_FILE"
}

# 添加新任务
add_task() {
    local content="$1"
    local tasks=$(get_all_tasks)
    echo "$tasks" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
new_id = max([t.get('id', 0) for t in tasks], default=0) + 1
new_task = {
    'id': new_id,
    'content': '$content',
    'done': False,
    'created_at': '$(date '+%Y-%m-%d %H:%M:%S')'
}
tasks.append(new_task)
json.dump(tasks, sys.stdout, indent=2)
" > "$TASKS_FILE.tmp"
    mv "$TASKS_FILE.tmp" "$TASKS_FILE"
}

# ==================== 执行阶段 ====================

# 阶段 1: 获取任务
phase_1_get_task() {
    log "========== 阶段 1: 获取任务 =========="
    
    local pending_count=$(count_pending)
    info "待完成任务数: $pending_count"
    
    if [ "$pending_count" -eq 0 ]; then
        info "没有待完成的任务，准备退出循环"
        return 1  # 返回1表示没有任务了
    fi
    
    local next_task=$(get_next_task)
    if [ -z "$next_task" ] || [ "$next_task" = "{}" ]; then
        error "无法获取下一个任务"
        return 1
    fi
    
    local task_id=$(get_task_field "$next_task" "id")
    local task_content=$(get_task_field "$next_task" "content")
    
    log "获取到任务 ID=$task_id: $task_content"
    
    # 导出任务信息供后续使用
    echo "$next_task" > /tmp/current_task.json
    
    return 0
}

# 阶段 2: opencode 执行任务
phase_2_execute() {
    log "========== 阶段 2: OpenCode 执行任务 =========="
    
    local task=$(cat /tmp/current_task.json)
    local task_id=$(get_task_field "$task" "id")
    local task_content=$(get_task_field "$task" "content")
    
    info "任务内容: $task_content"
    
    # 构建详细的提示词
    local prompt="你是一个专业的 Python 开发者。请完成以下任务：

【任务】$task_content

【项目信息】
- 项目路径: $PROJECT_DIR
- 这是一个 Python CLI Todo 管理器
- 主程序: todo.py
- 任务存储: tasks.json

【工作规范】(参考 AGENTS.md)
1. 分析任务需求，确定实现方案
2. 编写/修改代码，保持代码整洁
3. 添加必要的注释
4. 确保向后兼容
5. 不要破坏现有功能

【输出要求】
1. 完成代码编写
2. 报告完成的功能
3. 列出修改的文件
4. 说明如何测试

请开始执行任务。"

    log "调用 opencode..."
    
    # 使用 opencode run 模式执行
    if opencode run "$prompt" 2>&1 | tee -a "$LOG_FILE"; then
        success "OpenCode 执行完成"
        return 0
    else
        error "OpenCode 执行失败"
        return 1
    fi
}

# 阶段 3: 测试验证
phase_3_test() {
    log "========== 阶段 3: 测试验证 =========="
    
    local test_passed=true
    
    # 测试 1: 语法检查
    info "测试 1: Python 语法检查"
    if python3 -m py_compile todo.py 2>/dev/null; then
        success "语法检查通过"
    else
        error "语法检查失败"
        test_passed=false
    fi
    
    # 测试 2: 功能测试
    info "测试 2: 功能测试"
    
    # 清理之前的测试数据
    rm -f /tmp/test_todo.json
    
    # 测试添加
    if python3 todo.py add "测试任务_$(date +%s)" 2>&1 | tee -a "$LOG_FILE"; then
        success "添加功能正常"
    else
        error "添加功能失败"
        test_passed=false
    fi
    
    # 测试列出
    if python3 todo.py list 2>&1 | tee -a "$LOG_FILE"; then
        success "列出功能正常"
    else
        error "列出功能失败"
        test_passed=false
    fi
    
    if [ "$test_passed" = true ]; then
        success "所有测试通过"
        return 0
    else
        error "测试未通过"
        return 1
    fi
}

# 阶段 4: Git 提交推送
phase_4_git() {
    log "========== 阶段 4: Git 提交推送 =========="
    
    # 检查是否有变更
    if git diff --quiet && git diff --cached --quiet; then
        warn "没有变更需要提交"
        return 0
    fi
    
    # 获取当前任务信息用于提交信息
    local task=$(cat /tmp/current_task.json 2>/dev/null || echo '{}')
    local task_content=$(get_task_field "$task" "content")
    
    # 添加所有变更
    git add -A
    
    # 构建提交信息
    local commit_msg="Feat: $task_content

- 由 OpenCode Agent 自动执行
- 执行时间: $(date '+%Y-%m-%d %H:%M:%S')
- 参考: AGENTS.md 工作规范"
    
    # 提交
    if git commit -m "$commit_msg" 2>&1 | tee -a "$LOG_FILE"; then
        success "Git 提交成功"
    else
        error "Git 提交失败"
        return 1
    fi
    
    # 推送
    if git push origin main 2>&1 | tee -a "$LOG_FILE"; then
        success "推送到 GitHub 成功"
    else
        error "推送失败"
        return 1
    fi
    
    return 0
}

# 阶段 5: 更新任务状态
phase_5_update() {
    log "========== 阶段 5: 更新任务状态 =========="
    
    local task=$(cat /tmp/current_task.json)
    local task_id=$(get_task_field "$task" "id")
    local task_content=$(get_task_field "$task" "content")
    
    # 标记当前任务完成
    mark_done "$task_id"
    success "任务 $task_id 已标记为完成"
    
    # 让 opencode 分析是否需要创建新任务
    local prompt="任务已完成: $task_content

请分析是否需要基于这个任务创建新的后续任务：
1. 如果有遗漏的功能需要补充，创建新任务
2. 如果发现新的改进点，创建新任务
3. 如果没有，返回空

格式：一行一个任务，只返回任务内容，不要编号。如果没有新任务，返回 NONE"

    local new_tasks=$(opencode run "$prompt" 2>/dev/null | grep -v "^$" | head -5)
    
    if [ -n "$new_tasks" ] && [ "$new_tasks" != "NONE" ]; then
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                add_task "$line"
                info "创建新任务: $line"
            fi
        done <<< "$new_tasks"
    fi
    
    # 显示当前任务状态
    show_status
    
    return 0
}

# ==================== 辅助功能 ====================

show_status() {
    echo ""
    echo "========================================"
    echo "📊 当前任务状态"
    echo "========================================"
    
    python3 todo.py list 2>/dev/null || echo "暂无任务"
    
    local total=$(get_all_tasks | python3 -c "import sys,json;print(len(json.load(sys.stdin)))")
    local pending=$(count_pending)
    local done=$((total - pending))
    
    echo ""
    echo "总计: $total | 完成: $done | 待办: $pending"
    echo "========================================"
    echo ""
}

show_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║     BabyAGI Task Executor - 任务执行器        ║"
    echo "║         自动循环 · AI 驱动 · 持续集成          ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
}

# ==================== 主循环 ====================

main_loop() {
    show_banner
    
    log "初始化工作目录: $PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # 确保在 Git 仓库中
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "当前目录不是 Git 仓库"
        exit 1
    fi
    
    local iteration=0
    local max_iterations=100  # 防止无限循环的安全限制
    
    while true; do
        iteration=$((iteration + 1))
        
        log ""
        log "╔════════════════════════════════════════════════╗"
        log "║  第 $iteration 轮执行                          ║"
        log "╚════════════════════════════════════════════════╝"
        
        # 检查最大迭代次数
        if [ $iteration -gt $max_iterations ]; then
            warn "达到最大迭代次数 ($max_iterations)，退出循环"
            break
        fi
        
        # ===== 阶段 1: 获取任务 =====
        if ! phase_1_get_task; then
            info "没有更多任务，执行结束"
            break
        fi
        
        # ===== 阶段 2: 执行任务 =====
        if ! phase_2_execute; then
            warn "任务执行遇到问题，继续下一轮"
        fi
        
        # ===== 阶段 3: 测试 =====
        if ! phase_3_test; then
            error "测试失败，回滚变更..."
            git checkout -- . 2>/dev/null || true
            continue
        fi
        
        # ===== 阶段 4: Git 提交 =====
        if ! phase_4_git; then
            error "Git 操作失败"
        fi
        
        # ===== 阶段 5: 更新任务 =====
        phase_5_update
        
        # 短暂休息，避免 API 限流
        log "等待 3 秒后继续下一轮..."
        sleep 3
    done
    
    log ""
    log "╔════════════════════════════════════════════════╗"
    log "║  执行循环结束                                  ║"
    log "║  总轮数: $iteration                            ║"
    log "╚════════════════════════════════════════════════╝"
    
    show_status
}

# ==================== 入口 ====================

# 防止重复运行
if [ -f "$LOCK_FILE" ]; then
    warn "执行器已在运行 (PID: $(cat $LOCK_FILE))"
    exit 1
fi

trap "rm -f $LOCK_FILE; exit" INT TERM EXIT
echo $$ > "$LOCK_FILE"

# 清空日志
> "$LOG_FILE"

# 运行主循环
main_loop

# 清理
rm -f "$LOCK_FILE"
rm -f /tmp/current_task.json
