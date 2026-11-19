#!/usr/bin/env python3
"""Check portable links and generated workflow paths without running NPU jobs."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def check_directory(directory):
    require(directory.is_dir(), f"缺少 Skill 目录: {directory}")
    entries = sorted(directory.iterdir())
    for entry in entries:
        require((entry / "SKILL.md").is_file(), f"Skill 入口损坏: {entry}")
        require(entry.resolve().is_relative_to(ROOT), f"Skill 指向包外: {entry}")
    print(f"PASS: {directory.relative_to(ROOT)}，{len(entries)} 个入口")
    return entries


def local_path(value):
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    require(path.resolve().is_relative_to(ROOT), f"配置路径指向包外: {value}")
    require(path.exists(), f"配置目标不存在: {value}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="同时检查开发/性能工作流配置")
    args = parser.parse_args()
    entries = check_directory(ROOT / ".agents/skills")
    for entry in entries:
        if entry.is_symlink():
            require(not entry.readlink().is_absolute(), f"项目 Skill 链接使用绝对路径: {entry}")
    require(len(entries) >= 14, "上游 Skill 或本地 Skill 不完整")
    entry_skill = ROOT / "skills/cannbot-dsl-dev"
    require((ROOT / ".agents/skills" / entry_skill.name).resolve() == entry_skill.resolve(),
            "开发入口未指向自己的 cannbot-dsl-dev Skill")
    extension = ROOT / "skills/msprof-application-troubleshooting"
    require((ROOT / ".agents/skills" / extension.name).resolve() == extension.resolve(),
            "本地扩展未指向父仓库 skills/ 目录")
    if args.full:
        config = json.loads((ROOT / ".cannbot/ops-direct-invoke.json").read_text())
        require(config["language"] == "dsl", "开发语言配置不是 dsl")
        assets = local_path(config["asset_root"])
        require((assets / "tools/workspace.py").is_file(), "缺少开发工作流工具")
        external = local_path(config["external_skills_root"])
        check_directory(external)
        require((external / extension.name).resolve() == extension.resolve(), "工作流缺少本地扩展")
        performance = local_path(config["performance_root"])
        registry = json.loads(local_path(config["performance_registry"]).read_text())
        require(any(item["plugin"] == "ops-perf-optimize" for item in registry["plugins"]),
                "性能插件未登记")
        check_directory(performance / ".agents/skills")
        require((performance / ".agents/skills" / extension.name).resolve() == extension.resolve(),
                "性能工作区缺少本地扩展")
        upstream = ROOT / "third_party/cannbot/plugins-official/ops-direct-invoke"
        for relative in ("agents", "docs", "orchestrations", "skills", "tools", "tests"):
            require((assets / relative).resolve() == (upstream / relative).resolve(),
                    f"工作流资源没有直接引用原版: {relative}")
        for name in ("README.md", "QUICKSTART.md"):
            require((assets / name).read_bytes() == (upstream / name).read_bytes(),
                    f"安装文档与原版不同: {name}")
        original_skills = {
            "ops-direct-invoke": "skills/orchestrator",
            "ops-direct-invoke-maintain": "skills/maintain",
            "ops-direct-invoke-requirement": f"skills/custom-skills/requirement/{config['platform']}",
            "ops-direct-invoke-repo-guide": f"skills/custom-skills/repo-guide/{config['repo']}",
        }
        for name, relative in original_skills.items():
            require((ROOT / ".agents/skills" / name).resolve() == (upstream / relative).resolve(),
                    f"上游 Skill 未保持原版入口: {name}")
        print("PASS: 原版工作流直接引用 third_party，本地开发入口独立注册")
        print("PASS: 开发和性能配置全部定位到当前工作区")
    print("上述检查仅验证配置与资源；未执行 DSL 编译、精度或性能测试。")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
