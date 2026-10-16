"""在临时安装目录验证分发包，不写用户级 skills 或依赖业务仓库。"""

import re
import shutil
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


SOURCE = Path(__file__).resolve().parents[1] / "skills" / "project-development-standard"
EXPECTED_FILES = {
    "SKILL.md", "agents/openai.yaml", "references/change-workflows.md",
    "references/sensitive-chains.md", "references/coding-standard.md",
    "references/java-backend.md", "references/documentation.md",
}


def reference_errors(root):
    """从入口遍历文档链接，检查安装后缺失的引用及逃逸到包外的依赖。"""
    root = root.resolve()
    pending = [root / "SKILL.md"]
    visited = set()
    errors = []
    while pending:
        file = pending.pop()
        if file in visited:
            continue
        visited.add(file)
        text = file.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]*\]\(([^)\s]+)\)", text):
            url = urlsplit(target)
            if url.scheme or url.netloc:
                errors.append("运行说明不应依赖外部链接: " + target)
                continue
            resolved = (file.parent / unquote(url.path)).resolve() if url.path else file
            if root.resolve() not in resolved.parents and resolved != root.resolve():
                errors.append("引用逃逸到安装包外: " + target)
            elif not resolved.is_file():
                errors.append("引用缺失: " + target)
            elif resolved.suffix == ".md":
                if url.fragment:
                    headings = re.findall(r"^#{1,6} (.+)$",
                                          resolved.read_text(encoding="utf-8"), re.MULTILINE)
                    if unquote(url.fragment) not in headings:
                        errors.append("参考章节缺失: " + target)
                pending.append(resolved)
    return visited, errors


class SkillPackageTest(unittest.TestCase):
    """模拟仅安装 Skill 子目录后的文件可用性。"""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = (Path(temporary.name) / SOURCE.name).resolve()
        shutil.copytree(SOURCE, self.root)

    def test_installation_is_complete_without_project_or_repository_root(self):
        actual = {str(path.relative_to(self.root)) for path in self.root.rglob("*")
                  if path.is_file()}
        self.assertEqual(actual, EXPECTED_FILES)
        self.assertEqual(reference_errors(self.root)[1], [])

    def test_every_reference_is_discoverable_from_entrypoint(self):
        visited, errors = reference_errors(self.root)
        self.assertEqual(errors, [])
        # 安装包内的每份规范都必须能从唯一入口找到，不能只随包分发却永远不被读取。
        expected = {self.root / name for name in EXPECTED_FILES if name.endswith(".md")}
        self.assertEqual(visited, expected)

    def test_each_bundled_standard_is_required_by_reference_graph(self):
        for name in ("coding-standard.md", "java-backend.md", "documentation.md"):
            with self.subTest(standard=name):
                file = self.root / "references" / name
                content = file.read_text(encoding="utf-8")
                file.unlink()
                self.assertTrue(any("引用缺失" in error
                                    for error in reference_errors(self.root)[1]))
                file.write_text(content, encoding="utf-8")

    def test_missing_reference_is_detected(self):
        (self.root / "references/change-workflows.md").unlink()
        self.assertTrue(any("引用缺失" in error for error in reference_errors(self.root)[1]))

    def test_existing_external_file_cannot_mask_escaped_dependency(self):
        external = self.root.parent / "outside.md"
        external.write_text("# 外部文件\n", encoding="utf-8")
        with (self.root / "SKILL.md").open("a", encoding="utf-8") as file:
            file.write("\n[不应依赖的规则](../outside.md)\n")
        self.assertTrue(any("逃逸" in error for error in reference_errors(self.root)[1]))

    def test_missing_section_is_detected(self):
        with (self.root / "SKILL.md").open("a", encoding="utf-8") as file:
            file.write("\n[缺失章节](references/change-workflows.md#没有该章节)\n")
        self.assertTrue(any("章节缺失" in error for error in reference_errors(self.root)[1]))

    def test_external_runtime_dependency_is_detected(self):
        with (self.root / "SKILL.md").open("a", encoding="utf-8") as file:
            file.write("\n[远程规则](https://example.com/rules.md)\n")
        self.assertTrue(any("不应依赖外部链接" in error
                            for error in reference_errors(self.root)[1]))

    def test_symlink_cannot_escape_package(self):
        external = self.root.parent / "external.md"
        external.write_text("# 外部规则\n", encoding="utf-8")
        (self.root / "references/escaped.md").symlink_to(external)
        with (self.root / "SKILL.md").open("a", encoding="utf-8") as file:
            file.write("\n[错误引用](references/escaped.md)\n")
        self.assertTrue(any("逃逸" in error for error in reference_errors(self.root)[1]))

    def test_cyclic_references_terminate_without_losing_documents(self):
        file = self.root / "references/change-workflows.md"
        with file.open("a", encoding="utf-8") as output:
            output.write("\n[返回入口](../SKILL.md)\n")
        visited, errors = reference_errors(self.root)
        self.assertEqual(errors, [])
        self.assertIn(file, visited)
        self.assertIn(self.root / "SKILL.md", visited)


if __name__ == "__main__":
    unittest.main()
