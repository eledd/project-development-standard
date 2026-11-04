#!/usr/bin/env python3
"""校验 Git 工作分支名是否符合 project-development-standard 的默认格式。

只做校验，不执行任何 Git 写操作。格式与默认命名见 references/git-workflow.md：
    <type>/<YYYYMMDD>-<topic>
    <type>/<YYYYMMDD>-<issue-id>-<topic>   # 仅提供真实工单号时使用

用法：
    python3 check_branch_name.py <分支名> [<分支名> ...]

退出码：
    0  全部通过（含长期分支）
    1  存在不符合默认格式的分支名
    2  用法错误
"""

import re
import sys

# 项目已定义的长期分支，不套用工作分支格式（见 git-workflow.md）。
LONG_LIVED_BRANCHES = {
    "master", "main", "develop", "release",
    "feature_online", "pre", "prod", "production",
}

VALID_TYPES = {"feature", "fix", "hotfix"}

# 无业务含义的修订后缀：独立成词时视为不合格。
BANNED_TOKENS = {
    "new", "final", "v2", "v3", "wip", "tmp", "temp",
    "test", "test1", "test2", "fix1", "feature1",
}

# topic 的每个连字符分词只允许小写字母与数字。
TOPIC_TOKEN_RE = re.compile(r"^[a-z0-9]+$")


def check(name):
    """返回 (ok, errors, warnings)。errors 为致命问题，warnings 为建议。"""
    if name in LONG_LIVED_BRANCHES:
        return True, [], ["长期分支，不套用工作分支格式"]

    errors = []
    warnings = []

    if "/" not in name:
        return False, ["缺少类型前缀：应为 <type>/<YYYYMMDD>-<topic>，如 feature/20261020-mfa-push"], []

    parts = name.split("/")
    if len(parts) != 2:
        return False, ["只能有一个类型前缀：应为 <type>/<YYYYMMDD>-<topic>"], []

    branch_type, rest = parts
    if branch_type not in VALID_TYPES:
        errors.append(
            "类型 %r 不在白名单，应为 feature / fix / hotfix" % branch_type
        )

    matched = re.match(r"^(\d{8})-(.+)$", rest)
    if not matched:
        return False, ["缺少 8 位日期前缀：应为 <type>/<YYYYMMDD>-<topic>"], warnings

    date_str, topic = matched.group(1), matched.group(2)
    month, day = int(date_str[4:6]), int(date_str[6:8])
    if not (1 <= month <= 12 and 1 <= day <= 31):
        errors.append("日期 %s 不合法（YYYYMMDD）" % date_str)

    tokens = [t for t in topic.split("-") if t]
    if not tokens:
        errors.append("topic 不能为空或只写日期，需描述具体业务目标")
    else:
        for token in tokens:
            if not TOPIC_TOKEN_RE.match(token):
                errors.append(
                    "topic 含非法字符 %r：仅小写字母、数字、单个连字符，"
                    "不用中文/空格/下划线/大写混排" % token
                )
            elif token in BANNED_TOKENS:
                errors.append("topic 含无业务含义的修订后缀 %r" % token)

    if not (2 <= len(tokens) <= 6):
        warnings.append(
            "topic 建议 2~6 个词（当前 %d 个），以能辨识任务为准，不机械凑词" % len(tokens)
        )

    return (not errors), errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2

    all_ok = True
    for name in argv[1:]:
        ok, errors, warnings = check(name)
        if ok:
            note = ("  （" + warnings[0] + "）") if warnings else ""
            print("[OK]   %s%s" % (name, note))
        else:
            all_ok = False
            print("[FAIL] %s" % name)
            for message in errors:
                print("       - %s" % message)
            for message in warnings:
                print("       ! %s" % message)

    if all_ok:
        print("全部分支名符合默认格式")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
