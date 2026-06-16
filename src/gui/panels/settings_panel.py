import json, os
from PySide6.QtWidgets import (
   QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox,
   QLineEdit, QSpinBox, QPushButton, QStackedWidget, QTableWidget,
   QTableWidgetItem, QFileDialog, QHeaderView, QFormLayout, QDoubleSpinBox
)
from PySide6.QtCore import Signal

SETTINGS_FILE = 'config/settings.json'

class SettingsPanel(QWidget):
   connection_changed = Signal(bool)

   def __init__(self, parent=None):
       super().__init__(parent)
       self._build_ui()
       self._load_settings()

   def _build_ui(self):
       layout = QVBoxLayout(self)

       # ========== 连接配置 ==========
       conn_group = QGroupBox('连接配置')
       conn_layout = QVBoxLayout(conn_group)

       proto_row = QHBoxLayout()
       proto_row.addWidget(QLabel('协议:'))
       self.protocol_combo = QComboBox()
       self.protocol_combo.addItems(['TCP', 'RS-422', 'CAN'])
       proto_row.addWidget(self.protocol_combo)
       proto_row.addStretch()
       conn_layout.addLayout(proto_row)

       self.config_stack = QStackedWidget()
       self.config_stack.addWidget(self._tcp_form())    # 0
       self.config_stack.addWidget(self._rs422_form())  # 1
       self.config_stack.addWidget(self._can_form())    # 2
       conn_layout.addWidget(self.config_stack)

       btn_row = QHBoxLayout()
       self.connect_btn = QPushButton('连接')
       self.disconnect_btn = QPushButton('断开')
       self.conn_status = QLabel('状态: 未连接')
       btn_row.addWidget(self.connect_btn)
       btn_row.addWidget(self.disconnect_btn)
       btn_row.addWidget(self.conn_status)
       btn_row.addStretch()
       conn_layout.addLayout(btn_row)
       layout.addWidget(conn_group)

       # ========== 配置文件路径 ==========
       files_group = QGroupBox('配置文件路径')
       files_layout = QVBoxLayout(files_group)

       self.config_table = QTableWidget(0, 3)
       self.config_table.setHorizontalHeaderLabels(['名称', '路径', '操作'])
       self.config_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
       self.config_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
       files_layout.addWidget(self.config_table)

       self.add_btn = QPushButton('+ 添加配置表')
       files_layout.addWidget(self.add_btn)
       layout.addWidget(files_group)
       layout.addStretch()

       # 信号连接
       self.protocol_combo.currentIndexChanged.connect(self.config_stack.setCurrentIndex)
       self.connect_btn.clicked.connect(self._on_connect)
       self.disconnect_btn.clicked.connect(self._on_disconnect)
       self.add_btn.clicked.connect(self._add_row)

   def _tcp_form(self):
       w = QWidget()
       f = QFormLayout(w)
       self._tcp_host = QLineEdit('192.168.117.26')
       self._tcp_port = QSpinBox()
       self._tcp_port.setRange(1, 65535)
       self._tcp_port.setValue(20004)
       self._tcp_timeout = QDoubleSpinBox()
       self._tcp_timeout.setRange(0.5, 60)
       self._tcp_timeout.setValue(5)
       f.addRow('主机:', self._tcp_host)
       f.addRow('端口:', self._tcp_port)
       f.addRow('超时(s):', self._tcp_timeout)
       return w

   def _rs422_form(self):
       w = QWidget()
       f = QFormLayout(w)
       self._rs422_port = QComboBox()
       self._rs422_port.addItems(['COM1', 'COM2', 'COM3', 'COM4'])
       self._rs422_baud = QComboBox()
       self._rs422_baud.addItems(['9600', '19200', '38400', '57600', '115200'])
       self._rs422_baud.setCurrentText('115200')
       self._rs422_parity = QComboBox()
       self._rs422_parity.addItems(['无', '奇校验', '偶校验'])
       f.addRow('串口:', self._rs422_port)
       f.addRow('波特率:', self._rs422_baud)
       f.addRow('校验位:', self._rs422_parity)
       return w

   def _can_form(self):
       w = QWidget()
       f = QFormLayout(w)
       self._can_ch = QComboBox()
       self._can_ch.addItems(['PCAN_USBBUS1', 'PCAN_USBBUS2'])
       self._can_bit = QComboBox()
       self._can_bit.addItems(['125k', '250k', '500k', '1M'])
       self._can_tx_id = QLineEdit('0x100')
       self._can_rx_id = QLineEdit('0x200')
       f.addRow('通道:', self._can_ch)
       f.addRow('比特率:', self._can_bit)
       f.addRow('发送ID:', self._can_tx_id)
       f.addRow('接收ID:', self._can_rx_id)
       return w

   def _add_row(self):
       row = self.config_table.rowCount()
       self.config_table.insertRow(row)
       self.config_table.setItem(row, 0, QTableWidgetItem(''))
       self.config_table.setItem(row, 1, QTableWidgetItem(''))
       btn_w = QWidget()
       bl = QHBoxLayout(btn_w)
       bl.setContentsMargins(0, 0, 0, 0)
       browse_btn = QPushButton('浏览')
       browse_btn.clicked.connect(lambda r=row: self._browse(r))
       del_btn = QPushButton('x')
       del_btn.clicked.connect(lambda r=row: self.config_table.removeRow(r))
       bl.addWidget(browse_btn)
       bl.addWidget(del_btn)
       self.config_table.setCellWidget(row, 2, btn_w)

   def _browse(self, row):
       path, _ = QFileDialog.getOpenFileName(self, '选择配置表', '', 'Excel (*.xlsx)')
       if path:
           self.config_table.setItem(row, 1, QTableWidgetItem(path))
           if not self.config_table.item(row, 0).text():
               name = os.path.splitext(os.path.basename(path))[0]
               self.config_table.setItem(row, 0, QTableWidgetItem(name))

   def _on_connect(self):
       self.conn_status.setText('状态: 连接中...')
       self.connection_changed.emit(True)

   def _on_disconnect(self):
       self.conn_status.setText('状态: 未连接')
       self.connection_changed.emit(False)

   def get_connection_config(self) -> dict:
       proto = self.protocol_combo.currentText()
       if proto == 'TCP':
           return {'type': 'tcp', 'host': self._tcp_host.text(), 'port': self._tcp_port.value(), 'timeout': self._tcp_timeout.value()}
       if proto == 'RS-422':
           return {'type': 'rs422', 'port': self._rs422_port.currentText(), 'baudrate': int(self._rs422_baud.currentText()), 'parity': self._rs422_parity.currentText()}
       if proto == 'CAN':
           return {'type': 'can', 'channel': self._can_ch.currentText(), 'bitrate': self._can_bit.currentText(), 'tx_id': self._can_tx_id.text(), 'rx_id': self._can_rx_id.text()}
       return {}

   def get_table_mapping(self) -> list:
       result = []
       for r in range(self.config_table.rowCount()):
           name = self.config_table.item(r, 0)
           path = self.config_table.item(r, 1)
           if name and path and name.text() and path.text():
               result.append({'name': name.text(), 'path': path.text()})
       return result

   def _load_settings(self):
       if not os.path.exists(SETTINGS_FILE):
           return
       with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
           data = json.load(f)
       # 恢复协议选择
       proto = data.get('connection', {}).get('type', 'tcp')
       idx = {'tcp': 0, 'rs422': 1, 'can': 2}.get(proto, 0)
       self.protocol_combo.setCurrentIndex(idx)
       # 恢复配置文件列表
       for item in data.get('tables', []):
           self._add_row()
           r = self.config_table.rowCount() - 1
           self.config_table.setItem(r, 0, QTableWidgetItem(item.get('name', '')))
           self.config_table.setItem(r, 1, QTableWidgetItem(item.get('path', '')))

   def save_settings(self):
       os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
       data = {'connection': self.get_connection_config(), 'tables': self.get_table_mapping()}
       with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
           json.dump(data, f, indent=2, ensure_ascii=False)
