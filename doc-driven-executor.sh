#!/bin/bash
# 文档驱动的 BabyAGI 执行器
# 遵循 AGENTS.md v2.0 规范：SPEC + PLAN 双文档驱动

set -e

# ==================== 配置 ====================
PROJECT_DIR="/root/.openclaw/workspace/test/todo-manager"
SPEC_FILE="$PROJECT_DIR/SPEC.md"
PLAN_FILE="$PROJECT_DIR/PLAN.md"
TASKS_FILE="$PROJECT_DIR/tasks.json"
LOG_FILE="$PROJECT_DIR/logs/executor.log"
LOCK_FILE="/tmp/doc-driven-executor.lock"

cd "$PROJECT_DIR"

# 确保日志目录存在
mkdir -p "$PROJECT_DIR/logs"

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
        error "SPEC.md 不存在! 请确保技术规范文档已创建"
        exit 1
    fi
    
    if [ ! -f "$PLAN_FILE" ]; then
        error "PLAN.md 不存在! 请确保项目计划文档已创建"
        exit 1
    fi
    
    success "文档检查通过"
    info "SPEC.md: $(wc -l < "$SPEC_FILE") 行"
    info "PLAN.md: $(wc -l < "$PLAN_FILE") 行"
}

# ==================== 从 tasks.json 同步任务到 PLAN ====================

sync_tasks_to_plan() {
    log "检查 tasks.json 中的遗留任务..."
    
    if [ ! -f "$TASKS_FILE" ]; then
        info "tasks.json 不存在，跳过同步"
        return
    fi
    
    # 获取未完成的非测试任务
    local pending_tasks=$(python3 << EOF
import json
import sys

try:
    with open('$TASKS_FILE', 'r') as f:
        tasks = json.load(f)
    
    pending = []
    for t in tasks:
        if not t.get('done', False) and not t.get('is_test', False):
            # 过滤掉测试任务和无效内容
            content = t.get('content', '').strip()
            if content and len(content) > 2:
                # 排除明显是测试或无效的任务
                invalid_prefixes = ['测试任务_', 'test_', '根据分析', '我需要', '**', '1.', '2.', '3.']
                if not any(content.startswith(p) for p in invalid_prefixes):
                    pending.append(content)
    
    for task in pending[:20]:  # 最多同步20个
        print(task)
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(0)
EOF
)
    
    if [ -z "$pending_tasks" ]; then
        info "tasks.json 中没有需要同步的有效任务"
        return
    fi
    
    info "发现 tasks.json 中的遗留任务，同步到 PLAN.md"
    
    # 将任务添加到 PLAN.md
    local tmp_file=$(mktemp)
    local inserted=false
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^\|.*任务.*\|.*状态.*\| ]] && [ "$inserted" = false ]; then
            # 找到任务表格头部，在下面插入任务
            echo "$line" >> "$tmp_file"
            # 输出分隔行
            IFS= read -r sep_line
            echo "$sep_line" >> "$tmp_file"
            # 插入 tasks.json 的任务
            echo "$pending_tasks" | while IFS= read -r task_content; do
                if [ -n "$task_content" ]; then
                    echo "| 🟡 中 | $task_content | ⏳ 待开始 | AI | 2h | |" >> "$tmp_file"
                fi
            done
            inserted=true
        else
            echo "$line" >> "$tmp_file"
        fi
    done < "$PLAN_FILE"
    
    mv "$tmp_file" "$PLAN_FILE"
    success "已同步 $(echo "$pending_tasks" | wc -l) 个任务到 PLAN.md"
    
    # Git 提交
    git add "$PLAN_FILE"
    git commit -m "Docs: 从 tasks.json 同步遗留任务到 PLAN" || true
}

# ==================== 标记 tasks.json 任务完成 ====================

mark_task_json_done() {
    local task_content="$1"
    
    if [ ! -f "$TASKS_FILE" ]; then
        return
    fi
    
    python3 << EOF
import json
import sys

try:
    with open('$TASKS_FILE', 'r') as f:
        tasks = json.load(f)
    
    updated = False
    for t in tasks:
        if t.get('content') == '$task_content' and not t.get('done'):
            t['done'] = True
            from datetime import datetime
            t['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True
            break
    
    if updated:
        with open('$TASKS_FILE', 'w') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        print(f"✅ tasks.json 中标记完成: {task_content[:50]}")
except Exception as e:
    print(f"警告: 更新 tasks.json 失败: {e}", file=sys.stderr)
EOF
}
    # 解析 PLAN.md 获取第一个 ⏳ 待开始的任务
    local task_info=$(grep "|.*⏳ 待开始" "$PLAN_FILE" | head -1)
    
    if [ -z "$task_info" ]; then
        echo "NO_TASK"
        return
    fi
    
    # 提取任务名称（第3列）
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
    
    # 创建临时文件
    local tmp_file=$(mktemp)
    
    # 读取并修改 PLAN.md
    awk -F '|' '
    BEGIN { OFS="|" }
    {
        if ($0 ~ /\|.*\|.*'$task_name'.*\|.*⏳ 待开始/) {
            # 替换状态
            gsub(/⏳ 待开始/, "'$new_status'", $0)
            # 如提供了实际工时，更新第6列
            if ("'$actual_time'" != "") {
                $6 = " '$actual_time' "
            }
        }
        print $0
    }' "$PLAN_FILE" > "$tmp_file"
    
    mv "$tmp_file" "$PLAN_FILE"
    
    success "PLAN.md 已更新"
    
    # Git 提交 PLAN 更新
    if git diff --quiet "$PLAN_FILE" 2>/dev/null; then
        return
    fi
    
    git add "$PLAN_FILE"
    git commit -m "Docs: 更新 PLAN 进度 - $task_name $new_status" || true
    git push origin main 2>/dev/null || true
}

# ==================== 检查 PLAN 是否完成 ====================

check_plan_completion() {
    local pending_count=$(grep -c "⏳ 待开始" "$PLAN_FILE" || echo "0")
    local in_progress_count=$(grep -c "🔄 进行中" "$PLAN_FILE" || echo "0")
    
    if [ "$pending_count" -eq 0 ] && [ "$in_progress_count" -eq 0 ]; then
        echo "COMPLETE"
    else
        echo "PENDING:$((pending_count + in_progress_count))"
    fi
}

# ==================== 从 SPEC 获取规范 ====================

get_spec_section() {
    local section="$1"
    log "读取 SPEC.md: $section"
    # 这里可以实现 SPEC 章节解析
    # 简单实现：显示相关行
    grep -A 10 "$section" "$SPEC_FILE" | head -15 || echo "章节未找到"
}

# ==================== 阶段 1: 任务分析 ====================

phase_1_analyze() {
    local task_name="$1"
    
    log "========== 阶段 1: 任务分析 =========="
    info "任务: $task_name"
    
    # 在 PLAN 中标记为进行中
    sed -i "s/|.*$task_name.*|.*⏳ 待开始/| $task_name | 🔄 进行中/" "$PLAN_FILE"
    
    # 读取相关 SPEC 章节
    info "读取技术规范..."
    
    success "任务分析完成"
}

# ==================== 阶段 2-5: 调用 OpenCode ====================

phase_2_to_5_execute() {
    local task_name="$1"
    local start_time=$(date +%s)
    
    log "========== 阶段 2-5: 执行任务 =========="
    info "调用 OpenCode 执行任务: $task_name"
    
    # 构建提示词，包含 SPEC 和 PLAN 引用
    local prompt="你是一个专业的 Python 开发者。请完成以下任务：

【任务】$task_name

【项目信息】
- 项目路径: $PROJECT_DIR
- 这是一个 Python CLI Todo 管理器
- 主程序: todo.py
- 任务存储: tasks.json

【必须遵循的规范】
1. 实现必须符合 SPEC.md 中的技术规范
2. 接口必须符合 SPEC.md 第4章定义
3. 数据模型必须符合 SPEC.md 第3章定义
4. 参考 AGENTS.md 工作流程

【工作规范】(参考 AGENTS.md)
1. 阶段 0: 阅读 SPEC.md 和 PLAN.md
2. 阶段 1: 分析任务需求，确定实现方案
3. 阶段 2: 编写/修改代码，遵循 SPEC 规范
4. 阶段 3: 添加必要的测试，运行 pytest
5. 阶段 4: 如架构变更，更新 SPEC.md
6. 阶段 5: Git 提交，格式: \"Feat: $task_name\"
7. 阶段 6: 更新 PLAN.md 标记任务完成

【输出要求】
1. 完成代码编写
2. 报告完成的功能
3. 列出修改的文件
4. 说明如何测试
5. 确认 SPEC 和 PLAN 已更新

请开始执行任务。"

    # 执行 OpenCode
    if ! echo "$prompt" | opencode run --stdin; then
        error "OpenCode 执行失败"
        return 1
    fi
    
    local end_time=$(date +%s)
    local duration=$(( (end_time - start_time) / 60 ))
    
    success "任务执行完成，耗时 ${duration} 分钟"
    echo "$duration"
}

# ==================== 阶段 6: 更新 PLAN ====================

phase_6_update_plan() {
    local task_name="$1"
    local duration="$2"
    
    log "========== 阶段 6: 更新 PLAN =========="
    
    # 检查 PLAN 是否已被更新
    if grep -q "$task_name.*✅ 已完成" "$PLAN_FILE"; then
        success "PLAN 已标记为完成"
    else
        # 更新 PLAN
        update_plan_status "$task_name" "✅ 已完成" "${duration}m"
        success "PLAN 更新完成"
    fi
    
    # 同时更新 tasks.json（如果存在该任务）
    mark_task_json_done "$task_name"
}

# ==================== 主循环 ====================

main_loop() {
    log "======================================"
    log "文档驱动的 BabyAGI 执行器启动"
    log "======================================"
    
    # 检查文档
    check_documents
    
    # 同步 tasks.json 中的遗留任务到 PLAN
    sync_tasks_to_plan
    
    local iteration=0
    local max_iterations="${MAX_ITERATIONS:-100}"
    
    while [ $iteration -lt $max_iterations ]; do
        iteration=$((iteration + 1))
        
        log ""
        log "╔════════════════════════════════════════════════╗"
        log "║  第 $iteration 轮执行                          ║"
        log "╚════════════════════════════════════════════════╝"
        
        # 检查 PLAN 完成状态
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
            warn "没有待开始的任务，但 PLAN 未完成"
            warn "可能存在进行中的任务或状态异常"
            info "5秒后重试..."
            sleep 5
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
            # 标记为失败
            sed -i "s/|.*$task_name.*|.*🔄 进行中/| $task_name | ❌ 失败/" "$PLAN_FILE"
        fi
        
        # 轮询间隔
        log "等待 5 秒后继续下一轮..."
        sleep 5
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
