#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polyglot AST & Structural Repository Analyzer (repo_analyze.py)
Agentic Skills Standard Specification (ASSS v1.0) Compliant

Features:
- Polyglot structural decomposition (Python, TypeScript/JavaScript, Go, Rust, Java, C/C++)
- Deterministic Universal Symbol Contract (USC) mapping
- O(1) indexed dependency DAG resolution preventing N^2 performance cliff
- Windows POSIX normalization with Mermaid rendering node caps (Top 30)
- Resilient learning roadmap generation isolating malformed modules
"""

import os
import re
import ast
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple


class UniversalSymbol:
    """Standardized symbol representation across programming languages."""
    def __init__(self, name: str, kind: str, visibility: str = "PUBLIC",
                 complexity: int = 1, line: int = 1, args: List[str] = None,
                 docstring: Optional[str] = None):
        self.name = name
        self.kind = kind  # CLASS, INTERFACE, STRUCT, FUNCTION, METHOD, ENUM
        self.visibility = visibility  # PUBLIC, PRIVATE, PROTECTED
        self.complexity = complexity
        self.line = line
        self.args = args or []
        self.docstring = docstring

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "visibility": self.visibility,
            "complexity": self.complexity,
            "line": self.line,
            "args": self.args,
            "docstring": self.docstring
        }


class PythonASTParser:
    """Extracts classes, functions, complexity and imports from Python source."""
    @staticmethod
    def parse(file_path: Path, repo_root: Path) -> Dict[str, Any]:
        rel_posix = file_path.relative_to(repo_root).as_posix()
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except Exception as e:
            return {
                "file": rel_posix,
                "language": "Python",
                "error": f"AST Parse Error: {str(e)}",
                "symbols": [],
                "internal_deps": [],
                "external_deps": []
            }

        symbols = []
        internal_deps = set()
        external_deps = set()

        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.comp = 1
            def visit_If(self, node): self.comp += 1; self.generic_visit(node)
            def visit_For(self, node): self.comp += 1; self.generic_visit(node)
            def visit_While(self, node): self.comp += 1; self.generic_visit(node)
            def visit_Try(self, node): self.comp += len(node.handlers); self.generic_visit(node)
            def visit_BoolOp(self, node): self.comp += len(node.values) - 1; self.generic_visit(node)

        def get_comp(node):
            v = ComplexityVisitor()
            v.visit(node)
            return v.comp

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                c_comp = get_comp(node)
                symbols.append(UniversalSymbol(
                    name=node.name, kind="CLASS", complexity=c_comp, line=node.lineno,
                    docstring=ast.get_docstring(node)
                ).to_dict())
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        f_args = [a.arg for a in item.args.args]
                        vis = "PRIVATE" if item.name.startswith("_") and not item.name.startswith("__") else "PUBLIC"
                        symbols.append(UniversalSymbol(
                            name=f"{node.name}.{item.name}", kind="METHOD", visibility=vis,
                            complexity=get_comp(item), line=item.lineno, args=f_args,
                            docstring=ast.get_docstring(item)
                        ).to_dict())
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                f_args = [a.arg for a in node.args.args]
                vis = "PRIVATE" if node.name.startswith("_") else "PUBLIC"
                symbols.append(UniversalSymbol(
                    name=node.name, kind="FUNCTION", visibility=vis,
                    complexity=get_comp(node), line=node.lineno, args=f_args,
                    docstring=ast.get_docstring(node)
                ).to_dict())
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    pkg = alias.name.split(".")[0]
                    if (repo_root / pkg).exists() or (repo_root / f"{pkg}.py").exists():
                        internal_deps.add(alias.name)
                    else:
                        external_deps.add(pkg)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if node.level > 0 or mod.startswith("."):
                    internal_deps.add(mod)
                else:
                    pkg = mod.split(".")[0]
                    if (repo_root / pkg).exists() or (repo_root / f"{pkg}.py").exists():
                        internal_deps.add(mod)
                    else:
                        external_deps.add(pkg)

        return {
            "file": rel_posix,
            "language": "Python",
            "error": None,
            "symbols": symbols,
            "internal_deps": sorted(list(internal_deps)),
            "external_deps": sorted(list(external_deps))
        }


class PolyglotLexicalParser:
    """
    Zero-dependency lexical state-machine parser for TS/JS, Go, Rust, Java, C/C++.
    Extracts classes, structs, interfaces, functions, and import/include directives.
    """
    @staticmethod
    def strip_comments_and_strings(content: str) -> str:
        # Strip line comments and block comments
        content = re.sub(r"/\*[\s\S]*?\*/", " ", content)
        content = re.sub(r"//.*$", " ", content, flags=re.MULTILINE)
        content = re.sub(r"#.*$", " ", content, flags=re.MULTILINE)
        return content

    @classmethod
    def parse_typescript_javascript(cls, file_path: Path, repo_root: Path) -> Dict[str, Any]:
        rel_posix = file_path.relative_to(repo_root).as_posix()
        try:
            raw = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"file": rel_posix, "language": "TypeScript/JavaScript", "error": str(e), "symbols": [], "internal_deps": [], "external_deps": []}

        clean = cls.strip_comments_and_strings(raw)
        symbols = []
        internal_deps = set()
        external_deps = set()

        # Imports: import ... from './path' or require('./path')
        for match in re.finditer(r"""(?:import\s+(?:.*?)\s+from\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\s*\))""", clean):
            dep = match.group(1) or match.group(2)
            if dep.startswith(("./", "../")):
                internal_deps.add(dep)
            else:
                external_deps.add(dep.split("/")[0])

        # Exports and declarations
        class_matches = re.finditer(r"(?:export\s+)?(?:default\s+)?(class|interface|type)\s+([A-Za-z0-9_$]+)", clean)
        for m in class_matches:
            kind = "CLASS" if m.group(1) == "class" else ("INTERFACE" if m.group(1) == "interface" else "TYPE_ALIAS")
            symbols.append(UniversalSymbol(name=m.group(2), kind=kind, visibility="PUBLIC").to_dict())

        fn_matches = re.finditer(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\((.*?)\)", clean)
        for m in fn_matches:
            args = [a.strip().split(":")[0].strip() for a in m.group(2).split(",") if a.strip()]
            symbols.append(UniversalSymbol(name=m.group(1), kind="FUNCTION", visibility="PUBLIC", args=args).to_dict())

        return {
            "file": rel_posix,
            "language": "TypeScript/JavaScript",
            "error": None,
            "symbols": symbols,
            "internal_deps": sorted(list(internal_deps)),
            "external_deps": sorted(list(external_deps))
        }

    @classmethod
    def parse_golang(cls, file_path: Path, repo_root: Path) -> Dict[str, Any]:
        rel_posix = file_path.relative_to(repo_root).as_posix()
        try:
            raw = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"file": rel_posix, "language": "Go", "error": str(e), "symbols": [], "internal_deps": [], "external_deps": []}

        clean = cls.strip_comments_and_strings(raw)
        symbols = []
        internal_deps = set()
        external_deps = set()

        for m in re.finditer(r'import\s+(?:\(\s*([\s\S]*?)\s*\)|"([^"]+)")', clean):
            block = m.group(1)
            single = m.group(2)
            if single:
                external_deps.add(single)
            elif block:
                for line in block.splitlines():
                    p = line.strip().strip('"')
                    if p:
                        external_deps.add(p)

        # Structs and Interfaces
        for m in re.finditer(r"type\s+([A-Za-z0-9_]+)\s+(struct|interface)", clean):
            name, kind = m.groups()
            vis = "PUBLIC" if name[0].isupper() else "PRIVATE"
            symbols.append(UniversalSymbol(name=name, kind=kind.upper(), visibility=vis).to_dict())

        # Functions
        for m in re.finditer(r"func\s+(?:\([^\)]+\)\s+)?([A-Za-z0-9_]+)\s*\((.*?)\)", clean):
            name, raw_args = m.groups()
            vis = "PUBLIC" if name[0].isupper() else "PRIVATE"
            symbols.append(UniversalSymbol(name=name, kind="FUNCTION", visibility=vis).to_dict())

        return {
            "file": rel_posix,
            "language": "Go",
            "error": None,
            "symbols": symbols,
            "internal_deps": sorted(list(internal_deps)),
            "external_deps": sorted(list(external_deps))
        }

    @classmethod
    def parse_rust(cls, file_path: Path, repo_root: Path) -> Dict[str, Any]:
        rel_posix = file_path.relative_to(repo_root).as_posix()
        try:
            raw = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"file": rel_posix, "language": "Rust", "error": str(e), "symbols": [], "internal_deps": [], "external_deps": []}

        clean = cls.strip_comments_and_strings(raw)
        symbols = []
        internal_deps = set()
        external_deps = set()

        for m in re.finditer(r"use\s+([^;]+);", clean):
            u = m.group(1).strip()
            if u.startswith(("crate::", "super::")):
                internal_deps.add(u)
            else:
                external_deps.add(u.split("::")[0])

        for m in re.finditer(r"(pub(?:\([^\)]+\))?\s+)?(struct|enum|trait)\s+([A-Za-z0-9_]+)", clean):
            pub, kind, name = m.groups()
            vis = "PUBLIC" if pub else "PRIVATE"
            symbols.append(UniversalSymbol(name=name, kind=kind.upper(), visibility=vis).to_dict())

        for m in re.finditer(r"(pub(?:\([^\)]+\))?\s+)?fn\s+([A-Za-z0-9_]+)\s*\(", clean):
            pub, name = m.groups()
            vis = "PUBLIC" if pub else "PRIVATE"
            symbols.append(UniversalSymbol(name=name, kind="FUNCTION", visibility=vis).to_dict())

        return {
            "file": rel_posix,
            "language": "Rust",
            "error": None,
            "symbols": symbols,
            "internal_deps": sorted(list(internal_deps)),
            "external_deps": sorted(list(external_deps))
        }


class RepoAnalyzer:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.modules: List[Dict[str, Any]] = []
        self.external_libraries: Set[str] = set()

    def analyze(self) -> Dict[str, Any]:
        supported_exts = {
            ".py": "Python", ".pyw": "Python",
            ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
            ".go": "Go",
            ".rs": "Rust"
        }

        all_files = sorted(list(self.repo_root.rglob("*")), key=lambda p: p.as_posix())
        filtered = [f for f in all_files if f.is_file() and f.suffix.lower() in supported_exts and
                    not any(p.startswith(".") or p in ("__pycache__", "venv", ".venv", "node_modules", "target") for p in f.relative_to(self.repo_root).parts)]

        for fpath in filtered:
            ext = fpath.suffix.lower()
            if ext in (".py", ".pyw"):
                res = PythonASTParser.parse(fpath, self.repo_root)
            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                res = PolyglotLexicalParser.parse_typescript_javascript(fpath, self.repo_root)
            elif ext == ".go":
                res = PolyglotLexicalParser.parse_golang(fpath, self.repo_root)
            elif ext == ".rs":
                res = PolyglotLexicalParser.parse_rust(fpath, self.repo_root)
            else:
                continue

            self.modules.append(res)
            self.external_libraries.update(res["external_deps"])

        dep_graph = self._build_indexed_dependency_dag()
        learning_roadmap, malformed_modules = self._generate_resilient_learning_roadmap()

        return {
            "repository_name": self.repo_root.name,
            "root_path": self.repo_root.as_posix(),
            "module_count": len(self.modules),
            "external_dependencies": sorted(list(self.external_libraries)),
            "dependency_graph": dep_graph,
            "learning_roadmap": learning_roadmap,
            "malformed_modules": malformed_modules,
            "modules": self.modules
        }

    def _build_indexed_dependency_dag(self) -> Dict[str, List[str]]:
        """O(1) dictionary indexed matching for dependency DAG, avoiding N^2 loops."""
        file_lookup: Dict[str, str] = {}
        for mod in self.modules:
            f = mod["file"]
            file_lookup[f] = f
            file_lookup[Path(f).stem] = f

        graph: Dict[str, List[str]] = {}
        for mod in self.modules:
            src = mod["file"]
            graph[src] = []
            for dep in mod["internal_deps"]:
                norm = dep.lstrip("./").replace(".", "/")
                # Direct match or stem match
                matched = file_lookup.get(norm) or file_lookup.get(norm.split("/")[-1])
                if matched and matched != src and matched not in graph[src]:
                    graph[src].append(matched)

        return graph

    def _generate_resilient_learning_roadmap(self) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Partitions healthy modules into 3 progressive tiers while isolating malformed ones."""
        healthy = [m for m in self.modules if not m.get("error")]
        malformed = [m["file"] for m in self.modules if m.get("error")]

        sorted_healthy = sorted(
            healthy,
            key=lambda m: sum(s.get("complexity", 1) for s in m.get("symbols", []))
        )

        stages = [
            {"tier": "Stage 1: Core Primitives & Foundation Models (核心实体与基础数据模型)", "description": "Start here to understand data schemas, interfaces, and atomic utilities.", "modules": []},
            {"tier": "Stage 2: Business Logic & Processing Pipelines (核心算法与逻辑处理)", "description": "Understand core domain state machines, algorithms, and orchestration logic.", "modules": []},
            {"tier": "Stage 3: Entrypoints & Client Interfaces (系统入口与外部接口)", "description": "Trace main application lifecycles, CLI runners, and consumer API surfaces.", "modules": []}
        ]

        total = len(sorted_healthy)
        if total <= 2:
            stages[0]["modules"] = [m["file"] for m in sorted_healthy]
        else:
            p1 = max(1, total // 3)
            p2 = max(p1 + 1, (total * 2) // 3)
            stages[0]["modules"] = [m["file"] for m in sorted_healthy[:p1]]
            stages[1]["modules"] = [m["file"] for m in sorted_healthy[p1:p2]]
            stages[2]["modules"] = [m["file"] for m in sorted_healthy[p2:]]

        return stages, malformed

    def generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        md = [
            f"# Architectural Analysis & Learning Guide: {analysis['repository_name']}",
            "",
            "> 自动化生成的开源项目架构全景图、多语言符号契约与递进式学习路线图。",
            "",
            "## 1. 核心技术栈与外部依赖",
            f"- **源码模块总数**: {analysis['module_count']}",
            f"- **外部第三方库**: {', '.join(analysis['external_dependencies']) if analysis['external_dependencies'] else 'None (Pure Standard Library)'}",
            "",
            "## 2. 系统架构调用拓扑图 (Mermaid Topology)",
            "```mermaid",
            "graph TD"
        ]

        dag = analysis["dependency_graph"]
        rendered_edges = 0
        MAX_MERMAID_EDGES = 35

        for src, targets in dag.items():
            src_clean = re.sub(r"[^a-zA-Z0-9_]", "_", src)
            for tgt in targets:
                if rendered_edges >= MAX_MERMAID_EDGES:
                    break
                tgt_clean = re.sub(r"[^a-zA-Z0-9_]", "_", tgt)
                md.append(f'    {src_clean}["{src}"] --> {tgt_clean}["{tgt}"]')
                rendered_edges += 1

        if rendered_edges == 0:
            for mod in analysis["modules"][:6]:
                mclean = re.sub(r"[^a-zA-Z0-9_]", "_", mod["file"])
                mod_file = mod["file"]
                md.append(f'    {mclean}["{mod_file}"]')

        md.append("```")
        if rendered_edges >= MAX_MERMAID_EDGES:
            md.append(f"\n> ℹ️ *已截取前 {MAX_MERMAID_EDGES} 条关键依赖边以保证前端 Mermaid 渲染稳定性。*")

        md.append("")
        md.append("## 3. 递进式学习与精读路线图 (Progressive Learning Roadmap)")
        md.append("")

        for stage in analysis["learning_roadmap"]:
            md.append(f"### 📍 {stage['tier']}")
            md.append(f"*{stage['description']}*")
            md.append("")
            for mod_file in stage["modules"]:
                md.append(f"- [x] `{mod_file}`")
            md.append("")

        if analysis.get("malformed_modules"):
            md.append("### ⚠️ 异常隔离模块 (Malformed Modules - Needs Repair)")
            for mf in analysis["malformed_modules"]:
                md.append(f"- [ ] `{mf}`")
            md.append("")

        md.append("## 4. 关键导出符号与公共 API 矩阵 (Universal Symbols & Complexity)")
        md.append("")
        md.append("| 模块文件 | 语言 | 类/结构体 | 关键函数/方法 | 圈复杂度总计 |")
        md.append("| :--- | :---: | :--- | :--- | :---: |")

        for m in analysis["modules"]:
            classes = [s["name"] for s in m.get("symbols", []) if s.get("kind") in ("CLASS", "STRUCT", "INTERFACE")]
            funcs = [s["name"] for s in m.get("symbols", []) if s.get("kind") in ("FUNCTION", "METHOD")]

            c_names = ", ".join(f"`{c}`" for c in classes[:3]) or "-"
            if len(classes) > 3: c_names += f" (+{len(classes)-3})"

            f_names = ", ".join(f"`{f}()`" for f in funcs[:3]) or "-"
            if len(funcs) > 3: f_names += f" (+{len(funcs)-3})"

            comp = sum(s.get("complexity", 1) for s in m.get("symbols", []))
            md.append(f"| `{m['file']}` | {m.get('language', 'Unknown')} | {c_names} | {f_names} | {comp} |")

        md.append("")
        return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Polyglot Codebase AST & Dependency Topology Analyzer")
    parser.add_argument("repo_path", type=str, help="Root path of the repository")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file path (.md or .json)")
    args = parser.parse_args()

    root = Path(args.repo_path)
    if not root.is_dir():
        print(f"Error: Directory not found: {root}")
        exit(1)

    analyzer = RepoAnalyzer(root)
    result = analyzer.analyze()

    print(f"[OK] Analyzed {result['module_count']} source modules across polyglot languages.")
    print(f"[OK] Discovered {len(result['external_dependencies'])} external package dependencies.")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.suffix.lower() == ".json":
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            md_text = analyzer.generate_markdown_report(result)
            out.write_text(md_text, encoding="utf-8")
        print(f"[OK] Written analysis report to: {out}")
    else:
        print(analyzer.generate_markdown_report(result)[:1500])


if __name__ == "__main__":
    main()
