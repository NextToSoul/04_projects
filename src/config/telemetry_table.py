import openpyxl
from src.config.loader import load_excel_config

PKG_NAMES = ['常规包1(SlowFrame)', '常规包2(SlowFrame2)', '查询包1(QueryFrame)']

class TelemetryTable:
    def __init__(self, filepath):
        self.filepath = filepath
        self.packages = {}
        self.enum_maps = {}
        self._load()

    def _load(self):
        for pkg in PKG_NAMES:
            self.packages[pkg] = load_excel_config(self.filepath, pkg)
        try:
            wb = openpyxl.load_workbook(self.filepath, data_only=True)
            ws = wb['枚举值映射表']
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0] is None:
                    continue
                pid = str(row[0]).strip()
                val = str(row[3]).strip()
                label = str(row[4] or '').strip()
                if pid not in self.enum_maps:
                    self.enum_maps[pid] = {}
                self.enum_maps[pid][val] = label
        except Exception:
            pass

    def get_package(self, name):
        if name not in self.packages:
            raise KeyError('遥测包 ' + name + ' 未找到')
        return self.packages[name]

    def get_enum_map(self, param_id):
        return dict(self.enum_maps.get(param_id, {}))
