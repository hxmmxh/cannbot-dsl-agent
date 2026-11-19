# cannbot-dsl-agent

## 默认开发约定

- 本工作区的算子开发默认使用 CANNBot DSL；用户明确指定语言、芯片或工程时，以用户要求为准。
- 开发与编译前使用 `cannbot-dsl-env-check` 检查任务所选 Python/CANN 和设备环境，获取芯片身份、软件版本及可用能力，复用仍有效的检查结果。用户指定的编译或部署目标优先；无法识别时保留未知，只在影响实现或验证时确认必要缺项。安装时不预设芯片型号。
- Python/CANN 环境复用根目录 `env.sh` 和 `.venv`，在工作区根目录执行 `source env.sh`。不要因插件安装而替换已有的 uv 环境或依赖锁定文件。
- 算子源码和样例默认放在 `op_demo/`，生成日志、缓存与验证结果放在 `build/` 或工作流规定的 `.cannbot/` 目录。

## 按任务选择能力

- 主会话的 DSL 算子开发、修复与交付优先使用自己的 `cannbot-dsl-dev` 入口。简单 demo、小用例和局部修复使用本地直接开发流程；需要完整编排、独立验收、复杂协作或性能调优时，转到原版 `ops-direct-invoke` 并遵循其流程。用户明确选择的入口优先。性能工作区由 `.cannbot/ops-direct-invoke.json` 的 `performance_root` 和 `performance_registry` 定位。
- 单项环境检查、方案设计、实现任务拆分、测试生成、实现最佳实践、代码检视，分别使用对应的 `cannbot-dsl-*` Skill。
- 生成或校验规格使用 `ops-spec-gen`；查询算法范式使用 `ops-design-paradigms`；查询目标芯片能力使用 `npu-arch`。
- 性能采集与报告分析使用 `ops-profiling`；只有明确要求优化具体程序时才进入完整性能调优工作流。
- `msprof application` 已运行但 summary 缺失或 Host/Device 关联不完整时，补充使用本地 `msprof-application-troubleshooting` Skill，保留上游采样与数据校验协议。
- 精度标准使用 `ops-precision-standard`；DSL 文档自检与文档 PR 检视使用 `cannbotdsl-doc-reviewer`。
- Skill 从 `.agents/skills/` 发现，按当前任务读取所需正文与引用，不在每次会话中预读所有 Skill。

## 本地事实来源

- DSL 文档与样例：`third_party/cannbot-dsl/docs/`、`third_party/cannbot-dsl/samples/`。
- 插件与编排源码：`third_party/cannbot/`。
- 原子 Skill 源码：`third_party/cannbot-skills/ops/`。
- 自维护 Skill：`skills/`，包括开发入口 `cannbot-dsl-dev` 和采集排查能力 `msprof-application-troubleshooting`。运行 `bash install.sh` 注册本地 Skill 并安装原版工作流。
- 配置、复现与维护说明：`docs/插件与skill配置.md`。

`third_party/` 下三个上游仓库通过 submodule 固定版本，源文件和安装资源均保持原样。算子放在 `op_demo/`，个人行为定制放在 `skills/`，通过独立入口的条件路由选择能力。升级上游后重新安装并验证兼容性；不覆盖上游入口、模板、任务文件或其安装副本。

配置及链接存在不代表环境、编译、精度或性能验证已经通过。报告应区分实际执行的检查与尚未验证的能力。
