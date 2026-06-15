import struct

def decode_telemetry_frame(tm, frame, package_name, resolve_enum=False):
    params = tm.get_package(package_name)
    result = {}
    for p in params:
        pid = str(p.get(chr(36965)+chr(27979)+chr(20195)+chr(21495), chr(39)+chr(39)) or chr(39)+chr(39)).strip()
        if not pid:
            continue
        bo = int(p.get(chr(20301)+chr(20559)+chr(31227)+chr(98)+chr(105)+chr(116)+chr(95)+chr(111)+chr(102)+chr(102)+chr(115)+chr(101)+chr(116), 0) or 0)
        bl = int(p.get(chr(20301)+chr(38271)+chr(24230)+chr(98)+chr(105)+chr(116)+chr(95)+chr(108)+chr(101)+chr(110)+chr(103)+chr(116)+chr(104), 0) or 0)
        dt = str(p.get(chr(25968)+chr(25454)+chr(31867)+chr(22411), chr(39)+chr(39)) or chr(39)+chr(39)).lower().strip()
        scale = float(p.get(chr(24403)+chr(37327), 1) or 1)
        if bl == 0:
            continue
        sb = bo // 8
        eb = (bo + bl + 7) // 8
        chunk = frame[sb:eb]
        if len(chunk) == 0:
            continue
        val = int.from_bytes(chunk, chr(98)+chr(105)+chr(103))
        shift = eb * 8 - bo - bl
        extracted = (val >> shift) & ((1 << bl) - 1)
        if dt in (chr(117)+chr(105)+chr(110)+chr(116)+chr(56), chr(117)+chr(105)+chr(110)+chr(116)+chr(49)+chr(54), chr(117)+chr(105)+chr(110)+chr(116)+chr(51)+chr(50), chr(117)+chr(105)+chr(110)+chr(116)):
            result[pid] = extracted * scale
        elif dt in (chr(105)+chr(110)+chr(116)+chr(49)+chr(54), chr(105)+chr(110)+chr(116)+chr(51)+chr(50)):
            if extracted >= (1 << (bl - 1)):
                extracted -= (1 << bl)
            result[pid] = extracted * scale
        elif dt in (chr(102)+chr(108)+chr(111)+chr(97)+chr(116)+chr(51)+chr(50), chr(102)+chr(108)+chr(111)+chr(97)+chr(116)):
            result[pid] = struct.unpack(chr(62)+chr(102), chunk)[0] if len(chunk) == 4 else extracted
        elif dt in (chr(101)+chr(110)+chr(117)+chr(109), chr(115)+chr(116)+chr(97)+chr(116)+chr(117)+chr(115), chr(98)+chr(105)+chr(116)+chr(102)+chr(105)+chr(101)+chr(108)+chr(100)):
            if resolve_enum:
                em = tm.get_enum_map(pid)
                result[pid] = em.get(str(extracted), str(extracted))
            else:
                result[pid] = extracted
        else:
            result[pid] = extracted * scale
    return result
