def sum_invert_low16(data: bytes) -> int:
    s = sum(data)
    return (~s) & 0xFFFF

def calculate_checksum(data: bytes, algorithm: str = 'sum_invert_low16') -> int:
    if algorithm == 'sum_invert_low16':
        return sum_invert_low16(data)
    raise ValueError('不支持的校验算法: ' + algorithm)
