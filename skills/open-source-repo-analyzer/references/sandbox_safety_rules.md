# 开源项目沙箱隔离与调用安全防护准则 (Sandbox Safety Rules)

---

## 1. 隔离存储规范 (Storage Isolation Protocol)

在拉取、克隆或下载任何不受信任的外部开源代码时，必须强制遵守以下物理隔离规则：

1. **唯一受控目录**：
   所有外部代码必须落盘在本项目根目录下的 `external_repos/<repo-id>/` 目录内，严禁将外部代码直接解压至项目源代码根目录或主工程包下。
2. **双重 Git 屏蔽**：
   - 根目录 `.gitignore` 声明 `external_repos/`；
   - `external_repos/.gitignore` 声明 `*` 和 `!.gitignore`、`!README.md`。
   确保外部代码、大模型生成的临时文件、构建缓存（如 `.pyc`、`node_modules/`、`.venv/`、`.target/`）绝不流入主代码仓库的历史版本树中。
3. **命名合规与防穿越**：
   目标仓库目录名必须进行路径穿越（Path Traversal）安全清洗，剔除 `..`、`/`、`\\` 等恶意字符，统一格式化为短横线小写字符串。

---

## 2. 模拟运行防护与非破坏性探测 (Non-Destructive Dry-Run)

在对开源项目进行“模拟运行（Simulated Running）”时，严禁盲目执行 `eval()`、未经审计的 `curl | bash` 或直接运行可能包含后门的可执行文件。

### 2.1 探测分级防护机制

| 安全级别 | 探测动作 | 允许的操作与命令 | 风险控制 |
| :---: | :--- | :--- | :--- |
| **L1 (静态安全)** | 语法完整性与导入测试 | `python -m py_compile <file>`<br/>`node --check <file>` | 仅进行字节码/词法编译，零代码执行 |
| **L2 (探针扫描)** | 单测发现与用例搜集 | `pytest --collect-only`<br/>`npm test -- --dry-run` | 仅加载测试元数据，不执行具体测试逻辑 |
| **L3 (受控探活)** | 模块 Mock 执行与沙箱测试 | 在隔离子进程或独立虚拟环境中运行核心纯函数测试 | 设定严格超时限制 (Timeout: 15s)，限制网络与系统调用 |
| **L4 (高危禁用)** | 未知二进制与特权脚本 | 严禁以管理员/root 权限运行未经审计的 setup.py、二进制 ELF/EXE | 直接拦截并阻断 |

---

## 3. 跨项目调用适配器设计规范 (Adapter & Decoupling Standard)

当需要将外部开源项目的能力引入本项目时，严禁采用暴力“源码拷贝合并”方式，必须通过**适配器模式（Adapter Pattern）**进行解耦与代理：

```python
# 推荐的标准适配器模式示例：
import sys
from pathlib import Path

class ExternalModuleAdapter:
    """
    通过动态路径探测与契约封装，安全桥接 external_repos 中的外部算法算子
    """
    def __init__(self, external_repo_path: Path):
        self.repo_path = external_repo_path
        self._ensure_repo_available()

    def _ensure_repo_available(self):
        if not self.repo_path.exists():
            raise FileNotFoundError(f"External repo not found: {self.repo_path}")
        # 仅将外部仓库路径动态置入 sys.path，隔离命名空间
        if str(self.repo_path) not in sys.path:
            sys.path.insert(0, str(self.repo_path))

    def invoke_algorithm(self, input_data: dict) -> dict:
        # 强类型参数校验与异常捕获防护
        try:
            # 延迟导入目标模块
            from external_module.core import calculate
            return calculate(input_data)
        except Exception as e:
            return {"status": "error", "message": str(e)}
```

---

## 4. 敏感信息脱敏核查 (Credential & Secret Sanitization)

在对开源代码库进行文本打包或分析输出时，必须实时过滤如下敏感模式：
- AWS / GCP / Azure 密钥与凭据 (`AKIA...`, `ASIA...`, `AIzaSy...`)；
- 私有 SSH 密钥 (`-----BEGIN OPENSSH PRIVATE KEY-----`)；
- GitHub / GitLab 访问令牌 (`ghp_...`, `glpat-...`)；
- 数据库连接字符串 (`postgres://...`, `mongodb+srv://...`)。
任何被识别的敏感值均自动替换为 `[REDACTED_SECRET]`，防止在分析报告中造成凭据泄漏。
