---
name: msprof-application-troubleshooting
description: 排查 msprof application 已执行目标程序但 op_summary 缺失、Host/Device 任务关联不完整的问题；使用短 shell 启动和版本适配验证，并保持原性能采样与数据校验协议。
metadata:
  required_skills:
    - ops-profiling
---

# msprof application 采集排查

这是项目维护的性能采集补充能力。遇到目标确实运行、但 summary 缺失或原始任务关联不完整时使用；常规采集继续使用已安装的 `ops-profiling`。

1. 读取当前 `ops-profiling` 的 `references/application_runner_contract.md`，保留其采样、runner、manifest 和数据校验协议。
2. 读取 [关联缺失排查与短 shell 启动](references/msprof-application-troubleshooting.md)。先区分导出失败和原始关联记录缺失，再按实际日志选择处理方式。
3. 需要调整启动方式时，在当前任务目录创建短 shell 或参数适配器，保留原解释器、设备映射、实际叶 runner 和五个动态参数。针对当前工具版本验证选项。
4. 先以代表性小例确认修复，再在新目录完成正式采集并运行原校验器。退出码、命令长度和另一条采集路径成功都不能替代数据验收。

原参考中记录的环境、参数组合与样本数量来自 2026-11-13 的一次验证；适配其他版本时以当前证据为准。这里不增加固定重试次数或新的通用阈值。

定制维护在本 Skill、任务脚本或父仓库的其他 Skill 中，保持三方库及其安装资源原样。隔离工作流节点需要此能力时，显式绑定 `msprof-application-troubleshooting`；其 `required_skills` 会补齐 `ops-profiling` 依赖。
