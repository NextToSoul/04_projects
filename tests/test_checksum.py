from src.codec.checksum import sum_invert_low16, calculate_checksum

def test_known_frame():
    data = bytes.fromhex('0520C003000303DAAAAA')
    cs = sum_invert_low16(data)
    assert cs == 0xFCE3

def test_calculate_with_algorithm():
    data = bytes.fromhex('0520C003000303DAAAAA')
    cs = calculate_checksum(data, 'sum_invert_low16')
    assert cs == 0xFCE3

def test_empty():
    assert sum_invert_low16(b'') == 0xFFFF

def test_simple():
    data = bytes.fromhex('05')
    cs = sum_invert_low16(data)
    assert cs == 0xFFFA
