# Simulation & Execution Audit: microduck

**Overall Health**: `Issues Detected` | **Language**: `Rust`

## 1. 运行环境与构建清单
- **Primary Stack**: Rust
- **Manifests Found**: `Cargo.toml`

## 2. 语法完整性审计 (Tier 1 Check)
- **Audited Files**: 14
- **Syntax Pass Status**: ❌ FAIL
```text
File spaces/vision-demo/control.py:   File "D:\workspace\code\yunyu-esp32\microduck\microduck\spaces\vision-demo\control.py", line 1
    ../shared/control.py
    ^
SyntaxError: invalid syntax

File spaces/vision-demo/rendezvous.py:   File "D:\workspace\code\yunyu-esp32\microduck\microduck\spaces\vision-demo\rendezvous.py", line 1
    ../shared/rendezvous.py
    ^
SyntaxError: invalid syntax

File spaces/vision-demo/wire.py:   File "D:\workspace\code\yunyu-esp32\microduck\microduck\spaces\vision-demo\wire.py", line 1
    ../shared/wire.py
    ^
SyntaxError: invalid syntax

```

## 3. 入口探针与 Dry-Run 仿真 (Tier 2 Check)
- ⚠️ **`spaces/hello/app.py`** (Status: `Non-Zero Exit`)
- ⚠️ **`spaces/vision-demo/app.py`** (Status: `Non-Zero Exit`)

## 4. 自动化测试套件执行 (Tier 3 Check)
*No tests/ directory or test_*.py files discovered.*
