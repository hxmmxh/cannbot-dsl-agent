# msprof application 关联缺失：短 shell 启动

适用于目标确实执行、但 `op_summary` 缺失或 Host/Device 任务无法完整关联的 `msprof application` 采集。这里记录的是已验证的启动规避方法，不是对 msprof 二进制的修复；`msprof op` 流水图采集成功也不能证明 application 链路正常。

## 先区分导出失败与原始数据缺失

保留失败采集的命令、退出码、工具日志和原始 PROF。检查原始数据中的 `RuntimeHostTask`、`COMPUTE_TASK_INFO`、`task_track`、`stream_sq` 等记录及关联；名称和格式随工具版本变化，按当前数据库 schema 与日志判断。

原始记录完整时可尝试当前工具支持的重新导出；原始关联本身缺失时，重新导出不能补回数据。不得根据预期发射顺序给无名任务补名、填时间或强行生成通过的拓扑。会话容量、不完整 CANN 安装等其他问题见当前已安装 `ops-profiling` 的 `references/application_runner_contract.md`。

## 已验证范围

2026-11-13 在 Ascend950DT_9581、物理卡 4 / 逻辑 `npu:0`、CANN 9.2.1、CANNBotDSL 0.8.2 上验证了以下组合，未升级环境或修改目标实现：

- 外层 application 仅启动一个短路径 shell，传五个动态值；固定的长路径和参数留在 shell 内。
- shell 用独立 argv 和 `exec` 启动原环境入口与原叶 runner；不再增加额外的 Python“记录环境后 exec”包装层。
- 当前工具验证支持的 msprof 参数为：

  ```text
  --aic-mode=task-based --task-time=l2 --aic-metrics=PipeUtilization
  --runtime-api=on --ge-api=l1 --ai-core=on
  ```

仅改 `task-time=l2` 或仅移除额外 Python 包装层的探针仍曾失败；原环境 wrapper 同时用于成功与失败采集，不能据此认定 `source env.sh` 是原因。实测支持上述组合规避问题，尚未确认唯一底层根因或新的固定命令长度阈值。已有命令长度检查通过也不保证关联完整；不要把某次成功长度当作通用上限。

## 短 shell 使用方法

在本次任务目录保存 `profile_app.sh`。下面以已有 Python runner 为例；把固定路径替换为当前工程的真实路径，`task_python` 使用原来已经验证的解释器或环境 wrapper。`--cases` 是本例叶 runner 的固定参数，其他 adapter 参数也按实际接口放在 shell 内，不向通用 runner 发明新参数。

```bash
#!/usr/bin/env bash
set -euo pipefail
task_project=/path/to/project
task_python="$task_project/.venv/bin/python"
task_case_ids=${1:?case_ids}
task_samples=${2:?samples}
task_execution_manifest=${3:?execution_manifest}
task_warmup_mode=${4:?warmup_mode}
task_warmup_op=${5:?warmup_op}
task_fixed_args=(--cases "$task_project/cases.csv")
exec "$task_python" "$task_project/run_cases.py" \
    "${task_fixed_args[@]}" \
    --case-ids "$task_case_ids" --samples "$task_samples" \
    --execution-manifest "$task_execution_manifest" \
    --warmup-mode "$task_warmup_mode" --warmup-op "$task_warmup_op"
```

在原 `collect_perf_application.py` 调用中，保留其他已确认参数，替换 application 模板为：

```bash
--runner-file /path/to/project/run_cases.py \
--application-cmd 'bash /path/to/project/profile_app.sh "{case_ids}" "{samples}" "{execution_manifest}" "{warmup_mode}" "{warmup_op}"'
```

`--runner-file` 仍指向实际叶 runner，不改成 shell。五个占位符必须保留，使用采集器传入的真实 manifest 路径；禁止 `eval`。shell、固定参数及其 SHA 随执行身份归档。保留原设备映射与 profiler 注入环境，不为缩短命令另换 Python/CANN 或重写环境入口。

**采集参数适配位置**：当前采集器的 `--host-metadata-capture on` 产生 `task-time=on / runtime-api=on / ge-api=l1`，没有设置 `task-time=l2` 的公开命令行选项。本次验证由任务内兼容适配器将实际 msprof 参数中的 `--task-time=on` 替换为 `--task-time=l2`，并补上 `--ai-core=on`；规划、解析、统计和校验器保持原样。需要相同适配时，先保存当前工具 help/version 支持证据，再在任务目录实现并归档适配器与最终命令；参数变换应可重复执行且不累加重复项，以支持多会话。不要向采集器传不存在的 `--task-time` 参数，也不要覆盖工作流已冻结的采集器或历史产物。其他版本按实际能力验证，不默认套用此参数组合。

## 修复后验证与正式采集

1. 先用代表性小例验证原始任务和关联链完整，再在新目录冻结正式计划并执行完整 case 集；诊断结果不作为正式基线。保留失败 attempt，不覆盖历史记录，也不为择优重复成功采集。
2. 保持原叶 runner、输入/seed、warmup、采样数、目标实现、缓存和已验证身份。编译、加载与身份检查放在正式样本外；有设备 prime 时按契约声明 `preparation_kernel_sequence`。不要在计时目标内增加 hash、maps 扫描或 observer。
3. 每例仍为 10 组相邻 `warmup → synchronize → 完整 target → synchronize`。每组先汇总完整 target 的全部计算 kernel Task Duration，再对十个和值取中位数；不丢样本、不按 kernel 取最佳值。公开入口同步耗时另报，不能替代设备耗时或相减推断 Host 占比。
4. 运行原 canonical 校验器，核对 `expected == parsed == mapped`、每例 10 组、身份/频率/波动门禁。若原始关联曾缺失，另核对 CSV 计算记录、数据库计算任务和唯一 Host 关联数量一致，逐项保留并说明其他任务。Host memcpy API 耗时不能冒充设备 Task Duration；Event 等非计算任务单独归档，不能把真实辅助计算 kernel 当杂项删掉。
5. 每个 candidate/teacher 重新确认实际完整任务序列及对应 identity/topology。适配 shell 内若有固定实现入口，显式改为当前候选并重新冻结，避免仍测原基线。启动次数改变后不能沿用旧计数。

上述环境中，小例诊断的 820 条计算记录通过后，新正式采集的 4 例 × 10 组也通过原门禁及原始数据审阅：CSV、数据库计算记录与唯一 Host 关联均为 54,490，频率均为 1650 MHz，最大波动约 0.8782%。这些数字仅说明该次验证有效，不是通用拓扑、容量或频率要求；不据此提高其他环境的默认会话上限或跳过自动拆分。使用方法变更后仍以当前完整采集证据为准。
