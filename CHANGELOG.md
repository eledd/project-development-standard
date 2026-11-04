# Changelog

本文件记录 `project-development-standard` 各发布版本的变更。版本号以 `skills/project-development-standard/SKILL.md` frontmatter 的 `metadata.version` 为准。

## 2.5.0

- 新增 `scripts/check_branch_name.py`：把 Git 分支默认命名规则固化成确定性校验（type 白名单、日期、topic 字符与禁用词）。
- 新增 `assets/templates/`：功能说明、接口参考、技术方案、评审记录四份最小骨架模板。
- SKILL.md 增加「示例」章节。
- 安装目录内补充 `LICENSE.txt`，保证安装副本携带许可证。

## 2.4.0

- 技术方案与交付增加逐服务的改造、配置、部署范围核实，覆盖跨服务契约、部署顺序、混部兼容、验证和回滚。
- 未核实项明确标注为「待确认」，不根据依赖关系推断所有服务都需部署。
- `references/change-workflows.md` 新增「服务影响与发布范围」章节。

## 2.3.0

- 增加 Git 工作分支命名与创建前核查，新增 `references/git-workflow.md`。

## 历史版本

2.3.0 之前的版本未在本文件记录；如需追溯，请查阅 Git 提交历史。
