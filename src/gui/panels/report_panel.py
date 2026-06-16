import json
from PySide6.QtWidgets import (
   QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel,
   QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
   QFileDialog, QMessageBox, QHeaderView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class ReportPanel(QWidget):
   def __init__(self, parent=None):
       super().__init__(parent)
       self._report = None
       self._build_ui()

   def _build_ui(self):
       layout = QVBoxLayout(self)

       tb = QHBoxLayout()
       self.load_btn = QPushButton('加载报告')
       self.export_json = QPushButton('导出 JSON')
       self.export_html = QPushButton('导出 HTML')
       tb.addWidget(self.load_btn)
       tb.addWidget(self.export_json)
       tb.addWidget(self.export_html)
       tb.addStretch()
       layout.addLayout(tb)

       self.summary = QFrame()
       self.summary.setFrameShape(QFrame.StyledPanel)
       self.summary.setStyleSheet(
           'QFrame { background: #f5f5f5; padding: 8px; }')
       sl = QHBoxLayout(self.summary)
       self.name_label = QLabel('')
       self.name_label.setStyleSheet('font-size: 14px; font-weight: bold;')
       self.pass_label = QLabel('通过: --')
       self.pass_label.setStyleSheet('color: green; font-size: 14px; font-weight: bold;')
       self.fail_label = QLabel('失败: --')
       self.fail_label.setStyleSheet('color: red; font-size: 14px; font-weight: bold;')
       self.total_label = QLabel('总计: --')
       sl.addWidget(self.name_label)
       sl.addStretch()
       sl.addWidget(self.pass_label)
       sl.addWidget(self.fail_label)
       sl.addWidget(self.total_label)
       layout.addWidget(self.summary)

       split = QSplitter(Qt.Vertical)

       self.step_table = QTableWidget(0, 3)
       self.step_table.setHorizontalHeaderLabels(['步骤', '名称', '状态'])
       self.step_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
       self.step_table.setSelectionBehavior(QTableWidget.SelectRows)
       split.addWidget(self.step_table)

       self.detail = QTextEdit()
       self.detail.setReadOnly(True)
       split.addWidget(self.detail)
       split.setSizes([300, 300])
       layout.addWidget(split)

       self.load_btn.clicked.connect(self._load)
       self.export_json.clicked.connect(self._export_json)
       self.export_html.clicked.connect(self._export_html)
       self.step_table.itemSelectionChanged.connect(self._show_detail)

   def set_report(self, report: dict):
       self._report = report
       if not report:
           return
       self.name_label.setText(report.get('name', ''))
       passed = report.get('passed', 0)
       failed = report.get('failed', 0)
       total = passed + failed
       self.pass_label.setText(f'通过: {passed}')
       self.fail_label.setText(f'失败: {failed}')
       self.total_label.setText(f'总计: {total}')
       self._fill_steps(report.get('steps', []))

   def _fill_steps(self, steps):
       self.step_table.setRowCount(0)
       for s in steps:
           r = self.step_table.rowCount()
           self.step_table.insertRow(r)
           self.step_table.setItem(r, 0, QTableWidgetItem(s.get('id', '')))
           self.step_table.setItem(r, 1, QTableWidgetItem(s.get('name', '')))
           st = s.get('status', '')
           si = QTableWidgetItem(st.upper())
           si.setForeground(QColor('green') if st == 'pass' else QColor('red'))
           self.step_table.setItem(r, 2, si)

   def _show_detail(self):
       r = self.step_table.currentRow()
       if r < 0 or not self._report:
           self.detail.clear()
           return
       steps = self._report.get('steps', [])
       if r < len(steps):
           self.detail.setPlainText(json.dumps(steps[r], indent=2, ensure_ascii=False))

   def _load(self):
       p, _ = QFileDialog.getOpenFileName(self, '加载报告', '', 'JSON (*.json)')
       if not p:
           return
       try:
           with open(p, 'r', encoding='utf-8') as f:
               self.set_report(json.load(f))
       except Exception as e:
           QMessageBox.warning(self, '加载失败', str(e))

   def _export_json(self):
       if not self._report:
           return
       p, _ = QFileDialog.getSaveFileName(self, '导出 JSON', 'report.json', 'JSON (*.json)')
       if not p:
           return
       with open(p, 'w', encoding='utf-8') as f:
           json.dump(self._report, f, indent=2, ensure_ascii=False)
       QMessageBox.information(self, '导出成功', f'已保存: {p}')

   def _export_html(self):
       if not self._report:
           return
       p, _ = QFileDialog.getSaveFileName(self, '导出 HTML', 'report.html', 'HTML (*.html)')
       if not p:
           return
       with open(p, 'w', encoding='utf-8') as f:
           f.write(self._html())
       QMessageBox.information(self, '导出成功', f'已保存: {p}')

   def _html(self) -> str:
       r = self._report
       name = r.get('name', '')
       passed = r.get('passed', 0)
       failed = r.get('failed', 0)
       rows = ''
       for s in r.get('steps', []):
           c = 'green' if s.get('status') == 'pass' else 'red'
           rows += f'<tr><td>{s.get("id","")}</td><td>{s.get("name","")}</td><td style="color:{c}">{s.get("status","").upper()}</td></tr>'
       return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>测试报告</title>
<style>
body{{font-family:sans-serif;margin:20px}}
.summary{{padding:10px;background:#f5f5f5;border-radius:5px}}
.pass{{color:green}}.fail{{color:red}}
table{{border-collapse:collapse;width:100%;margin-top:10px}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#2F5496;color:white}}
</style></head><body>
<h1>测试报告</h1>
<div class="summary">
<h2>{name}</h2>
<p class="pass">通过: {passed}</p>
<p class="fail">失败: {failed}</p>
<p>总计: {passed + failed}</p></div>
<table><tr><th>步骤</th><th>名称</th><th>状态</th></tr>{rows}</table>
</body></html>'''
