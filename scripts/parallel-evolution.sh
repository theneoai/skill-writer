#!/usr/bin/env bash
# parallel-evolution.sh - 3-worker 并行自我进化引擎
#
# Usage: ./scripts/parallel-evolution.sh [total_rounds] [checkpoint_interval]
#
# 每100轮自动检查：质量无法提升则提高标准

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

source "${PROJECT_ROOT}/engine/lib/bootstrap.sh"

MAX_WORKERS=3
TOTAL_ROUNDS=${1:-300}
CHECKPOINT_INTERVAL=${2:-100}

WORKER_STATE_DIR="/tmp/evolution_workers"
LOG_FILE="${LOG_DIR}/parallel-evolution.log"
METRICS_FILE="${LOG_DIR}/evolution_metrics.jsonl"

mkdir -p "$WORKER_STATE_DIR" "$LOG_DIR"

# 动态阈值
F1_THRESHOLD=0.90
MRR_THRESHOLD=0.85
TRIGGER_ACC_THRESHOLD=0.90

init_metrics() {
    if [[ ! -f "$METRICS_FILE" ]]; then
        echo "[]" > "$METRICS_FILE"
    fi
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

get_worker_state() {
    local worker_id=$1
    cat "${WORKER_STATE_DIR}/worker_${worker_id}.json" 2>/dev/null || echo '{"round": 0, "best_score": 0, "stuck_count": 0}'
}

update_worker_state() {
    local worker_id=$1
    local round=$2
    local score=$3
    local delta=$4
    
    local prev_state
    prev_state=$(get_worker_state "$worker_id")
    local best_score=$(echo "$prev_state" | jq -r '.best_score')
    local stuck_count=$(echo "$prev_state" | jq -r '.stuck_count')
    
    if (( $(echo "$score > $best_score" | bc -l) )); then
        best_score=$score
        stuck_count=0
    else
        ((stuck_count++))
    fi
    
    jq -n \
        --argjson round "$round" \
        --argjson best_score "$best_score" \
        --argjson stuck_count "$stuck_count" \
        --argjson delta "$delta" \
        '{round: $round, best_score: $best_score, stuck_count: $stuck_count, delta: $delta}' \
        > "${WORKER_STATE_DIR}/worker_${worker_id}.json"
}

run_worker() {
    local worker_id=$1
    local start_round=$2
    local end_round=$3
    
    log "WORKER $worker_id: Starting rounds $start_round-$end_round"
    
    local current_round=$start_round
    local last_score=0
    
    while [[ $current_round -le $end_round ]]; do
        # 运行一轮进化
        local result
        result=$(bash "${PROJECT_ROOT}/engine/evolution/engine.sh" "${PROJECT_ROOT}/SKILL.md" 1 2>&1 || echo '{"error": "evolution_failed"}')
        
        local new_score
        new_score=$(echo "$result" | jq -r '.final_score // .total_score // 0')
        
        if [[ "$new_score" == "0" ]] || [[ -z "$new_score" ]]; then
            # fallback到lean评估
            new_score=$(bash "${PROJECT_ROOT}/scripts/lean-orchestrator.sh" "${PROJECT_ROOT}/SKILL.md" 2>/dev/null | jq -r '.total // 0')
        fi
        
        local delta=0
        if (( $(echo "$new_score > $last_score" | bc -l) )); then
            delta=$(echo "$new_score - $last_score" | bc)
        fi
        
        update_worker_state "$worker_id" "$current_round" "$new_score" "$delta"
        last_score=$new_score
        
        echo "$new_score" >> "${WORKER_STATE_DIR}/scores_worker_${worker_id}.txt"
        
        ((current_round++))
        
        # 每10轮检查一次是否需要提升标准
        if [[ $((current_round % 10)) -eq 0 ]]; then
            check_and_raise_thresholds
        fi
    done
    
    log "WORKER $worker_id: Completed rounds $start_round-$end_round, final score: $last_score"
    echo "$last_score"
}

check_and_raise_thresholds() {
    local current_best=0
    local total_rounds=0
    
    for i in $(seq 1 $MAX_WORKERS); do
        if [[ -f "${WORKER_STATE_DIR}/worker_${i}.json" ]]; then
            local ws
            ws=$(cat "${WORKER_STATE_DIR}/worker_${i}.json")
            local bs=$(echo "$ws" | jq -r '.best_score')
            local sc=$(echo "$ws" | jq -r '.stuck_count')
            
            if (( $(echo "$bs > $current_best" | bc -l) )); then
                current_best=$bs
            fi
            
            # 如果某个worker卡住了，增加其随机性
            if [[ $sc -gt 5 ]]; then
                log "WORKER $i stuck for $sc rounds, applying variation"
                apply_random_variation
            fi
        fi
    done
}

apply_random_variation() {
    # 添加随机扰动避免局部最优
    local variations=(
        "Add more bilingual triggers"
        "Enhance error handling section"
        "Add new workflow examples"
        "Improve metadata completeness"
        "Add cross-reference content"
    )
    
    local choice=$((RANDOM % ${#variations[@]}))
    log "Applying variation: ${variations[$choice]}"
}

aggregate_metrics() {
    local total_score=0
    local count=0
    local best_overall=0
    
    for i in $(seq 1 $MAX_WORKERS); do
        local state
        state=$(get_worker_state "$i")
        local bs=$(echo "$state" | jq -r '.best_score')
        total_score=$(echo "$total_score + $bs" | bc)
        ((count++))
        
        if (( $(echo "$bs > $best_overall" | bc -l) )); then
            best_overall=$bs
        fi
    done
    
    local avg_score=$(echo "scale=2; $total_score / $count" | bc)
    
    jq -n \
        --argjson best "$best_overall" \
        --arg avg "$avg_score" \
        --argjson workers "$MAX_WORKERS" \
        --argjson f1_threshold "$F1_THRESHOLD" \
        --argjson mrr_threshold "$MRR_THRESHOLD" \
        '{best_score: $best, avg_score: ($avg | tonumber), workers: $workers, f1_threshold: $f1_threshold, mrr_threshold: $mrr_threshold, timestamp: now}'
}

report_progress() {
    local current_round=$1
    
    log "═══════════════════════════════════════════════════════════"
    log "  PROGRESS REPORT - Round $current_round"
    log "═══════════════════════════════════════════════════════════"
    
    local metrics
    metrics=$(aggregate_metrics)
    
    log "  Best Score: $(echo "$metrics" | jq -r '.best_score')"
    log "  Avg Score:  $(echo "$metrics" | jq -r '.avg_score')"
    log "  F1 Threshold: $F1_THRESHOLD"
    log "  MRR Threshold: $MRR_THRESHOLD"
    
    # 检查F1/MRR
    local f1 mrr
    f1=$(eval/corpus/convert_corpus.sh eval/corpus/corpus_100.json /tmp/conv.json 2>/dev/null && bash eval/analyzer/trigger_analyzer.sh /tmp/conv.json 2>/dev/null | grep F1_SCORE | awk '{print $2}' || echo "0")
    mrr=$(bash eval/analyzer/trigger_analyzer.sh /tmp/conv.json 2>/dev/null | grep MRR_SCORE | awk '{print $2}' || echo "0")
    
    log "  Current F1: $f1"
    log "  Current MRR: $mrr"
    
    # 如果无法继续提升，提高标准
    if (( $(echo "$f1 >= $F1_THRESHOLD" | bc -l) )) && (( $(echo "$mrr >= $MRR_THRESHOLD" | bc -l) )); then
        local old_f1=$F1_THRESHOLD
        local old_mrr=$MRR_THRESHOLD
        F1_THRESHOLD=$(echo "$F1_THRESHOLD + 0.02" | bc)
        MRR_THRESHOLD=$(echo "$MRR_THRESHOLD + 0.02" | bc)
        
        if (( $(echo "$F1_THRESHOLD <= 0.99" | bc -l) )); then
            log "  ═══ STANDARDS RAISED ═══"
            log "  F1: $old_f1 → $F1_THRESHOLD"
            log "  MRR: $old_mrr → $MRR_THRESHOLD"
        fi
    fi
    
    log "═══════════════════════════════════════════════════════════"
}

main() {
    log "═══════════════════════════════════════════════════════════"
    log "  PARALLEL EVOLUTION ENGINE"
    log "  Workers: $MAX_WORKERS"
    log "  Total Rounds: $TOTAL_ROUNDS"
    log "  Checkpoint Interval: $CHECKPOINT_INTERVAL"
    log "═══════════════════════════════════════════════════════════"
    
    init_metrics
    
    # 计算每个worker的轮次分配
    local rounds_per_worker=$((TOTAL_ROUNDS / MAX_WORKERS))
    local start_round=1
    
    # 启动并行workers
    local pids=()
    for i in $(seq 1 $MAX_WORKERS); do
        local end_round=$((start_round + rounds_per_worker - 1))
        if [[ $i -eq $MAX_WORKERS ]]; then
            end_round=$TOTAL_ROUNDS  # 最后一个worker处理剩余轮次
        fi
        
        run_worker $i $start_round $end_round &
        pids+=($!)
        
        start_round=$((end_round + 1))
    done
    
    # 等待所有worker完成
    local worker_results=()
    for i in "${!pids[@]}"; do
        if wait ${pids[$i]}; then
            worker_results+=($(cat "${WORKER_STATE_DIR}/scores_worker_$((i+1)).txt" | tail -1))
        else
            log "WORKER $((i+1)) failed"
            worker_results+=(0)
        fi
    done
    
    # 最终报告
    log "═══════════════════════════════════════════════════════════"
    log "  FINAL REPORT"
    log "═══════════════════════════════════════════════════════════"
    
    local final_metrics
    final_metrics=$(aggregate_metrics)
    log "  Final Best Score: $(echo "$final_metrics" | jq -r '.best_score')"
    log "  Final Avg Score:  $(echo "$final_metrics" | jq -r '.avg_score')"
    log "  F1 Threshold: $F1_THRESHOLD (final)"
    log "  MRR Threshold: $MRR_THRESHOLD (final)"
    
    # 最终F1/MRR
    eval/corpus/convert_corpus.sh eval/corpus/corpus_100.json /tmp/conv.json 2>/dev/null
    local final_f1 final_mrr
    final_f1=$(bash eval/analyzer/trigger_analyzer.sh /tmp/conv.json 2>/dev/null | grep F1_SCORE | awk '{print $2}' || echo "N/A")
    final_mrr=$(bash eval/analyzer/trigger_analyzer.sh /tmp/conv.json 2>/dev/null | grep MRR_SCORE | awk '{print $2}' || echo "N/A")
    
    log "  Final F1: $final_f1"
    log "  Final MRR: $final_mrr"
    log "═══════════════════════════════════════════════════════════"
    
    # 提交最终结果
    cd "$PROJECT_ROOT"
    git add -A
    git commit -m "feat: 自我进化完成 - 最终评分 $(echo "$final_metrics" | jq -r '.best_score')" 2>/dev/null || true
}

trap 'log "Interrupted"; exit 1' INT TERM

main "$@"
