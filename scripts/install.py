#!/usr/bin/env python3
"""Register local Skills and install unmodified upstream CANNBot workflows."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "cannbot-dsl-env-check", "cannbot-dsl-op-design",
    "cannbot-dsl-unit-planner", "cannbot-dsl-test-generator",
    "cannbot-dsl-best-practice", "cannbot-dsl-code-reviewer",
    "ops-design-paradigms", "ops-profiling", "ops-spec-gen",
    "npu-arch", "ops-precision-standard",
)
LOCAL_SKILLS = ("cannbot-dsl-dev", "msprof-application-troubleshooting")


def run(args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def skill_sources():
    result = {name: ROOT / "third_party/cannbot-skills/ops" / name
              for name in SKILL_NAMES}
    result["cannbotdsl-doc-reviewer"] = (
        ROOT / "third_party/cannbot-dsl/skill/cannbotdsl-doc-reviewer")
    result.update({name: ROOT / "skills" / name for name in LOCAL_SKILLS})
    return result


def register_skills():
    destination = ROOT / ".agents/skills"
    sources = skill_sources()
    # Validate all entries before changing any link.
    for name, source in sources.items():
        if not (source / "SKILL.md").is_file():
            raise RuntimeError(f"缺少 Skill: {source}")
        target = destination / name
        if os.path.lexists(target) and not (
                target.is_symlink() and target.resolve() == source.resolve()):
            raise RuntimeError(f"目标已有不同内容，请先处理: {target}")
    destination.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        target = destination / name
        if not os.path.lexists(target):
            target.symlink_to(os.path.relpath(source, destination), target_is_directory=True)
    print(f"已注册 {len(sources)} 个独立 Skill。", flush=True)


def check_prerequisites():
    for command in ("bash", "git", "node", "tmux"):
        if not shutil.which(command):
            raise RuntimeError(f"缺少命令: {command}，请安装后重试。")
    version = subprocess.check_output(["node", "--version"], text=True).strip()
    major, minor = map(int, version.lstrip("v").split(".")[:2])
    if (major, minor) < (20, 11):
        raise RuntimeError(f"需要 Node.js >= 20.11，当前为 {version}")
    if importlib.util.find_spec("yaml") is None:
        raise RuntimeError(
            "安装脚本所用 Python 缺少 PyYAML。请选择已安装 PyYAML 的 Python，"
            "例如 CANNBOT_PYTHON=/path/to/python bash install.sh。")


def check_upstream_worktrees():
    for name in ("cannbot", "cannbot-skills", "cannbot-dsl"):
        source = ROOT / "third_party" / name
        top = subprocess.run(["git", "-C", source, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True)
        if top.returncode != 0 or Path(top.stdout.strip()).resolve() != source.resolve():
            raise RuntimeError(f"请先初始化 submodule：git submodule update --init（缺少 {name}）")
        status = subprocess.check_output(
            ["git", "-C", source, "status", "--porcelain"], text=True)
        if status:
            raise RuntimeError(f"{name} 有本地修改；个人定制请维护在 skills/ 中。")


def register_extension(directory):
    source = ROOT / "skills/msprof-application-troubleshooting"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / source.name
    if os.path.lexists(target):
        if target.is_symlink() and target.resolve() == source.resolve():
            return
        raise RuntimeError(f"扩展 Skill 目标已有不同内容: {target}")
    target.symlink_to(os.path.relpath(source, directory), target_is_directory=True)


def remove_legacy_overlay_cache():
    # Retire only the generated copy owned by the previous installer, after the
    # new upstream installation has passed validation. Task records are untouched.
    parent = ROOT / ".cannbot/bootstrap"
    marker = parent / "cannbot-managed-by-dev-kit"
    legacy = parent / "cannbot"
    if not marker.is_file() or marker.read_text() != "Generated upstream copy with parent-owned overrides.\n":
        return
    if legacy.is_symlink():
        return
    if legacy.exists():
        shutil.rmtree(legacy)
    marker.unlink()
    (parent / "overrides-applied.json").unlink(missing_ok=True)
    if not any(parent.iterdir()):
        parent.rmdir()
    print("已清理旧的工作流覆盖缓存。", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-only", action="store_true",
                        help="只注册 12 个上游 Skill 和 2 个本地 Skill")
    args = parser.parse_args()
    if not args.skills_only:
        check_prerequisites()
        check_upstream_worktrees()
    register_skills()
    if args.skills_only:
        print("在当前目录重新打开 Codex；完整工作流可稍后运行 bash install.sh。")
        return
    # This repository has a fixed purpose. Device selection belongs to the
    # task's environment check; clear any machine-specific chip from old installs.
    config = {
        "platform": "ascend",
        "chip": "unknown",
        "repo": "common",
        "language": "dsl",
        "preferences": {"interaction": "confirm"},
    }
    local_config = ROOT / ".cannbot/init-config.json"
    local_config.parent.mkdir(parents=True, exist_ok=True)
    local_config.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    shared = ROOT / "third_party/cannbot-skills"
    plugin_source = ROOT / "third_party/cannbot"
    environment = os.environ.copy()
    environment.update({
        "CANNBOT_SKIP_DEPENDENCY_REPOS": "1",
        "CANNBOT_SKIP_KNOWLEDGE_INDEX": "1",
        "CANNBOT_SKIP_OPMODEL_INSTALL": "1",
        "CANNBOT_PYTHON": sys.executable,
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    # Do not depend on a caller's cwd, global hooks or interactive installer menus.
    run(["bash", plugin_source / "plugins-official/ops-direct-invoke/init.sh",
         "project", "codex", ROOT, "--skills", shared,
         "--init-config", local_config], cwd=ROOT, env=environment,
        stdin=subprocess.DEVNULL)
    installed = json.loads((ROOT / ".cannbot/ops-direct-invoke.json").read_text())
    register_extension(Path(installed["external_skills_root"]))
    register_extension(Path(installed["performance_root"]) / ".agents/skills")
    run([sys.executable, ROOT / "scripts/check_setup.py", "--full"], cwd=ROOT)
    remove_legacy_overlay_cache()
    print("安装完成。在当前目录重新打开 Codex 即可使用。", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"安装失败: {error}", file=sys.stderr)
        sys.exit(1)
