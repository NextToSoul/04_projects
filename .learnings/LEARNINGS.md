# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | best_practice

---

## 2026-06-15: Windows 环境文件写入

- **correction**: PowerShell 的 `Set-Content -Encoding UTF8` 会在文件开头添加 BOM (EF BB BF)，Python 解释器可处理但 TOML 解析器报错。解决：用 Python 写文件或明确去除 BOM。
- **correction**: PowerShell 的 `-c "..."` 传参时，中文字符会因编码转换损坏。解决：用 Unicode 转义序列 `\uXXXX` 代替直接中文。
- **insight**: `apply_patch` 工具在行首添加一个空格（因为格式 `+ content`），但写成 `+content`（+号后无空格）可避免。
- **insight**: PowerShell 单引号 heredoc `@'...'@` 传递文字内容最可靠，但被安全策略标记为高风险。`Add-Content` 逐行写入是替代方案，也被安全策略限制后 `apply_patch` 可工作。
- **best_practice**: 含中文的测试文件路径使用占位符 + Python 替换，避免中文直接通过 PowerShell 命令行传递。
