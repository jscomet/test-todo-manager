#!/bin/bash
# 文档驱动的 BabyAGI 执行器 v2.2
# 使用项目目录下的 opencode.json 配置权限

set -e

# ==================== 配置 ====================
PROJECT_DIR="/root/.openclaw/workspace/test/todo-manager"
SPEC_FILE="$PROJECT_DIR/SPEC.md"
PLAN_FILE="$PROJECT_DIR/PLAN.md"
DATA_TASKS_FILE="$PROJECT_DIR/data/tasks.json"
LOG_FILE="$PROJECT_DIR/logs/executor.log"
LOCK_FILE="/tmp/doc-driven-executor.lock"

# ==================== 配置 ====================
PROJECT_DIR="/root/.openclaw/workspace/test/todo-manager"
SPEC_FILE="$PROJECT_DIR/SPEC.md"
PLAN_FILE="$PROJECT_DIR/PLAN.md"
DATA_TASKS_FILE="$PROJECT_DIR/data/tasks.json"
LOG_FILE="$PROJECT_DIR/logs/executor.log"
LOCK_FILE="/tmp/doc-driven-executor.lock"

# 确保目录存在
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/core"
mkdir -p "$PROJECT_DIR/commands"

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

# ==================== 文档检查 ====================

check_documents() {
    log "========== 阶段 0: 文档检查 =========="
    
    if [ ! -f "$SPEC_FILE" ]; then
        error "SPEC.md 不存在!"
        exit 1
    fi
    
    if [ ! -f "$PLAN_FILE" ]; then
        error "PLAN.md 不存在!"
        exit 1
    fi
    
    success "文档检查通过"
    info "SPEC.md: $(wc -l < "$SPEC_FILE") 行"
    info "PLAN.md: $(wc -l < "$PLAN_FILE") 行"
}

# ==================== 从 PLAN 获取任务 ====================

get_next_task_from_plan() {
    local task_info=$(grep "|.*⏳ 待开始" "$PLAN_FILE" | head -1)
    
    if [ -z "$task_info" ]; then
        echo "NO_TASK"
        return
    fi
    
    local task_name=$(echo "$task_info" | awk -F '|' '{print $3}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    local priority=$(echo "$task_info" | awk -F '|' '{print $2}' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    
    echo "${priority}:${task_name}"
}

# ==================== 更新 PLAN 状态 ====================

update_plan_status() {
    local task_name="$1"
    local new_status="$2"
    local actual_time="${3:-}"
    
    log "更新 PLAN.md: $task_name → $new_status"
    
    local tmp_file=$(mktemp)
    
    # 使用 awk 安全地替换状态
    awk -F '|' -v task="$task_name" -v status="$new_status" -v time="$actual_time" '
    BEGIN { OFS="|" }
    {
        if (match($0, "\\|[^\\|]*\\|[^\\|]*" task "[^\\|]*\\|[^\\|]*⏳ 待开始")) {
            gsub(/⏳ 待开始/, status, $0)
            if (time != "") {
                $6 = " " time " "
            }
        }
        print $0
    }' "$PLAN_FILE" > "$tmp_file"
    
    mv "$tmp_file" "$PLAN_FILE"
    success "PLAN.md 已更新"
    
    # Git 提交
    if ! git diff --quiet "$PLAN_FILE" 2>/dev/null; then
        git add "$PLAN_FILE"
        git commit -m "Docs: 更新 PLAN 进度 - $task_name $new_status" || true
        git push origin main 2>/dev/null || true
    fi
}

# ==================== 检查 PLAN 完成状态 ====================

check_plan_completion() {
    local pending_count=$(grep -c "⏳ 待开始" "$PLAN_FILE" || echo "0")
    
    if [ "$pending_count" -eq 0 ]; then
        echo "COMPLETE"
    else
        echo "PENDING:$pending_count"
    fi
}

# ==================== 阶段 1: 任务分析 ====================

phase_1_analyze() {
    local task_name="$1"
    
    log "========== 阶段 1: 任务分析 =========="
    info "任务: $task_name"
    
    # 标记为进行中
    local tmp_file=$(mktemp)
    awk -F '|' -v task="$task_name" '
    BEGIN { OFS="|" }
    {
        if (match($0, "\\|[^\\|]*\\|[^\\|]*" task "[^\\|]*\\|[^\\|]*⏳ 待开始")) {
            gsub(/⏳ 待开始/, "🔄 进行中", $0)
        }
        print $0
    }' "$PLAN_FILE" > "$tmp_file"
    mv "$tmp_file" "$PLAN_FILE"
    
    info "读取技术规范..."
    success "任务分析完成"
}

# ==================== 阶段 2-5: 执行 OpenCode ====================

phase_2_to_5_execute() {
    local task_name="$1"
    local start_time=$(date +%s)
    
    log "========== 阶段 2-5: 执行任务 =========="
    info "调用 OpenCode 执行任务: $task_name"
    
    # 创建提示词文件 - 使用简单 ASCII 字符避免编码问题
    local prompt_file=$(mktemp)
    cat > "$prompt_file" << PROMPT_EOF
Task: TASK_NAME_PLACEHOLDER

Project: PROJECT_DIR_PLACEHOLDER

Requirements:
1. Read SPEC.md for technical specifications
2. Read PLAN.md for task planning
3. Implement code following SPEC chapter 3 (data model) and chapter 4 (interfaces)
4. Run pytest tests to verify
5. Update SPEC.md if architecture changes
6. Git commit with format: "Feat: task name"
7. Update PLAN.md to mark task as completed ONLY after real completion

Important: You must ACTUALLY write code files and verify they work. Do NOT return success without real implementation.

Start working on this task now.
PROMPT_EOF
    
    # 替换变量
    sed -i "s/TASK_NAME_PLACEHOLDER/$task_name/g" "$prompt_file"
    sed -i "s|PROJECT_DIR_PLACEHOLDER|$PROJECT_DIR|g" "$prompt_file"
    
    # 执行 OpenCode
    local output_file=$(mktemp)
    
    # 使用 timeout 防止卡住
    if ! timeout 300 opencode run "$prompt_file" > "$output_file" 2>&1; then
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            error "OpenCode 执行超时（5分钟）"
        else
            error "OpenCode 执行失败 (exit: $exit_code)"
        fi
        cat "$output_file" | tail -30 >> "$LOG_FILE"
        rm -f "$prompt_file" "$output_file"
        return 1
    fi
    
    # 记录输出
    cat "$output_file" >> "$LOG_FILE"
    
    # 检查是否实际创建了文件
    local new_files=$(find "$PROJECT_DIR" -name "*.py" -newer "$prompt_file" 2>/dev/null | wc -l)
    
    rm -f "$prompt_file" "$output_file"
    
    # 验证：必须实际创建了新文件
    if [ "$new_files" -lt 1 ]; then
        error "OpenCode 未实际创建文件 (new files: $new_files)"
        return 1
    fi
    
    success "OpenCode 执行成功，创建 $new_files 个新文件"
    
    local end_time=$(date +%s)
    local duration=$(( (end_time - start_time) / 60 ))
    
    echo "$duration"
}

# ==================== 阶段 6: 更新 PLAN ====================

phase_6_update_plan() {
    local task_name="$1"
    local duration="$2"
    
    log "========== 阶段 6: 更新 PLAN =========="
    
    update_plan_status "$task_name" "✅ 已完成" "${duration}m"
    
    success "PLAN 更新完成"
}

# ==================== 主循环 ====================

main_loop() {
    log "======================================"
    log "文档驱动的 BabyAGI 执行器 v2.2 启动"
    log "======================================"
    
    check_documents
    
    local iteration=0
    local max_iterations="${MAX_ITERATIONS:-50}"
    
    while [ $iteration -lt $max_iterations ]; do
        iteration=$((iteration + 1))
        
        log ""
        log "╔════════════════════════════════════════════════╗"
        log "║  第 $iteration 轮执行                          ║"
        log "╚════════════════════════════════════════════════╝"
        
        # 检查完成状态
        local plan_status=$(check_plan_completion)
        
        if [ "$plan_status" = "COMPLETE" ]; then
            log ""
            success "🎉 PLAN 中所有任务已完成!"
            success "执行器正常退出"
            exit 0
        fi
        
        local remaining=$(echo "$plan_status" | cut -d':' -f2)
        info "剩余任务数: $remaining"
        
        # 获取下一个任务
        local task_info=$(get_next_task_from_plan)
        
        if [ "$task_info" = "NO_TASK" ]; then
            warn "没有待开始的任务"
            sleep 10
            continue
        fi
        
        local priority=$(echo "$task_info" | cut -d':' -f1)
        local task_name=$(echo "$task_info" | cut -d':' -f2-)
        
        info "获取到任务: [$priority] $task_name"
        
        # 执行六阶段流程
        phase_1_analyze "$task_name"
        
        local duration
        if duration=$(phase_2_to_5_execute "$task_name"); then
            phase_6_update_plan "$task_name" "$duration"
        else
            error "任务执行失败: $task_name"
            # 标记为失败，避免无限重试
            update_plan_status "$task_name" "❌ 失败" "0m"
        fi
        
        # 轮询间隔
        log "等待 10 秒后继续下一轮..."
        sleep 10
    done
    
    warn "达到最大迭代次数 ($max_iterations)，执行器退出"
}

# ==================== 信号处理 ====================

cleanup() {
    log "执行器收到退出信号，正在清理..."
    rm -f "$LOCK_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# ==================== 入口 ====================

# 检查锁文件
if [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$LOCK_FILE")
    if ps -p "$pid" > /dev/null 2>&1; then
        error "执行器已在运行 (PID: $pid)"
        exit 1
    fi
fi

echo $$ > "$LOCK_FILE"

# 主循环
main_loop

# 清理
rm -f "$LOCK_FILE"
