# 下一代开源代码全生命周期分析体系：跨语言扩展、全平台韧性与大模型上下文经济学架构白皮书
## *Architectural Specification for Polyglot Analysis, Cross-Platform Resilience, and LLM Context Economics*

---

> **作者**: 跨语言系统架构师兼大模型上下文工程专家 (Principal Architect & LLM Context Engineer)  
> **目标工程**: `microUnit/skills/open-source-repo-analyzer`  
> **适用规范**: [Agentic Skills Specification Standard (ASSS v1.0)](../SPECIFICATION.md) · **状态**: Architecture Baseline Specification  

---

## 1. 执行摘要与架构演进动力 (Executive Summary)

在以大语言模型 (LLM) 和自主智能体 (Autonomous Coding Agents) 为驱动的软件工程范式变革中，`open-source-repo-analyzer` 承担着**“将异构开源世界翻译并安全注入智能体认知流”**的核心枢纽职责。

然而，当前 v1.0 基础版本存在三大维度的工程架构局限：
1. **语言绑定局限 (Monoglot Bottleneck)**：静态分析核心强耦合于 Python 标准库 `ast`，对占据开源生态半壁江山的前端/全栈 (`JavaScript/TypeScript`)、系统级编程 (`Go`, `Rust`)、后端企业级 (`Java`, `C/C++`) 代码库无原生结构化推导能力；
2. **环境异构脆弱性 (Platform Fragility)**：在 Windows (反斜杠路径、子进程孤儿子树、NTFS 文件锁竞争) 与 POSIX/容器 (信号隔离、文件权限位、无头环境挂起) 之间缺乏自愈与防御性设计；
3. **上下文经济学失谐 (Context Economics Mismatch)**：全量文本打包机制在超长上下文模型 (Claude 3.5 Sonnet 200k, Gemini 1.5 Pro 2M) 下未能释放 **Prompt Caching 提示词缓存** 的经济与延迟红利，而在短上下文/本地小模型 (DeepSeek 32k-64k, Qwen 2.5 Coder 32k, Llama 3.3 8k-16k) 下极易触发注意力衰减 (Lost in the Middle) 与上下文窗口溢出。

本架构白皮书围绕 **“多语言支持体系”**、**“跨平台运行环境兼容性”**、**“大模型调用矩阵与上下文经济学适配”** 以及 **“`scripts/` 目录工程化重构”** 四大支柱，输出全套工程技术规格与实现蓝图。

```mermaid
flowchart TD
    subgraph "Input Layer: 多源开源输入"
        RepoSource["开源项目源 (Local Path / Git URL)"]
        Langs["多语言技术栈: Python / TS / Go / Rust / Java / C++"]
    end

    subgraph "Core 1: Polyglot Parsing (多语言支持体系)"
        Tier0["Tier 0: 纯 Python 零依赖词法状态机 (DFA / Tokenizer)"]
        Tier1["Tier 1: 原生轻量工具链探针 (Subprocess Native Probe)"]
        Tier2["Tier 2: 动态 Tree-sitter / SCIP 语法引擎 (可选加速)"]
        USC["通用符号抽象契约 (Universal Symbol Contract - USC)"]
        Tier0 --> USC
        Tier1 --> USC
        Tier2 --> USC
    end

    subgraph "Core 2: Environment Resilience (环境韧性引擎)"
        WinSup["Windows 守护: JobObject 级联销毁 + NTFS 锁重试"]
        UnixSup["POSIX 守护: PGID 信号隔离 + 权限位修复 + 软链防逃逸"]
        CISup["CI/无头守护: 非交互环境变量 + 缓冲区流式消费"]
    end

    subgraph "Core 3: LLM Context Economics (大模型上下文经济学)"
        LongLLM["长上下文模型 (200k-2M):<br/>XML 语义隔离 + 确定性拓扑排序 + Prompt Caching 前缀缓存"]
        ShortLLM["短上下文 / 本地模型 (8k-64k):<br/>自适应 Token 预算 (ATB) + AST 骨架裁剪 (Skeletonizer)"]
        ContractOut["结构化输出: JSON Schema (Draft 2020-12) + MCP Tool Response"]
    end

    subgraph "Output & Execution: 交付与集成"
        AnalysisReport["架构拓扑报告 (Markdown / JSON / XML)"]
        IsolatedSandbox["安全沙箱探活 (Tier 1-3 Probes)"]
        CrossLangAdapter["多语言隔离适配器 (Polyglot Bridging Adapter)"]
    end

    RepoSource --> Core1
    RepoSource --> Core2
    USC --> Core3
    Core2 --> IsolatedSandbox
    Core3 --> AnalysisReport
    Core3 --> CrossLangAdapter
```

---

## 2. 专题一：多语言支持体系 (Polyglot Support Architecture)

### 2.1 架构设计目标与零硬依赖约束
- **核心难题**：在宿主环境不强加 GCC/Clang 编译链、Node.js 运行时或 Rust 工具链的前提下，如何以纯 Python 运行时解析多语言代码的模块结构、公共符号和依赖 DAG？
- **分层渐进式解析策略 (Multi-Tier Progressive Parsing Strategy)**：
  - **Tier 0 (Zero-Dependency Universal Lexical Parser)**：**保底引擎**。纯 Python 标准库 (`re`, `io`, `tokenize`) 实现，基于正则词法分析器与括号平衡栈的状态机。能 100% 独立运行在任何 Python 3.10+ 环境下，精准提取常见语言的公共符号（接口、结构体、类、函数、常量）与导入依赖。
  - **Tier 1 (Subprocess Native Toolchain Probe)**：**探活增强引擎**。自动探测宿主是否安装语言本地工具（如 `node`、`go`、`rustc`、`javap`）。若探测命中，通过轻量级命令行探针（如 `go doc -json` 或轻量内置 Node 脚本）提取编译期高精度元数据。
  - **Tier 2 (Pluggable Tree-Sitter Acceleration)**：**高性能精密引擎**。采用动态加载机制 (`importlib.util.find_spec("tree_sitter")`)。若存在 `tree_sitter` 和编译好的 Grammar 共享库，无缝升阶为毫秒级、完全精确的 CST/AST 解析。若缺失，无感知回退至 Tier 0，绝不阻断流水线。

---

### 2.2 通用符号抽象契约 (Universal Symbol Contract - USC)

为了让后续的架构拓扑推导、Mermaid 生成、Token 预算器和跨语言适配器能够解耦运行，必须统一各语言的 AST 符号表达。设计如下强类型契约模型（基于 Python `dataclasses`）：

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any


class SymbolKind(str, Enum):
    MODULE = "module"
    PACKAGE = "package"
    CLASS = "class"
    INTERFACE = "interface"
    STRUCT = "struct"
    ENUM = "enum"
    TRAIT = "trait"
    FUNCTION = "function"
    METHOD = "method"
    TYPE_ALIAS = "type_alias"
    CONSTANT = "constant"


class SymbolVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    INTERNAL = "internal"       # Go package unexported, Rust pub(crate)
    PACKAGE = "package_private" # Java default


@dataclass(frozen=True)
class SymbolSpan:
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0


@dataclass
class ParameterSpec:
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    is_variadic: bool = False


@dataclass
class UniversalSymbol:
    name: str
    qualified_name: str
    kind: SymbolKind
    visibility: SymbolVisibility
    span: SymbolSpan
    docstring: Optional[str] = None
    parameters: List[ParameterSpec] = field(default_factory=list)
    return_type: Optional[str] = None
    generic_params: List[str] = field(default_factory=list)
    decorators_or_annotations: List[str] = field(default_factory=list)
    is_async: bool = False
    is_abstract: bool = False
    mccabe_complexity: int = 1
    children: List["UniversalSymbol"] = field(default_factory=list)


@dataclass
class UniversalImport:
    raw_statement: str
    source_module: str                # 如 "express", "./utils", "github.com/gin-gonic/gin"
    imported_symbols: List[str]       # 导入的具体符号，若通配符为 ["*"]
    alias_mapping: Dict[str, str]     # 别名映射 {原名: 别名}
    is_relative: bool                 # 是否为工程内相对路径引入
    is_type_only: bool = False        # 如 TS 的 `import type { User }`
    line_number: int = 0


@dataclass
class UniversalModule:
    file_path: str                    # 统一为正斜杠 POSIX 相对路径
    language: str                     # "python", "typescript", "javascript", "go", "rust", "java", "cpp"
    loc: int                          # 代码有效行数
    docstring: Optional[str] = None
    symbols: List[UniversalSymbol] = field(default_factory=list)
    imports: List[UniversalImport] = field(default_factory=list)
    internal_dependencies: List[str] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    total_complexity: int = 0
    syntax_error: Optional[str] = None
```

---

### 2.3 通用依赖提取与词法状态机 (Universal Lexical State Machine)

为实现 Tier 0 的零依赖解析，设计一套基于字符流与词法标记 (Lexical Tokens) 的**通用有限状态机 (Universal Tokenizer State Machine)**。该状态机通过消除注释和字符串字面量干扰，提取跨语言结构。

#### 1. 通用词法过滤状态机转换图
```mermaid
stateDiagram-v2
    [*] --> STATE_CODE
    
    STATE_CODE --> STATE_LINE_COMMENT: 遇到 // 或 #
    STATE_LINE_COMMENT --> STATE_CODE: 遇到 \n
    
    STATE_CODE --> STATE_BLOCK_COMMENT: 遇到 /*
    STATE_BLOCK_COMMENT --> STATE_CODE: 遇到 */
    
    STATE_CODE --> STATE_STRING_SINGLE: 遇到 '
    STATE_STRING_SINGLE --> STATE_CODE: 遇到非转义 '
    
    STATE_CODE --> STATE_STRING_DOUBLE: 遇到 "
    STATE_STRING_DOUBLE --> STATE_CODE: 遇到非转义 "
    
    STATE_CODE --> STATE_RAW_STRING: 遇到 ` (JS/Go) 或 r#" (Rust)
    STATE_RAW_STRING --> STATE_CODE: 匹配闭合标记
```

#### 2. 多语言符号模式提取规则库 (Pattern Specifications)
在清理掉注释与字符串后，基于多语言语法特征与**大括号嵌套深度栈 (Brace Nesting Stack)** 进行精准提取：

| 目标语言 | 依赖导入规范 (Import Syntax) | 类/结构体/接口模式 (Type Declaration) | 函数与方法模式 (Function Declaration) |
| :--- | :--- | :--- | :--- |
| **JS / TS** | `import (?:type )?(?:(\w+) \|{([^}]+)}) from ['"]([^'"]+)['"]`<br/>`const (\w+) = require\(['"]([^'"]+)['"]\)` | `(?:export )?(?:default )?(class\|interface\|type\|enum)\s+(\w+)` | `(?:export )?(?:async )?function\s+(\w+)\s*\(([^)]*)\)`<br/>`(?:const\|let)\s+(\w+)\s*=\s*(?:async )?\(([^)]*)\)\s*=>` |
| **Go** | `import\s+"([^"]+)"`<br/>`import\s+\(([\s\S]*?)\)` | `type\s+(\w+)\s+(struct\|interface)` | `func\s+(?:\((\w+\s+\*?\w+)\)\s+)?(\w+)\s*\(([^)]*)\)\s*([^{]*)` |
| **Rust** | `(?:pub\s+)?use\s+([^;]+);`<br/>`mod\s+(\w+);` | `(?:pub\s+)?(?:struct\|enum\|trait)\s+(\w+)`<br/>`impl(?:\s+<[^>]+>)?\s+(?:(\w+)\s+for\s+)?(\w+)` | `(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)` |
| **Java** | `import\s+(?:static\s+)?([^;]+);`<br/>`package\s+([^;]+);` | `(?:public\|protected)?\s*(?:abstract\|final)?\s*(class\|interface\|record\|enum)\s+(\w+)` | `(?:public\|protected\|private)\s+(?:static\s+)?[<\w>,\[\]]+\s+(\w+)\s*\(([^)]*)\)` |
| **C / C++** | `#include\s*[<"]([^>"]+)[>"]`<br/>`import\s+([^;]+);` (C++20) | `(?:template\s*<[^>]*>\s*)?(?:class\|struct)\s+(\w+)` | `(?:[\w:*&<>]+\s+)+(\w+)\s*\(([^)]*)\)\s*(?:const)?\s*(?:override)?\s*[{;]` |

#### 3. 跨语言圈复杂度 (McCabe Metric) 纯文本启发式计算器
无需完整编译即可计算高置信度的 McCabe 复杂度：
$$\text{Complexity} = 1 + \sum (\text{BranchKeywords}) + \sum (\text{LogicalOperators})$$
- 分支关键词：`if`, `else if`, `elif`, `for`, `while`, `case`, `catch`, `except`, `match`, `guard`
- 逻辑运算符：`&&`, `||`, ` and `, ` or `, `?` (三元运算符与可选链空值合并 `??`)

---

### 2.4 依赖图谱归一化状态机 (Dependency Resolution State Machine)

提取到导入字符串后，必须将其区分为 **工程内部依赖 (Internal)** 与 **外部三方依赖 (External)**，以生成准确的 Mermaid 依赖拓扑：

```python
class UniversalDependencyResolver:
    """
    根据不同语言的包管理规范，将原始 import 目标解析并映射为仓库内相对文件路径。
    """
    def __init__(self, repo_root: Path, file_index: Set[str]):
        self.repo_root = repo_root
        self.file_index = file_index  # 仓库内所有文件正斜杠集合，如 {"src/utils.ts", "src/models/user.ts"}

    def resolve(self, current_file: str, language: str, raw_dep: str) -> Tuple[Optional[str], Optional[str]]:
        """
        返回: (internal_target_path, external_library_name)
        二者必居其一。
        """
        curr_dir = Path(current_file).parent.as_posix()

        if language in ("typescript", "javascript"):
            # 1. 相对路径导入: ./foo, ../bar
            if raw_dep.startswith("."):
                candidate_base = Path(curr_dir, raw_dep).as_posix()
                for ext in ["", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.js"]:
                    target = (candidate_base + ext).replace("//", "/")
                    if target in self.file_index:
                        return (target, None)
            # 2. 别名/三方库导入: react, @org/pkg
            return (None, raw_dep.split("/")[0] if not raw_dep.startswith("@") else "/".join(raw_dep.split("/")[:2]))

        elif language == "go":
            # Go 依据 go.mod 的 module 声明区分内部包与外部仓库
            # 若 raw_dep 匹配本仓库的 module prefix，则映射为内部相对路径
            module_name = self._get_go_module_name()
            if module_name and raw_dep.startswith(module_name):
                internal_subpath = raw_dep[len(module_name):].lstrip("/")
                # 检查 internal_subpath 下是否存在 go 文件
                if any(f.startswith(internal_subpath) for f in self.file_index):
                    return (internal_subpath, None)
            return (None, raw_dep)

        elif language == "rust":
            # crate::xxx -> 内部映射为 src/xxx.rs 或 src/xxx/mod.rs
            if raw_dep.startswith("crate::"):
                sub = raw_dep.replace("crate::", "").split("::")[0]
                candidates = [f"src/{sub}.rs", f"src/{sub}/mod.rs", f"{sub}.rs"]
                for c in candidates:
                    if c in self.file_index:
                        return (c, None)
            return (None, raw_dep.split("::")[0])

        elif language == "python":
            if raw_dep.startswith("."):
                return (self._resolve_python_relative(curr_dir, raw_dep), None)
            top_pkg = raw_dep.split(".")[0]
            if any(f.startswith(f"{top_pkg}/") or f == f"{top_pkg}.py" for f in self.file_index):
                return (raw_dep.replace(".", "/"), None)
            return (None, top_pkg)

        elif language in ("c", "cpp"):
            if not raw_dep.startswith("<"): # 双引号本地引用
                candidate = Path(curr_dir, raw_dep).as_posix()
                if candidate in self.file_index:
                    return (candidate, None)
                # 递归在 include_dirs 搜索
                for f in self.file_index:
                    if f.endswith(raw_dep):
                        return (f, None)
            return (None, raw_dep)

        return (None, raw_dep)
```

---

## 3. 专题二：跨平台运行环境兼容性 (Cross-Platform Environmental Resilience)

针对生产环境中 Windows、Linux、macOS 以及 Docker / CI/CD 无头沙箱的天然异构鸿沟，构建三大防线。

### 3.1 Windows 平台适配深度治理

Windows 环境下最致命的三类故障及其系统级治理：

#### 1. 路径反斜杠与字符串转义污染 (Backslash Contamination)
- **痛点**：`Path.resolve()` 在 Windows 上输出 `D:\repo\core\model.py`。反斜杠传给 Mermaid 图表（`spatial\core\models --> spatial\transform`）会导致语法错误崩溃，传给 JSON / Regex 极易引发非法转义符。
- **强制约束准则**：
  - 建立 **“POSIX Internal Normalization”** 原则：所有进入系统内存的路径，必须在入口处执行 `.as_posix()`；
  - 面向宿主 OS 交互（如 `open()`、`subprocess`）时由 Python 标准库自动处理 Windows 驱动器盘符与路径，所有序列化产物（Markdown、Mermaid、JSON）**绝对禁止反斜杠泄漏**。

#### 2. 进程树孤儿子进程与死锁 (Process Tree Orphanage & Subprocess Timeout)
- **痛点**：在 Windows 上，`subprocess.Popen.kill()` 仅终止调用的外层批处理或主进程。如果开源项目在测试探活中启动了构建守护进程（如 `npm run test` 派生的 Node worker、`pytest-xdist` 派生的 Python 子进程），主命令超时被杀后，子进程依旧死锁挂起，持续霸占端口与文件句柄。
- **内核级解决方案：Windows Job Object (作业对象) 托管**：
  通过 `ctypes` 调用 Windows 原生 Win32 API 创建 `JobObject`，并配置 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`。将子进程注入作业对象后，一旦 Python 探针关闭句柄或探针退出，操作系统内核保证**物理销毁整个级联进程树**。

```python
import sys
import ctypes
from typing import Optional

def setup_windows_job_object() -> Optional[int]:
    """
    配置 Windows Job Object 以保证子进程树的级联彻底清理。
    """
    if sys.platform != "win32":
        return None

    # Win32 API 声明
    kernel32 = ctypes.windll.kernel32
    CreateJobObject = kernel32.CreateJobObjectW
    SetInformationJobObject = kernel32.SetInformationJobObject
    
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    JobObjectExtendedLimitInformation = 9

    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [("ReadOperationCount", ctypes.c_uint64), ...]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoCounters", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryLimit", ctypes.c_size_t),
            ("PeakJobMemoryLimit", ctypes.c_size_t),
        ]

    job = CreateJobObject(None, None)
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE

    SetInformationJobObject(
        job,
        JobObjectExtendedLimitInformation,
        ctypes.byref(info),
        ctypes.sizeof(info)
    )
    return job
```
*(回退方案：若无 Win32 权限，捕获 `TimeoutExpired` 后强制执行 `subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)`)*

#### 3. NTFS 文件锁定与权限竞争 (WinError 32 / WinError 5)
- **痛点**：动态测试或克隆外部仓库后，清理 `external_repos/` 或 `__pycache__` 时，杀毒软件 (Windows Defender) 或刚退出的进程未及时释放句柄，导致 `shutil.rmtree` 频发 `PermissionError: [WinError 32] 另一个程序正在使用此文件`。
- **解决方案**：实现具有**指数退避与抖动 (Exponential Backoff with Jitter)** 的弹性文件操作器，并绑定 `onerror` 自动清除只读标记 (`stat.S_IWRITE`)。

---

### 3.2 Linux / macOS 环境适配规范

1. **Unix 信号机制与会话组隔离 (PGID Process Group Kill)**：
   - 在 POSIX 环境下，通过 `preexec_fn=os.setsid` 将子进程置于全新的会话组中；
   - 超时发生时，通过 `os.killpg(os.getpgid(proc.pid), signal.SIGTERM)` 进行优雅停机；
   - 设定 1.5 秒宽限期 (Grace Period)，若进程仍未退出，则发送硬性 `signal.SIGKILL` 彻底清除。
2. **文件权限与可执行位校验 (POSIX Executable Permissions)**：
   - 在动态探针执行脚本（如 `./gradlew`, `./mvnw`, `entrypoint.sh`）之前，预先审计其文件权限：
     ```python
     mode = os.stat(script_path).st_mode
     if not (mode & stat.S_IXUSR):
         os.chmod(script_path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
     ```
3. **符号链接安全沙箱穿越防御 (Symlink Traversal & Directory Escape)**：
   - 外部克隆的恶意开源仓库可能利用软链接指向宿主机的敏感路径（如 `/etc/passwd`、`~/.ssh/id_rsa`）或构造无限递归目录；
   - **防御策略**：遍历时检测 `path.is_symlink()`，计算 `path.resolve()` 并执行 `resolved.is_relative_to(repo_root)`，一旦逃逸或出现回环立即告警并熔断。

---

### 3.3 容器与 CI/CD 自动化流水线 (Headless Environment)

1. **零交互死锁防护 (Non-Interactive Guard)**：
   - 在 Docker、DevContainer 和 GitHub Actions 等无头环境中，交互式命令行提示会导致任务无限挂死；
   - 统一注入环境变量沙盒：
     ```python
     SAFE_ENV = {
         **os.environ,
         "GIT_TERMINAL_PROMPT": "0",          # 禁止 git clone 弹框询问凭据
         "CI": "true",                         # 告知各 CLI 处于 CI 模式
         "DEBIAN_FRONTEND": "noninteractive",
         "PYTHONUNBUFFERED": "1",              # 禁用 Python 缓冲区以保证实时日志
         "FORCE_COLOR": "0",                   # 过滤 ANSI 终端颜色转义码
         "TERM": "dumb"
     }
     ```
   - 进程执行时强制设定 `stdin=subprocess.DEVNULL`。
2. **管道缓冲区溢出防御 (Stream Deadlock Prevention)**：
   - 严禁对长输出命令使用同步 `proc.stdout.read()` 导致系统 64KB 管道缓冲区填满死锁；必须使用 `communicate(timeout=...)` 或独立后台守护线程分块排空。

---

## 4. 专题三：大模型调用矩阵与上下文经济学适配 (LLM Economics & Context Adaptation)

代码分析产物最终是为大语言模型消费服务的。根据底层模型的注意力机制和上下文窗口，必须采取完全分异的适配策略。

```mermaid
graph TD
    Repo["开源项目代码"] --> PackEngine["智能上下文打包引擎"]
    
    PackEngine --> Check{模型能力矩阵判定}
    
    Check -->|"超长上下文模型<br/>(Claude 3.5 Sonnet 200k, Gemini 1.5 Pro 2M)"| ModelTierA["策略 A: 语义隔离与 Prompt Caching 优化"]
    Check -->|"中短上下文 / 本地代码模型<br/>(DeepSeek-V3 64k, Qwen 2.5 Coder 32k, Llama 8k)"| ModelTierB["策略 B: 自适应 Token 预算 (ATB) 与代码骨架化"]

    subgraph "策略 A 流程"
        ModelTierA --> XMLDelim["XML 语义标签严格边界隔离"]
        XMLDelim --> StableSort["按路径规范字典序稳定排序"]
        StableSort --> CachePoints["设置前缀缓存断点 (cache_control: ephemeral)"]
        CachePoints --> FastInference["命中 Prompt Cache: 降低 90% 成本 + 80% 延迟"]
    end

    subgraph "策略 B 流程"
        ModelTierB --> ATB["ATB 算法: 计算目标 Token 预算配额"]
        ATB --> Skeletonize["骨架化: 保留类/方法签名与类型，裁剪实现为 ..."]
        Skeletonize --> Centrality["拓扑评分: PageRank + 入度 + McCabe 圈复杂度"]
        Centrality --> GreedyPack["贪婪背包算法: 预算内优先升级填充核心代码"]
    end
```

---

### 4.1 超长上下文模型适配架构 (Ultra-Long Context Models)

针对 **Claude 3.5 Sonnet (200k)**、**Gemini 1.5 Pro (2M)** 和 **GPT-4o (128k)** 等前沿长上下文模型：

#### 1. 结构化 XML 边界隔离标准 (Semantic XML Enclosure)
为什么必须从 Markdown 升级为 XML？
- **防代码反引号逃逸**：源代码中普遍包含 ``` 标记，这会导致 Markdown 解析器提前闭合代码块造成结构错乱；
- **Prompt 注入免疫**：通过专用标签 `<file path="...">` 与 `<![CDATA[...]]>` 明确界定代码数据与控制指令边界；
- **模型注意力锚定**：Anthropic 官方研究表明，Claude 对 XML 标签的层次解析敏感度显著优于 Markdown 二级标题。

标准输出结构规范：
```xml
<repository_context name="spatial_kinematics" total_files="8" tokens="14250">
  <architecture_summary>
    <modules count="3"/>
    <external_dependencies>
      <dependency name="numpy" version=">=1.22.0"/>
    </external_dependencies>
    <topology_dag format="mermaid">
      <![CDATA[
      graph TD
          spatial_core_transform --> spatial_core_models
      ]]>
    </topology_dag>
  </architecture_summary>

  <file_catalog>
    <file path="spatial_core/models.py" language="python" lines="68" complexity="4">
      <![CDATA[
# ... 文件原始内容 ...
      ]]>
    </file>
  </file_catalog>
</repository_context>
```

#### 2. Prompt Caching 提示词前缀缓存架构设计
Anthropic Claude 与 Google Gemini 的 Prompt Caching 机制基于**严格的前缀字节一致性 (Byte-for-Byte Prefix Invariance)**。
- **失效陷阱**：如果在 Prompt 开头放置了当前时间戳、随机生成的任务 ID 或遍历顺序不固定的目录列表，整个后续 10 万 Token 的缓存将全部失效，带来严重的经济与响应延迟惩罚。
- **缓存敏感型布局规范 (Cache-Optimized Layout)**：

```text
[01: System Instructions & ASSS Persona]  --> 静态系统提示词 (严格不变，命中缓存)
[02: Repository Global AST & Topology]    --> 模块依赖图、公共符号清单 (按规范字母序排序，命中缓存)
[03: Deterministic Source Catalog]       --> 全量代码文件 (按规范 POSIX 路径严格排序，稳定缓存)
-------------------------------------------------- [Cache Breakpoint: cache_control={"type": "ephemeral"}]
[04: Dynamic Sandbox Audit Results]      --> 实时沙箱探活日志、报错堆栈 (易变部分，不缓存)
[05: User Specific Query / Objective]     --> 具体的学习/调用/重构任务 (易变部分，不缓存)
```

---

### 4.2 中短上下文与本地开源模型适配 (Short-Context & Local LLMs)

针对 **DeepSeek-V3 / DeepSeek-R1 (32k/64k)**、**Qwen 2.5 Coder (32k)**、**Llama 3.3 (8k/16k)** 及 **Ollama / vLLM** 离线部署场景：代码库体量常常远超窗口上限。

#### 1. 自适应 Token 预算算法 (Adaptive Token Budgeting - ATB)
系统根据调用者传入的 `--max-tokens`（例如 28,000）自适应切分各层预算：

$$B_{\text{total}} = B_{\text{meta}} (5\%) + B_{\text{skeleton}} (35\%) + B_{\text{core\_impl}} (45\%) + B_{\text{headroom}} (15\%)$$

#### 2. 语法树骨架化提取器 (AST-Aware Skeletonizer)
将非核心代码压缩为其**公有契约骨架**。
- **输入代码**：
  ```python
  class KinematicsTransformer:
      """Manages spatial transformation matrix calculations."""
      def __init__(self, precision: int = 4):
          self.precision = precision
          self.history = []

      def transform_full(self, point: Point3D, rot: RotationMatrix, trans: TranslationVector) -> Point3D:
          """Performs full rigid-body transformation."""
          # 包含 15 行复杂的矩阵相乘、旋转平移及边界校验逻辑
          res = ...
          return res
  ```
- **骨架化产物**（压缩比高达 75%~90%，保留完整类型信息）：
  ```python
  class KinematicsTransformer:
      """Manages spatial transformation matrix calculations."""
      def __init__(self, precision: int = 4): ...

      def transform_full(self, point: Point3D, rot: RotationMatrix, trans: TranslationVector) -> Point3D:
          """Performs full rigid-body transformation."""
          ... # [TRUNCATED: 15 lines, McCabe=5]
  ```

#### 3. 基于图拓扑中介中心性与圈复杂度的重要性打分算法
当预算 $B_{\text{core\_impl}}$ 允许展开部分函数的完整实现时，何种函数具有最高认知优先级？
建立多因子评分模型：
$$Score(f_i) = w_1 \cdot \text{InDegree}(Module(f_i)) + w_2 \cdot \text{PageRank}(Module(f_i)) + w_3 \cdot \frac{\text{McCabe}(f_i)}{\text{MaxComplexity}} + w_4 \cdot \mathbb{I}_{\text{Public}}(f_i)$$
其中：
- $\text{InDegree}$ 代表被其他模块引用的频次（越高说明是底层核心基座）；
- $\text{McCabe}$ 代表算法复杂度（越高说明是核心算子，需要模型深读）；
- $\mathbb{I}_{\text{Public}}$ 为是否是对外暴露的公共 API。

**贪婪背包算法**：优先保留全仓骨架；随后按 $Score$ 降序将模块从“骨架”逐步升级为“完整实现”，直到触发 $B_{\text{core\_impl}}$ 预算红线截断。

---

### 4.3 统一结构化输出契约 (JSON Schema & MCP Specification)

为无缝融入 Cursor、OpenHands、Claude Desktop 及 Antigravity Agent 等 MCP (Model Context Protocol) 宿主，输出满足严格 Schema：

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RepoAnalysisResult",
  "type": "object",
  "required": ["repository_name", "status", "environment", "metrics", "modules", "topology"],
  "properties": {
    "repository_name": { "type": "string" },
    "status": { "type": "string", "enum": ["Healthy", "Degraded", "Failed"] },
    "environment": {
      "type": "object",
      "required": ["primary_language", "detected_manifests"],
      "properties": {
        "primary_language": { "type": "string" },
        "detected_manifests": { "type": "array", "items": { "type": "string" } }
      }
    },
    "metrics": {
      "type": "object",
      "required": ["total_files", "total_lines", "estimated_tokens"],
      "properties": {
        "total_files": { "type": "integer" },
        "total_lines": { "type": "integer" },
        "estimated_tokens": { "type": "integer" },
        "average_complexity": { "type": "number" }
      }
    },
    "topology": {
      "type": "object",
      "required": ["nodes", "edges", "mermaid_diagram"],
      "properties": {
        "nodes": { "type": "array", "items": { "type": "string" } },
        "edges": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["source", "target"],
            "properties": {
              "source": { "type": "string" },
              "target": { "type": "string" }
            }
          }
        },
        "mermaid_diagram": { "type": "string" }
      }
    },
    "modules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file", "language", "complexity", "symbols"],
        "properties": {
          "file": { "type": "string" },
          "language": { "type": "string" },
          "complexity": { "type": "integer" },
          "symbols": { "type": "array" }
        }
      }
    }
  }
}
```

---

## 5. 专题四：`scripts/` 目录代码架构重构与增强工程方案

### 5.1 现存代码架构瓶颈诊断
通过对当前 `scripts/` 的全量走读，识别出以下重构必要点：
1. **职责过载**：`repo_analyze.py` 将文件遍历、AST 遍历、圈复杂度计算、Mermaid 渲染、路线图编排全部揉在一个单文件中，扩展新语言极其困难；
2. **缺乏跨平台保护**：`repo_runner.py` 的子进程执行未设置 Windows 作业对象，未设定 `GIT_TERMINAL_PROMPT=0`，在长命令下极易产生孤儿死锁；
3. **适配器单向性**：`repo_adapter.py` 仅能生成 Python 包装 Python 模块的适配器，不支持宿主项目通过 CLI / IPC / WebAssembly / C-ABI 调用外部 JS/Go/Rust 项目；
4. **格式单调性**：`repo_pack.py` 缺乏 XML 格式与自适应 Token 裁剪功能。

---

### 5.2 全新架构目录拓扑规划

将 `scripts/` 模块化演进为内聚的高内聚低耦合分层架构：

```text
skills/open-source-repo-analyzer/scripts/
├── cli.py                         # 统一入口 (argparse, 支持 --budget, --model-tier, --format)
├── core/
│   ├── __init__.py
│   ├── symbols.py                 # Universal Symbol Contract (USC 数据模型)
│   ├── resilience.py              # 跨平台环境韧性 (Windows JobObject, PGID, 文件锁重试)
│   ├── budgeter.py                # 自适应 Token 预算算法 (ATB) 与代码骨架裁剪器
│   └── normalizer.py              # POSIX 路径归一化与敏感信息脱敏
├── parsers/
│   ├── __init__.py
│   ├── base.py                    # 抽象解析器基类 BaseRepoParser
│   ├── python_ast.py              # Python 专用高精度 AST 解析器
│   ├── polyglot_lexer.py          # 零依赖多语言通用词法状态机 (TS/Go/Rust/Java/C++)
│   └── tree_sitter_engine.py      # 可选 Tree-sitter 动态加速引擎 (若环境已装)
├── runner/
│   ├── __init__.py
│   ├── detector.py                # 构建清单与语言环境探测器
│   ├── supervisor.py              # 跨平台非破坏性执行沙箱看门狗
│   └── test_discovery.py          # 多语言测试套件发现与探活 (pytest, npm test, go test, cargo test)
└── adapters/
    ├── __init__.py
    ├── python_adapter.py          # 针对 Python 外部库的动态 sys.path 适配器
    └── polyglot_adapter.py        # 跨语言适配器 (Python <-> Node/Rust/Go subprocess/IPC 桥接)
```

---

### 5.3 核心增强模块详细规格与伪代码实现

#### 1. 跨平台沙箱执行看门狗 (`core/resilience.py` / `runner/supervisor.py`)
具备操作系统进程树治理、非交互保护与超时熔断能力的执行器：

```python
import os
import sys
import stat
import time
import signal
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class PlatformResilientSupervisor:
    """
    具备跨平台级联清理、环境隔离与防死锁能力的子进程看门狗。
    """
    def __init__(self, timeout_sec: int = 15):
        self.timeout_sec = timeout_sec

    def _get_safe_env(self) -> Dict[str, str]:
        env = dict(os.environ)
        env.update({
            "GIT_TERMINAL_PROMPT": "0",
            "CI": "true",
            "DEBIAN_FRONTEND": "noninteractive",
            "PYTHONUNBUFFERED": "1",
            "FORCE_COLOR": "0",
            "TERM": "dumb"
        })
        return env

    def run_command(self, cmd: List[str], cwd: Path) -> Dict[str, Any]:
        cwd_str = str(cwd.resolve())
        is_windows = sys.platform == "win32"
        
        # 针对 Windows 配置无弹框启动标志
        creationflags = 0
        if is_windows:
            # CREATE_NO_WINDOW = 0x08000000
            creationflags = 0x08000000

        start_time = time.time()
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd_str,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL, # 杜绝交互式悬挂
                text=True,
                encoding="utf-8",
                errors="replace",
                env=self._get_safe_env(),
                creationflags=creationflags,
                preexec_fn=None if is_windows else os.setsid # POSIX 会话组
            )

            try:
                stdout, stderr = proc.communicate(timeout=self.timeout_sec)
                elapsed = time.time() - start_time
                return {
                    "exit_code": proc.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "elapsed_sec": round(elapsed, 2),
                    "timed_out": False
                }
            except subprocess.TimeoutExpired:
                self._terminate_process_tree(proc)
                stdout, stderr = proc.communicate()
                return {
                    "exit_code": -1,
                    "stdout": stdout or "",
                    "stderr": f"Process timed out after {self.timeout_sec}s",
                    "elapsed_sec": self.timeout_sec,
                    "timed_out": True
                }

        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Supervisor invocation failure: {str(e)}",
                "elapsed_sec": round(time.time() - start_time, 2),
                "timed_out": False
            }

    def _terminate_process_tree(self, proc: subprocess.Popen):
        """跨平台彻底清理进程树"""
        if sys.platform == "win32":
            # 使用 Windows taskkill 强制杀灭子进程树
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        else:
            try:
                pgid = os.getpgid(proc.pid)
                os.killpg(pgid, signal.SIGTERM)
                time.sleep(0.5)
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def resilient_rmtree(target_path: Path, max_retries: int = 4):
    """带指数退避和权限剥离的跨平台删除器，抵抗 Windows 文件锁定"""
    def _handle_remove_readonly(func, path, exc):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    for attempt in range(max_retries):
        try:
            if target_path.is_dir():
                import shutil
                shutil.rmtree(target_path, onerror=_handle_remove_readonly)
            elif target_path.exists():
                os.chmod(target_path, stat.S_IWRITE)
                target_path.unlink()
            return
        except (PermissionError, OSError) as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(0.2 * (2 ** attempt))
```

---

#### 2. 通用词法解析状态机与符号提取器 (`parsers/polyglot_lexer.py`)
支持 Python、TS/JS、Go、Rust、Java、C++ 的纯 Python 零依赖解析器核心片段：

```python
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from ..core.symbols import (
    UniversalModule, UniversalSymbol, UniversalImport,
    SymbolKind, SymbolVisibility, SymbolSpan, ParameterSpec
)


class PolyglotLexicalParser:
    """
    通用零外部依赖多语言词法状态机解析器。
    """
    # 语言映射与扩展名规则
    LANG_EXT_MAP = {
        ".py": "python",
        ".ts": "typescript", ".tsx": "typescript",
        ".js": "javascript", ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".cpp": "cpp", ".hpp": "cpp", ".c": "c", ".h": "c"
    }

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def parse_file(self, file_path: Path) -> UniversalModule:
        rel_path = file_path.relative_to(self.repo_root).as_posix()
        ext = file_path.suffix.lower()
        language = self.LANG_EXT_MAP.get(ext, "unknown")

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return UniversalModule(
                file_path=rel_path, language=language, loc=0, syntax_error=str(e)
            )

        clean_code, comments = self._strip_comments_and_strings(content, language)
        loc = len([line for line in content.splitlines() if line.strip()])

        imports = self._extract_imports(content, language)
        symbols = self._extract_symbols(clean_code, content, language)
        total_complexity = sum(s.mccabe_complexity for s in symbols)

        return UniversalModule(
            file_path=rel_path,
            language=language,
            loc=loc,
            symbols=symbols,
            imports=imports,
            total_complexity=max(1, total_complexity)
        )

    def _strip_comments_and_strings(self, source: str, language: str) -> Tuple[str, List[str]]:
        """词法状态机：将注释与字符串替换为空白以消除模式干扰，但保留换行以维持行号对齐"""
        clean_chars = []
        comments = []
        i = 0
        n = len(source)

        while i < n:
            # C 风格行注释 //
            if source[i:i+2] == "//" and language != "python":
                start = i
                while i < n and source[i] != '\n':
                    i += 1
                comments.append(source[start:i])
                clean_chars.append(" " * (i - start))
            # C 风格块注释 /* ... */
            elif source[i:i+2] == "/*" and language != "python":
                start = i
                i += 2
                while i < n and source[i:i+2] != "*/":
                    clean_chars.append('\n' if source[i] == '\n' else ' ')
                    i += 1
                i = min(n, i + 2)
                clean_chars.append("  ")
            # Python 行注释 #
            elif source[i] == '#' and language == "python":
                start = i
                while i < n and source[i] != '\n':
                    i += 1
                comments.append(source[start:i])
                clean_chars.append(" " * (i - start))
            # 双引号字符串 "..."
            elif source[i] == '"':
                clean_chars.append('"')
                i += 1
                while i < n and source[i] != '"':
                    if source[i] == '\\' and i + 1 < n:
                        clean_chars.append("  ")
                        i += 2
                    else:
                        clean_chars.append('\n' if source[i] == '\n' else ' ')
                        i += 1
                if i < n:
                    clean_chars.append('"')
                    i += 1
            else:
                clean_chars.append(source[i])
                i += 1

        return "".join(clean_chars), comments

    def _extract_symbols(self, clean_code: str, original_code: str, language: str) -> List[UniversalSymbol]:
        symbols = []
        lines = clean_code.splitlines()

        # TypeScript / JavaScript 符号规则
        if language in ("typescript", "javascript"):
            class_pattern = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(class|interface|type)\s+(\w+)")
            func_pattern = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)")
            const_func_pattern = re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>")

            for idx, line in enumerate(lines):
                c_match = class_pattern.search(line)
                if c_match:
                    kind_str, name = c_match.groups()
                    kind = SymbolKind.INTERFACE if kind_str == "interface" else (SymbolKind.TYPE_ALIAS if kind_str == "type" else SymbolKind.CLASS)
                    symbols.append(UniversalSymbol(
                        name=name, qualified_name=name, kind=kind,
                        visibility=SymbolVisibility.PUBLIC if "export" in line else SymbolVisibility.INTERNAL,
                        span=SymbolSpan(start_line=idx+1, end_line=idx+1)
                    ))
                f_match = func_pattern.search(line) or const_func_pattern.search(line)
                if f_match:
                    name, params = f_match.groups()
                    symbols.append(UniversalSymbol(
                        name=name, qualified_name=name, kind=SymbolKind.FUNCTION,
                        visibility=SymbolVisibility.PUBLIC if "export" in line else SymbolVisibility.INTERNAL,
                        span=SymbolSpan(start_line=idx+1, end_line=idx+1),
                        mccabe_complexity=self._estimate_mccabe(line)
                    ))

        # Go 语言符号规则
        elif language == "go":
            type_pattern = re.compile(r"^type\s+(\w+)\s+(struct|interface)")
            func_pattern = re.compile(r"^func\s+(?:\((?:[^)]+)\)\s+)?(\w+)\s*\(([^)]*)\)")

            for idx, line in enumerate(lines):
                t_match = type_pattern.search(line)
                if t_match:
                    name, kind_str = t_match.groups()
                    kind = SymbolKind.STRUCT if kind_str == "struct" else SymbolKind.INTERFACE
                    vis = SymbolVisibility.PUBLIC if name[0].isupper() else SymbolVisibility.INTERNAL
                    symbols.append(UniversalSymbol(
                        name=name, qualified_name=name, kind=kind, visibility=vis,
                        span=SymbolSpan(start_line=idx+1, end_line=idx+1)
                    ))
                f_match = func_pattern.search(line)
                if f_match:
                    name, params = f_match.groups()
                    vis = SymbolVisibility.PUBLIC if name[0].isupper() else SymbolVisibility.INTERNAL
                    symbols.append(UniversalSymbol(
                        name=name, qualified_name=name, kind=SymbolKind.FUNCTION, visibility=vis,
                        span=SymbolSpan(start_line=idx+1, end_line=idx+1),
                        mccabe_complexity=self._estimate_mccabe(line)
                    ))

        # Rust 语言符号规则
        elif language == "rust":
            struct_pattern = re.compile(r"^\s*(pub\s+)?(struct|enum|trait)\s+(\w+)")
            fn_pattern = re.compile(r"^\s*(pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)")

            for idx, line in enumerate(lines):
                s_match = struct_pattern.search(line)
                if s_match:
                    is_pub, kind_str, name = s_match.groups()
                    kind = SymbolKind.TRAIT if kind_str == "trait" else (SymbolKind.ENUM if kind_str == "enum" else SymbolKind.STRUCT)
                    symbols.append(UniversalSymbol(
                        name=name, qualified_name=name, kind=kind,
                        visibility=SymbolVisibility.PUBLIC if is_pub else SymbolVisibility.INTERNAL,
                        span=SymbolSpan(start_line=idx+1, end_line=idx+1)
                    ))
                fn_match = fn_pattern.search(line)
                if fn_match:
                    is_pub, name, params = fn_match.groups()
                    symbols.append(UniversalSymbol(
                        name=name, qualified_name=name, kind=SymbolKind.FUNCTION,
                        visibility=SymbolVisibility.PUBLIC if is_pub else SymbolVisibility.INTERNAL,
                        span=SymbolSpan(start_line=idx+1, end_line=idx+1),
                        mccabe_complexity=self._estimate_mccabe(line)
                    ))

        return symbols

    def _estimate_mccabe(self, text: str) -> int:
        branch_words = ["if ", "else if", "elif ", "for ", "while ", "case ", "catch ", "?", "&&", "||", " and ", " or "]
        count = 1
        for w in branch_words:
            count += text.count(w)
        return count
```

---

#### 3. 自适应 Token 预算器与代码骨架修剪器 (`core/budgeter.py`)
面向本地模型与受限上下文的智能压缩器：

```python
import re
from typing import Dict, Any, List
from ..core.symbols import UniversalModule, UniversalSymbol, SymbolKind


class AdaptiveTokenBudgeter:
    """
    根据给定的 Token 预算上限，动态对源码执行 AST 骨架化与重要性填充。
    """
    def __init__(self, max_token_budget: int = 32000):
        self.budget = max_token_budget

    def prune_and_pack(self, modules: List[UniversalModule]) -> Dict[str, Any]:
        b_meta = int(self.budget * 0.05)
        b_skeleton = int(self.budget * 0.35)
        b_core = int(self.budget * 0.45)
        
        # 1. 骨架化所有模块
        skeleton_modules = []
        for m in modules:
            skel_code = self._skeletonize(m)
            skeleton_modules.append({
                "module": m,
                "skel_content": skel_code,
                "skel_tokens": len(skel_code) // 4
            })

        current_tokens = sum(sm["skel_tokens"] for sm in skeleton_modules)

        # 2. 如果骨架总量超出 (b_meta + b_skeleton + b_core)，则进一步执行纯接口裁剪
        if current_tokens > (b_skeleton + b_core):
            return self._emergency_prune(skeleton_modules, self.budget)

        # 3. 计算模块重要性评分并贪婪填充完整代码
        remaining_budget = (b_skeleton + b_core) - current_tokens
        scored_modules = sorted(
            skeleton_modules,
            key=lambda x: self._calculate_importance(x["module"]),
            reverse=True
        )

        final_contents = {}
        for item in scored_modules:
            mod = item["module"]
            # 读取完整源码
            full_code = Path(mod.file_path).read_text(encoding="utf-8", errors="replace")
            full_tokens = len(full_code) // 4
            delta = full_tokens - item["skel_tokens"]

            if delta <= remaining_budget:
                final_contents[mod.file_path] = full_code
                remaining_budget -= delta
            else:
                final_contents[mod.file_path] = item["skel_content"]

        return {
            "allocated_tokens": self.budget - remaining_budget,
            "file_contents": final_contents
        }

    def _skeletonize(self, module: UniversalModule) -> str:
        """根据语言特征裁剪函数实现，仅保留签名与注释"""
        raw_code = Path(module.file_path).read_text(encoding="utf-8", errors="replace")
        if module.language == "python":
            # 将 def/class 内部非 docstring 的主体替换为 ...
            return self._skeletonize_python(raw_code)
        else:
            # 针对大括号语言 (TS/Go/Rust/C++)：保留外层结构，将花括号主体折叠为 { ... }
            return self._skeletonize_c_style(raw_code)

    def _skeletonize_python(self, code: str) -> str:
        lines = code.splitlines()
        result = []
        in_func = False
        func_indent = 0

        for line in lines:
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())

            if stripped.startswith("def ") or stripped.startswith("async def "):
                in_func = True
                func_indent = indent
                result.append(line)
            elif in_func:
                if indent <= func_indent and stripped != "":
                    in_func = False
                    result.append(line)
                elif '"""' in stripped or "'''" in stripped:
                    result.append(line) # 保留文档注释
                elif in_func and (len(result) == 0 or not result[-1].strip().endswith("...")):
                    result.append(" " * (func_indent + 4) + "...")
            else:
                result.append(line)
        return "\n".join(result)

    def _skeletonize_c_style(self, code: str) -> str:
        # 简单折叠函数主体示例：func(...) { ... }
        pattern = re.compile(r"(\)\s*(?:[^{;]*)\s*)\{[\s\S]*?\}", re.MULTILINE)
        return pattern.sub(r"\1{ ... }", code)

    def _calculate_importance(self, module: UniversalModule) -> float:
        # 基于入度 + 复杂度的重要性
        in_degree = len(module.internal_dependencies)
        return in_degree * 2.5 + module.total_complexity * 0.8
```

---

## 6. 演进路线图与验收基准 (Roadmap & Verification Criteria)

| 阶段里程碑 | 周期目标 | 交付物与质量门禁 |
| :--- | :--- | :--- |
| **Phase 1: 契约与环境就绪** | 跨平台看门狗、符号契约定义、路径归一化重构 | - 交付 `core/symbols.py`, `core/resilience.py`<br/>- Windows 下进程彻底销毁测试覆盖率 100%<br/>- 无反斜杠泄漏回归测试通过 |
| **Phase 2: 零依赖多语言解析** | 实现 TS/JS, Go, Rust, Java, C++ 词法状态机 | - 交付 `parsers/polyglot_lexer.py`<br/>- 验证 5 种异构语言样例仓库，公共符号抽取召回率 > 92%<br/>- 零新增 pip 强依赖 |
| **Phase 3: 上下文经济学闭环** | ATB 预算器、代码骨架裁剪器、XML/Prompt Caching 格式化 | - 交付 `core/budgeter.py` 与 `--budget` CLI 选项<br/>- 本地 32k 模型测试：10 万行代码库在 32k 窗口内准确保留核心调用链，无溢出报错<br/>- 验证 Anthropic Prompt Caching 命中率提升至 85%+ |
| **Phase 4: 多语言适配器生成** | 扩展 `repo_adapter.py` 支持 Python 桥接外部 TS/Go/Rust 二进制与 IPC | - 交付 `adapters/polyglot_adapter.py`<br/>- 成功生成 Python 调用外部 Go 模块 / Node 模块的双向集成样例 |

---

## 7. 专家结论 (Architectural Sign-Off)

本方案在严格继承并遵守 `ASSS v1.0 Standard` 的前提下，通过**“分层渐进多语言词法状态机”**突破了对单一语言 `ast` 的历史依赖；通过**“作业对象与会话组治理”**彻底解决了 Windows/POSIX/Docker 跨平台进程与文件锁死穴；通过**“长上下文 Prompt Caching 语义对齐”**与**“短上下文自适应 Token 预算骨架化”**双轮驱动，构建了真正契合现代大模型上下文经济学的高可用系统基座。
