import openpyxl
from src.config.loader import load_excel_config, normalize_hex

class CommandTable:
    def __init__(self, filepath):
        self.filepath = filepath
        self.rows = load_excel_config(filepath, '立即遥控指令')
        self.by_name = {}
        for row in self.rows:
            name = str(row.get('指令代号', '') or '').strip()
            if name:
                self.by_name[name] = row
        self.enum_map = {}
        self._load_enum()

    def _load_enum(self):
        try:
            wb = openpyxl.load_workbook(self.filepath, data_only=True)
            ws = wb['枚举值映射表']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] is None:
                    continue
                code = normalize_hex(str(row[0]))
                val = normalize_hex(str(row[3]))
                label = str(row[4] or '').strip()
                if code not in self.enum_map:
                    self.enum_map[code] = {}
                if val:
                    self.enum_map[code][val] = label
        except Exception:
            pass

    def lookup(self, name):
        if name not in self.by_name:
            raise KeyError('指令 ' + name + ' 未找到')
        return self.by_name[name]

    def get_enum_map(self, inst_code):
        return dict(self.enum_map.get(inst_code, {}))

    def all(self):
        return list(self.rows)
