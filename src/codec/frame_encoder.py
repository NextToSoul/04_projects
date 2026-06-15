import struct
from src.codec.checksum import calculate_checksum

def encode_immediate_command(table, cmd_name, params_bytes=b'', seq=0, apid=None):
    if apid is None:
        apid = bytes.fromhex('0520')
    cmd = table.lookup(cmd_name)
    inst_code = bytes.fromhex(cmd['指令码(Hex)'])
    data = inst_code + params_bytes
    data_len = len(data) - 1
    header = bytes.fromhex('EB90') + apid
    header += struct.pack('>H', (0b11 << 14) | (seq & 0x3FFF))
    header += struct.pack('>H', data_len & 0xFFFF)
    payload = header + data
    checksum = calculate_checksum(payload[2:])
    return payload + struct.pack('>H', checksum)

def encode_inject_package(inj_table, inst_code, seq=0, apid=None):
    if apid is None:
        apid = bytes.fromhex('0520')
    params = inj_table.get_params()
    bo_key = '位偏移' + chr(10) + 'bit_offset'
    bl_key = '位长度' + chr(10) + 'bit_length'
    params_sorted = sorted(params, key=lambda p: int(p.get(bo_key, 0) or 0))
    data = inst_code
    for p in params_sorted:
        dt = str(p.get('数据类型', '') or '').lower().strip()
        val = p.get('参数值(十进制)') or p.get('参数值', 0) or 0
        val = float(val)
        if dt in ('float', 'float32'):
            data += struct.pack('>f', val)
        elif dt == 'uint32':
            data += struct.pack('>I', int(val))
        elif dt == 'uint16':
            data += struct.pack('>H', int(val))
        elif dt == 'uint8':
            data += struct.pack('B', int(val))
        else:
            data += struct.pack('>f', val)
    data_len = len(data) - 1
    header = bytes.fromhex('EB90') + apid
    header += struct.pack('>H', (0b11 << 14) | (seq & 0x3FFF))
    header += struct.pack('>H', data_len & 0xFFFF)
    payload = header + data
    checksum = calculate_checksum(payload[2:])
    return payload + struct.pack('>H', checksum)
