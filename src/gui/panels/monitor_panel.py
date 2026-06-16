import time
from collections import deque
from PySide6.QtWidgets import (
   QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTreeWidget,
   QTreeWidgetItem, QTableWidget, QTableWidgetItem, QTextEdit,
   QPushButton, QLabel, QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from src.codec.frame_decoder import decode_telemetry_frame

APID_MAP = {'0525': '常规包1(SlowFrame)', '0526': '常规包2(SlowFrame2)'}

class MonitorPanel(QWidget):
   def __init__(self, tm_table, parent=None):
       super().__init__(parent)
       self.tm_table = tm_table
       self.driver = None
       self._queue = deque()
       self._watched = {}
       self._values = {}
       self._build_ui()
       self._timer = QTimer()
       self._timer.timeout.connect(self._process)
       self._timer.start(100)

   def _build_ui(self):
       layout = QVBoxLayout(self)

       tb = QHBoxLayout()
       self.conn_btn = QPushButton('连接')
       self.status = QLabel('未连接')
       self.clear_btn = QPushButton('清空日志')
       tb.addWidget(self.conn_btn)
       tb.addWidget(self.status)
       tb.addStretch()
       tb.addWidget(self.clear_btn)
       layout.addLayout(tb)

       split = QSplitter(Qt.Horizontal)

       left = QWidget()
       lv = QVBoxLayout(left)
       lv.setContentsMargins(0, 0, 0, 0)
       self.tree = QTreeWidget()
       self.tree.setHeaderLabels(['参数', 'ID'])
       self.tree.setMinimumWidth(220)
       self._build_tree()
       lv.addWidget(self.tree)
       split.addWidget(left)

       right = QWidget()
       rl = QVBoxLayout(right)
       rl.setContentsMargins(0, 0, 0, 0)
       self.table = QTableWidget(0, 4)
       self.table.setHorizontalHeaderLabels(['参数ID', '参数名称', '当前值', '单位'])
       self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
       rl.addWidget(self.table, 2)

       self.log = QTextEdit()
       self.log.setReadOnly(True)
       self.log.setMaximumBlockCount(500)
       rl.addWidget(self.log, 1)

       split.addWidget(right)
       split.setSizes([280, 620])
       layout.addWidget(split)

       self.tree.itemChanged.connect(self._on_check)
       self.conn_btn.clicked.connect(self._toggle)
       self.clear_btn.clicked.connect(self.log.clear)

   def _build_tree(self):
       if not self.tm_table:
           return
       for pkg in ['常规包1(SlowFrame)', '常规包2(SlowFrame2)', '查询包1(QueryFrame)']:
           try:
               params = self.tm_table.get_package(pkg)
           except KeyError:
               continue
           top = QTreeWidgetItem([pkg, ''])
           top.setFlags(top.flags() & ~Qt.ItemIsUserCheckable)
           self.tree.addTopLevelItem(top)
           for p in params:
               pid = str(p.get('遥测代号', '') or '').strip()
               pname = str(p.get('参数名称', '') or '').strip()
               if not pid:
                   continue
               item = QTreeWidgetItem([pname, pid])
               item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
               item.setCheckState(0, Qt.Unchecked)
               top.addChild(item)

   def _on_check(self, item, col):
       if col != 0:
           return
       pid = item.text(1)
       if not pid:
           return
       if item.checkState(0) == Qt.Checked:
           if pid not in self._watched:
               self._watched[pid] = item
               self._add_row(pid, item.text(0))
       else:
           self._watched.pop(pid, None)
           self._del_row(pid)

   def _add_row(self, pid, name):
       r = self.table.rowCount()
       self.table.insertRow(r)
       self.table.setItem(r, 0, QTableWidgetItem(pid))
       self.table.setItem(r, 1, QTableWidgetItem(name))
       self.table.setItem(r, 2, QTableWidgetItem('--'))
       self.table.setItem(r, 3, QTableWidgetItem(''))

   def _del_row(self, pid):
       for r in range(self.table.rowCount()):
           if self.table.item(r, 0).text() == pid:
               self.table.removeRow(r)
               return

   def set_driver(self, driver):
       self.driver = driver
       if driver:
           driver.set_receive_callback(self._on_rx)

   def _on_rx(self, data):
       self._queue.append(data)

   def _process(self):
       while self._queue:
           raw = self._queue.popleft()
           self._log(raw, is_rx=True)
           if not self.tm_table or len(raw) < 10:
               continue
           apid = raw[2:4].hex()
           pkg = APID_MAP.get(apid, '')
           if not pkg:
               continue
           decoded = decode_telemetry_frame(self.tm_table, raw, pkg, resolve_enum=True)
           for pid, val in decoded.items():
               if pid in self._watched:
                   self._values[pid] = str(val)
                   self._update_cell(pid, str(val))

   def _update_cell(self, pid, val):
       for r in range(self.table.rowCount()):
           if self.table.item(r, 0).text() == pid:
               self.table.item(r, 2).setText(val)
               return

   def _log(self, data, is_rx):
       prefix = 'RX' if is_rx else 'TX'
       ts = time.strftime('%H:%M:%S')
       h = data.hex().upper()
       self.log.append(f'[{ts}] {prefix} {h[:64]}')

   def _toggle(self):
       if self.driver and self.driver.is_open():
           self.driver.close()
           self.conn_btn.setText('连接')
           self.status.setText('未连接')
       elif self.driver:
           ok = self.driver.open({'host': '192.168.117.26', 'port': 20004, 'timeout': 5})
           if ok:
               self.conn_btn.setText('断开')
               self.status.setText('已连接')
               self._log(b'connected', is_rx=False)
           else:
               self.status.setText('连接失败')
