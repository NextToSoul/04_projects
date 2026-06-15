# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## 2026-06-15: Windows 环境文件写入

- **correction**: PowerShell 的 Set-Content -Encoding UTF8 会在文件开头添加 BOM (EF BB BF)
- **correction**: PowerShell 的 -c "..." 传参时，中文字符会因编码转换损坏
- **insight**: pply_patch 工具 +content 格式（+后无空格）可避免前置空格
- **best_practice**: 含中文的测试文件路径使用占位符 + Python 替换

## 2026-06-15: Telemetry frame decoding verification

- **correction**: Hex strings passed through PowerShell -c "..." can lose characters
- **correction**: TM codes include full number (TM2036 not TM36)
- **insight**: Telemetry bit_offset values are absolute (from byte 0 of the frame)
- **insight**: Protocol uses MSB-first bit numbering (bit 0 = MSB of byte), formula shift = end_byte * 8 - bo - bl correctly implements MSB-first extraction
- **best_practice**: Validate telemetry offsets against real frame data before trusting config table

