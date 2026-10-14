# Project Development Standard

通用 Agent Skill：先发现目标项目规则，再完成代码或文档任务、核查兼容性并报告真实验证结果。它不包含某个业务项目的规范、目录、协议、内部地址或凭据。

发布仓库：`eledd/project-development-standard`。可安装目录为 `skills/project-development-standard/`。

## 发布目录

```text
project-development-standard/
├── README.md
├── skills/
│   └── project-development-standard/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
│           ├── change-workflows.md
│           └── sensitive-chains.md
└── tests/
    └── test_skill_package.py
```

独立 Git 仓库应以本目录为根。安装对象是 `skills/project-development-standard/`，不是整个仓库；Skill 运行时只依赖该子目录内的文本，不需要业务项目、私有网络、特定 MCP、Python 包或其他 Skill。

## Skill 与项目规则的分工

- Skill：发现规则、理解调用方、保持兼容、按授权实施、验证和交付。
- 项目规则：决定技术栈、代码风格、文档目录与模板、业务边界、构建限制和检查命令。
- 团队强制执行：由项目钩子、CI 与代码评审承接，安装 Skill 本身不创建这些设施。

Skill 不会把其他项目的标准带入当前仓库。没有取得团队规范时会报告缺失，不会凭空声称满足团队标准。

## 安装与使用

### Codex

可以在 Codex 中明确请求：

```text
使用 $skill-installer，从 GitHub 仓库 eledd/project-development-standard
安装 skills/project-development-standard。团队使用时固定到确认过的提交版本。
```

Skill 目录链接：

```text
https://github.com/eledd/project-development-standard/tree/main/skills/project-development-standard
```

如果使用已安装的官方安装器，可执行下面的命令形式。脚本路径以本机实际安装位置为准；首次试用可读取 main，团队推广时将 main 替换为确认过的提交 SHA：

```bash
python3 "<skill-installer目录>/scripts/install-skill-from-github.py" \
  --repo "eledd/project-development-standard" \
  --path "skills/project-development-standard" \
  --ref "main"
```

安装器默认写入 Codex 用户级 skills 目录；已有同名目录时会拒绝覆盖，需要先核查来源及升级方式，不直接删除或覆盖。安装成功后的后续对话可显式调用：

```text
$project-development-standard
先读取当前项目规则，再完成本次开发或文档任务，并报告实际验证结果。
```

### 私有 Git 与仓库级接入

官方 GitHub 安装器的 `--repo` 针对 GitHub，不适用于任意内部 Git 域名。内部 Git 可通过已有受控流程拉取固定版本，再将完整 Skill 子目录放入工具支持的 skills 位置；不要只复制 `SKILL.md` 而漏掉参考文件。拉取与安装需要使用者的实际权限。

使用仓库级方式时，可将该 Skill 目录作为固定版本副本放入项目支持的位置。项目 `AGENTS.md` 引用该入口，并说明本项目规范在哪里；不要在通用 Skill 内添加项目专用规则。同名的全局安装与仓库副本并存时，应确认当前工具实际发现的版本；项目需要固定版本时，明确读取对应仓库副本。

其他 Agent 按其支持的 Skill 格式与规则入口配置，不承诺一次安装覆盖所有工具。即使不支持自动发现，也可以让 Agent 直接读取安装后的 `SKILL.md` 及其中需要的参考文件。

## 版本维护

版本以 Skill frontmatter 的 `metadata.version` 为准，当前为 `2.0.0`。发布后消费者固定标签或提交，不在开发热路径联网拉取最新版；升级需检查变更并重新验证项目接入。

通用流程只在本仓库维护。项目内的 Skill 是发布版本副本，项目专用约定留在该项目中；不要同时修改多个副本作为不同维护源。

公开发布前核实版权、许可、脱敏与所在组织的发布要求；开源许可证由所有者确认。Git 初始化、提交、推送和全局安装分别按实际授权执行，不因目录已经整理就视为已经发布或安装。

## 本地验证

发布前运行不联网的包验证：

```bash
python3 -B -m unittest discover -s tests -p test_skill_package.py
```

它在临时安装目录中验证 Skill 自包含、参考文件完整及路径不逃逸，不改用户级 Skill 安装。发布前另需检查内部信息和凭据；包结构或格式验证不证明所有 Agent 均已真实使用，也不代替实际项目的行为评估。
