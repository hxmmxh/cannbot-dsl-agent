# Python/CANN 环境

环境重建步骤见 [仓库说明](../README.md#重建算子-pythoncann-环境)。

`uv.lock` 复现原机 Linux aarch64 / Python 3.12 的 Python 包；宿主机提供 CANN、驱动和芯片算子包。先 `uv sync --locked` 创建 `.venv`，再指定 `CANNBOT_CANN_ROOT` 并在工作区根目录执行 `source env.sh`。不同平台应先调整依赖声明和锁文件。

安装 Skill 或检查链接不等于通过设备环境验证。实际设备任务前，使用 `cannbot-dsl-env-check` 检查目标机器，再运行对应算子的编译及精度用例。
