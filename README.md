# cannbot-dsl-agent

CANNBot DSL 算子开发 Agent，集成 Skills、开发与性能调优工作流，支持跨机器部署

## 新机器安装流程

开发环境和 Agent 能力分两步准备：先用 uv 创建 Python 环境，再用 `install.sh` 注册 Skill 和安装上游工作流。`install.sh` 不执行 uv 环境初始化，也不安装宿主机驱动或 CANN Toolkit。

### 准备宿主机和基础工具

准备 Bash、Git、uv、Node.js 20.11+ 和 tmux；实际使用 Agent 时需要 Codex。当前默认安装脚本会检查 Node.js、tmux，以及所用 Python 中的 PyYAML；下面的 uv 步骤会在项目环境中安装 PyYAML。

实际编译和上板验证前，宿主机还需提供匹配的昇腾驱动、CANN Toolkit 和芯片算子包。芯片型号由开发前的环境检查获取，无需填写配置文件。

### 获取源码和三个上游依赖

```bash
git clone git@github.com:hxmmxh/cannbot-dsl-agent.git
cd cannbot-dsl-agent
git submodule update --init
```

顶层三个 submodule 足够运行安装脚本。上游内部的其他子模块按任务需要再初始化。

### 重建算子 Python/CANN 环境

当前锁文件面向 Linux aarch64、Python 3.12.15，固定 CANNBot DSL 0.8.2、PyTorch 2.10.0+cpu 和 torch-npu 2.10.0.post7。其他平台需要调整依赖声明与锁文件。

在仓库根目录执行：

```bash
uv python install 3.12.15
uv sync --locked
```

Python 依赖安装在本仓库的 `.venv/`，包括 DSL、PyTorch、torch-npu、PyYAML 和 pytest。`pyproject.toml` 声明依赖，`uv.lock` 锁定版本，`.python-version` 指定 Python 版本；这些文件随 Git 保存，`.venv/` 在每台机器重新创建。

### 安装 Skill 和上游工作流

使用刚创建的项目 Python 运行安装器：

```bash
CANNBOT_PYTHON="$PWD/.venv/bin/python" bash install.sh
.venv/bin/python scripts/check_setup.py --full
```

默认命令会注册 14 个可单独调用的 Skill 入口，再调用原版 CANNBot 安装器，准备开发编排入口、角色、任务模板、工具脚本和配套性能工作区；主工作区最终有 18 个顶层入口。工作流在后续任务需要时调用。

安装默认使用 Ascend、CANNBot DSL 和通用工程，芯片暂记为未知。生成的配置和工作流资源保存在 `.cannbot/`、`.codex/`；默认跳过额外参考仓库、知识索引和 OpModel。安装入口和三方资源保持上游原版。

### 加载并检查实际开发环境

`env.sh` 默认从 `/usr/local/Ascend/cann-9.2.1` 加载 CANN；如果本机路径不同，先指定包含 `set_env.sh` 的实际目录。以下路径应按本机安装位置调整：

```bash
export CANNBOT_CANN_ROOT=/usr/local/Ascend/cann-9.2.1
source env.sh

PYTHON="$PWD/.venv/bin/python" \
  bash .agents/skills/cannbot-dsl-env-check/scripts/check_env.sh \
    --output-dir build/env-check
```

`source env.sh` 在当前终端加载 CANN 并激活项目 `.venv`；新终端使用开发环境时重新加载。

环境检查验证 DSL 导入、翻译、编译及 NPU 可用性，报告写入 `build/env-check/environment/environment.yaml`，设备选择结果写入同目录的 `env_selected_soc.yaml`。查看报告中的编译门禁和执行模式：`full` 表示可以进入上板验证，`compile_only` 表示当前只能编译。具体算子的精度和性能由后续测试验证。

### 在 Codex 中开始开发

在本仓库根目录打开 Codex，使用自己的开发入口：

```text
使用 cannbot-dsl-dev，复用 build/env-check 的环境检查结果，
开发一个 CANNBot DSL 算子并验证精度。
使用 msprof-application-troubleshooting 排查采集后缺少 op_summary 的问题。
```

## 安装命令的两种模式

这里的“独立 Skill”指可单独调用的能力，例如环境检查、代码检视和本地开发入口，包含 12 个上游 Skill 和 2 个自维护 Skill。注册入口是在项目 `.agents/skills/` 中建立或校验相对链接，让 Codex 发现对应的 `SKILL.md`。

| 命令 | 准备的内容 | 首次安装后的顶层入口 |
| --- | --- | --- |
| `bash install.sh` | 注册 14 个独立入口，并安装原版开发编排、角色、模板、工具脚本和性能工作区，生成项目配置 | 18 个 |
| `bash install.sh --skills-only` | 仅注册 14 个独立入口，跳过上游工作流安装和项目配置生成 | 14 个 |

如果只使用原子能力和自己的直接开发流程，可选择：

```bash
bash install.sh --skills-only
python3 scripts/check_setup.py
```

该模式需要 Python 3.10+ 和已取得的 submodule 源码，不要求 Node.js、tmux 或系统 Python 中的 PyYAML。运行 Skill 自带脚本时，仍需准备该能力实际使用的 Python/CANN 依赖。

任务需要原版完整编排时，再执行默认安装命令。已完成默认安装后运行 `--skills-only` 不会卸载已有工作流；它只是跳过本次的工作流安装步骤。两种模式均不创建 uv 环境。

## 目录与维护边界

```text
cannbot-dsl-agent/
├── third_party/             三个官方仓库的 submodule，固定提交
│   ├── cannbot/
│   ├── cannbot-skills/
│   └── cannbot-dsl/
├── skills/                  自维护入口和补充能力
│   ├── cannbot-dsl-dev/
│   └── msprof-application-troubleshooting/
├── .agents/skills/          14 个独立 Skill 的相对链接
├── scripts/                 安装与配置检查
├── docs/                    使用和维护说明
├── AGENTS.md                默认开发规则
└── install.sh
```

自己的开发入口维护在 `skills/cannbot-dsl-dev/`：小范围任务由主会话按本地直接开发流程实现、测试和自检，需要完整编排、独立验收或性能调优时调用原版 `ops-direct-invoke`。完整流程的模板和节点规则按上游原样执行。

采集排查经验维护在 `skills/msprof-application-troubleshooting/`。个人行为定制通过独立 Skill 和入口路由实现；三个上游 submodule 及其安装资源保持原样。修改已有本地 Skill 会通过相对链接生效；新增注册项或升级上游后重新安装并验证。

`.cannbot/`、`.codex/`、虚拟环境、构建产物和自动生成的插件入口由 `.gitignore` 排除。移动目录或换机器后，重新运行 `bash install.sh` 刷新路径。

更多内容见 [Git 与 submodule 管理](docs/GIT.md)、[插件与 Skill 配置](docs/插件与skill配置.md)、[Python/CANN 环境](docs/uv_setup.md)。配置检查不执行 DSL 编译、NPU 精度或性能测试。
