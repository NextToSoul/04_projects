# Errors

Command failures and integration errors.

---

## 2026-06-15: Hex string truncated through PowerShell

**Error**: Hex string `0x0A` at end of frame was dropped when passed through `python -c "..."`, causing frame to be 77 instead of 78 bytes.

**Impact**: Frame byte offsets from index 51 onward were shifted, causing decoding errors for TM2036-TM2042.

**Fix**: Use Python script file (`.py`) instead of inline `-c "..."` to pass frame data. Scripts are not subject to PowerShell character processing.
