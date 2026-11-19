# Git 与 submodule 管理

本仓库跟踪自己的 Skill、入口路由、安装脚本和环境配置。`third_party/` 下三个官方仓库已登记为 submodule，父仓库仅保存其提交指针。

## 当前固定的上游版本

| 路径 | 提交 |
| --- | --- |
| `third_party/cannbot` | `fe0ed0b47eb0e281c7c49df34bf6dba2751006db` |
| `third_party/cannbot-skills` | `2fa8d0592d4aadc2220777bcb2e21bb2f0aa7c68` |
| `third_party/cannbot-dsl` | `08a04f7e290ab89d27c74087335a46c87e4aa82f` |

官方 URL 记录在 [`.gitmodules`](../.gitmodules)。个人开发行为维护在 `skills/cannbot-dsl-dev/`，通过任务条件选择本地流程或原版上游工作流。

## 克隆与更新

```bash
git clone git@github.com:hxmmxh/cannbot-dsl-agent.git
cd cannbot-dsl-agent
git submodule update --init
bash install.sh
```

这里初始化三个顶层 submodule；上游自身声明的其他子模块按任务需要再初始化。独立 Skill 入口和安装脚本使用本仓库的三个顶层依赖。

更新已有工作区：

```bash
git pull --ff-only
git submodule update --init
bash install.sh
```

查看当前登记和修改：

```bash
git submodule status
git diff --submodule
git status --short
```

## 维护自己的定制

- `skills/cannbot-dsl-dev/`：自己的开发入口与直接开发流程。
- `skills/msprof-application-troubleshooting/`：application 性能采集排查经验。

平台、语言和工程采用安装脚本内置的 Ascend / DSL / common 默认值。芯片与软件环境在实际开发前探测，生成的本机配置放在忽略的 `.cannbot/` 中。

安装器直接安装原版上游工作流，个人 Skill 以独立名称注册。已有本地 Skill 的修改会通过相对链接生效；新增注册项后重新安装。源文件和安装资源均保持原样。

```bash
git add skills scripts docs README.md AGENTS.md
git commit -m "Update local agent skills and task routing"
git push
```

本机尚未配置提交身份时，可只在当前仓库设置自己的姓名和邮箱，再提交：

```bash
git config user.name "你的 Git 姓名"
git config user.email "你的 Git 邮箱"
```

## 升级上游

在相应 submodule 中获取并选择新的官方提交，重新安装，验证本地 Skill 与上游入口、API 和工具的兼容性。个人流程所需的适配维护在自己的 Skill 或安装脚本中，上游源文件与安装资源保持原样。

验证后，父仓库一起提交新的 submodule 指针和本地适配：

```bash
git add third_party/cannbot third_party/cannbot-skills third_party/cannbot-dsl skills scripts
git diff --cached --submodule
git commit -m "Update pinned CANNBot dependencies"
```

运行配置、虚拟环境、任务记录和构建产物已忽略。父仓库的 `git archive` 不包含 submodule 源码；需要离线迁移时，应另外打包已取得的依赖工作树。
