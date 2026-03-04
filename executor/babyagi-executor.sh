#!/bin/bash
# BabyAGI Style Task Executor
# 基于 BabyAGI 思想的自动化任务执行脚本

set -e

PROJECT_DIR="/root/.openclaw/workspace/test/todo-manager"
TASKS_FILE="$PROJECT_DIR/tasks.json"
LOG_FILE="$PROJECT_DIR/execution.log"

cd "$PROJECT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

# 获取当前任务列表
get_tasks() {
    if [ -f "$TASKS_FILE" ]; then
        cat "$TASKS_FILE"
    else
        echo "[]"
    fi
}

# 检查是否还有待完成的任务
check_pending_tasks() {
    local tasks=$(get_tasks)
    local pending=$(echo "$tasks" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len([t for t in d if not t.get('done', False)]))")
    echo "$pending"
}

# 获取下一个待完成的任务
get_next_task() {
    local tasks=$(get_tasks)
    local next_task=$(echo "$tasks" | python3 -c "import sys,json; d=json.load(sys.stdin); tasks=[t for t in d if not t.get('done', False)]; print(json.dumps(tasks[0]) if tasks else '{}')")
    echo "$next_task"
}

# 获取任务描述
get_task_description() {
    local task="$1"
    echo "$task" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('content', '未知任务'))"
}

get_task_id() {
    local task="$1"
    echo "$task" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id', 0))"
}

# 更新任务状态为完成
mark_task_done() {
    local task_id="$1"
    local tasks=$(get_tasks)
    echo "$tasks" | python3 -c "import sys,json; d=json.load(sys.stdin); [t.update({'done': True}) for t in d if t.get('id') == $task_id]; json.dump(d, sys.stdout, indent=2)" > "$TASKS_FILE.tmp"
    mv "$TASKS_FILE.tmp" "$TASKS_FILE"
}

# 使用 opencode 执行任务
execute_task_with_opencode() {
    local task_desc="$1"
    local task_id="$2"
    
    log "开始执行任务 [$task_id]: $task_desc"
    
    # 构建提示词
    local prompt="你是一个任务执行助手。请完成以下任务：

任务: $task_desc

要求：
1. 分析任务需求
2. 编写或修改必要的代码
3. 确保代码可以正常运行
4. 完成后报告执行结果

当前工作目录: $PROJECT_DIR
项目信息:
- 这是一个 Python CLI Todo 管理器
- 主程序是 todo.py
- 使用 JSON 存储任务

请执行任务并报告结果。"

    # 调用 opencode 执行
    opencode run "$prompt" 2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    return $exit_code
}

# 测试功能
test_functionality() {
    log "测试功能..."
    
    # 测试添加任务
    python3 todo.py add "测试任务_$(date +%s)" 2>&1 | tee -a "$LOG_FILE"
    
    # 测试列出任务
    python3 todo.py list 2>&1 | tee -a "$LOG_FILE"
    
    # 测试标记完成
    python3 todo.py done 1 2>&1 | tee -a "$LOG_FILE"
    
    # 测试删除任务
    python3 todo.py delete 1 2>&1 | tee -a "$LOG_FILE"
    
    success "功能测试完成"
}

# Git 提交和推送
git_commit_and_push() {
    log "提交代码到 Git..."
    
    # 添加所有更改
    git add -A 2>&1 | tee -a "$LOG_FILE"
    
    # 检查是否有更改要提交
    if git diff --cached --quiet; then
        warning "没有更改需要提交"
        return 0
    fi
    
    # 提交
    local commit_msg="$(date '+%Y-%m-%d %H:%M:%S') - 自动更新任务状态"
    git commit -m "$commit_msg" 2>&1 | tee -a "$LOG_FILE"
    
    # 推送
    git push origin main 2>&1 | tee -a "$LOG_FILE"
    
    success "代码已推送到 GitHub"
}

# 更新任务列表（由 opencode 修改）
update_task_list() {
    log "检查任务列表更新..."
    
    # 提示 opencode 检查并更新任务列表
    local prompt="请检查当前任务列表，根据执行结果：
1. 如果任务已完成，更新任务状态
2. 如果需要创建新任务，添加到列表
3. 如果需要修改现有任务，进行更新

当前任务列表: $(cat $TASKS_FILE)"

    opencode run "$prompt" 2>&1 | tee -a "$LOG_FILE"
}

# 显示当前任务状态
show_status() {
    local total=$(echo "$(get_tasks)" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))")
    local pending=$(check_pending_tasks)
    local completed=$((total - pending))
    
    echo ""
    echo "========================================"
    echo "📊 任务统计"
    echo "========================================"
    echo "总任务数: $total"
    echo "已完成: $completed"
    echo "待完成: $pending"
    echo "========================================"
    echo ""
    
    # 显示任务列表
    python3 todo.py list 2>/dev/null || echo "暂无任务"
    echo ""
}

# 主循环
main_loop() {
    log "========================================"
    log "🚀 BabyAGI 风格任务执行器启动"
    log "========================================"
    
    local iteration=0
    local max_iterations=50  # 防止无限循环
    
    while true; do
        iteration=$((iteration + 1))
        log "========================================"
        log "🔄 第 $iteration 轮执行"
        log "========================================"
        
        # 显示当前状态
        show_status
        
        # 检查是否还有任务
        local pending=$(check_pending_tasks)
        
        if [ "$pending" -eq 0 ]; then
            success "所有任务已完成！退出循环"
            break
        fi
        
        if [ "$iteration" -gt "$max_iterations" ]; then
            warning "达到最大迭代次数 ($max_iterations)，退出"
            break
        fi
        
        # 获取下一个任务
        local next_task=$(get_next_task)
        
        if [ "$next_task" = "{}" ] || [ -z "$next_task" ]; then
            warning "没有可执行的任务"
            break
        fi
        
        local task_id=$(get_task_id "$next_task")
        local task_desc=$(get_task_description "$next_task")
        
        log "获取到任务 [$task_id]: $task_desc"
        
        # 使用 opencode 执行任务
        if execute_task_with_opencode "$task_desc" "$task_id"; then
            success "任务 [$task_id] 执行完成"
            
            # 标记任务完成
            mark_task_done "$task_id"
            
            # 测试功能
            test_functionality
            
            # Git 提交和推送
            git_commit_and_push
            
            # 更新任务列表
            update_task_list
            
        else
            error "任务 [$task_id] 执行失败"
            warning "跳过此任务，继续下一个"
            # 标记为失败状态
        fi
        
        # 短暂休息，避免请求过快
        log "等待 5 秒后继续..."
        sleep 5
    done
    
    log "========================================"
    log "🏁 执行循环结束"
    log "总轮数: $iteration"
    log "========================================"
}

# 初始化
init() {
    log "初始化执行环境..."
    
    # 确保在正确的目录
    cd "$PROJECT_DIR"
    
    # 确保 Git 远程仓库配置正确
    if ! git remote get-url origin &>/dev/null; then
        error "Git 远程仓库未配置"
        exit 1
    fi
    
    # 确保任务文件存在
    if [ ! -f "$TASKS_FILE" ]; then
        echo "[]" > "$TASKS_FILE"
        log "创建空的任务列表"
    fi
    
    success "初始化完成"
}

# 添加示例任务（如果没有任务）
add_sample_tasks() {
    local total=$(echo "$(get_tasks)" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))")
    
    if [ "$total" -eq 0 ]; then
        log "添加示例任务..."
        
        cat > "$TASKS_FILE" << 'EOF'
[
  {
    "id": 1,
    "content": "优化 todo.py 的代码结构，添加函数注释",
    "done": false,
    "created_at": "2026-03-04 01:00:00"
  },
  {
    "id": 2,
    "content": "添加任务优先级功能",
    "done": false,
    "created_at": "2026-03-04 01:00:01"
  },
  {
    "id": 3,
    "content": "添加任务截止日期功能",
    "done": false,
    "created_at": "2026-03-04 01:00:02"
  }
]
EOF
        success "已添加 3 个示例任务"
    fi
}

# 主函数
main() {
    init
    add_sample_tasks
    main_loop
}

# 运行
main "$@"
