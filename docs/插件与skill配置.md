# 插件与 Skill 配置

安装和调用步骤见 [仓库说明](../README.md)。

- 安装脚本内置 `ascend` / `common` / `dsl` / `confirm` 默认值，无需维护初始化配置文件。
- 芯片在安装时记为 `unknown`；开发前由 `cannbot-dsl-env-check` 获取任务环境中的芯片身份、CANN/DSL 版本与可用能力。任务明确指定的目标优先，探测不到时不推断型号。
- `.agents/skills/` 保存相对链接；12 个上游 Skill 来自 `third_party/`，2 个本地 Skill 来自 `skills/`。
- `bash install.sh` 自动生成 `.cannbot/init-config.json`，调用上游安装器，重新生成 `.cannbot/ops-direct-invoke.json`、`.cannbot/plugins/`、配套性能工作区及 `.codex/` 登记。安装阶段不运行设备或编译探针。
- 安装器直接调用 `third_party/cannbot` 中的原版初始化入口，`--skills` 指向干净的 `third_party/cannbot-skills` submodule。
- `cannbot-dsl-dev` 是自己的主会话入口：简单任务使用本地直接开发流程，需要完整编排或性能调优时调用原版 `ops-direct-invoke`。原版入口、模板、任务和安装资源均不替换。
- 性能采集排查经验维护在独立的 `msprof-application-troubleshooting` Skill 中。已有本地 Skill 的修改通过相对链接生效；新增注册项后重新安装。
- 安装记录中的源码提交号由上游安装器从对应 submodule 读取。检查脚本会确认工作流资源及四个上游入口直接引用原版目录。
- 完整安装还向主插件的外部 Skill 目录与性能工作区注册本地扩展；隔离节点需要时显式绑定该 Skill，其依赖仍为上游 `ops-profiling`。
- 安装脚本默认跳过额外参考仓库、知识索引和 OpModel。相关能力需按 `third_party/cannbot/plugins-official/ops-perf-optimize/` 中的安装说明单独补齐。

移动工作区后重新运行完整安装脚本刷新路径；只注册独立能力可执行 `bash install.sh --skills-only`。检查当前配置可执行 `python3 scripts/check_setup.py --full`。
