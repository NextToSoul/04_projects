import sys
from pathlib import Path
from PySide6.QtWidgets import (
   QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
   QListWidget, QPushButton, QMessageBox, QFileDialog, QApplication
)
from PySide6.QtCore import QThread, Signal

from src.gui.panels.settings_panel import SettingsPanel
from src.gui.panels.editor_panel import EditorPanel
from src.gui.panels.monitor_panel import MonitorPanel
from src.gui.panels.report_panel import ReportPanel
from src.config.command_table import CommandTable
from src.config.telemetry_table import TelemetryTable
from src.config.inject_table import InjectTable
from src.protocol.registry import get_driver
from src.engine.test_runner import TestRunner

CONFIG = Path('项目文档/优化后excel配置表')
SEQUENCES = Path('sequences')

class RunWorker(QThread):
   finished = Signal(dict)
   error = Signal(str)

   def __init__(self, seq_file, driver, cmd_table, tm_table):
       super().__init__()
       self.seq_file = seq_file
       self.driver = driver
       self.cmd_table = cmd_table
       self.tm_table = tm_table

   def run(self):
       try:
           runner = TestRunner(self.cmd_table, self.tm_table)
           report = runner.run(self.seq_file, self.driver)
           self.finished.emit(report)
       except Exception as e:
           self.error.emit(str(e))

class MainWindow(QMainWindow):
   def __init__(self):
       super().__init__()
       self.setWindowTitle('自动化测试平台')
       self.setMinimumSize(1200, 750)

       self.cmd_table = CommandTable(str(CONFIG / '立即遥控指令配置表_优化后.xlsx'))
       self.tm_table = TelemetryTable(str(CONFIG / '遥测配置表_优化后.xlsx'))
       self.inj_table = InjectTable(str(CONFIG / '固定地址参数注入表1_优化后.xlsx'))

       self._worker = None
       self._build_ui()
       self._connect()

   def _build_ui(self):
       self.tabs = QTabWidget()

       # Tab 0: Suite
       suite = QWidget()
       sl = QVBoxLayout(suite)
       tb = QHBoxLayout()
       self.refresh_btn = QPushButton('刷新')
       tb.addWidget(self.refresh_btn)
       tb.addStretch()
       sl.addLayout(tb)
       self.suite_list = QListWidget()
       self._refresh_suite()
       sl.addWidget(self.suite_list)
       self.tabs.addTab(suite, '测试方案')

       # Tab 1-4: panels
       self.editor = EditorPanel(self.cmd_table)
       self.tabs.addTab(self.editor, '序列编辑')

       self.monitor = MonitorPanel(self.tm_table)
       self.tabs.addTab(self.monitor, '实时监控')

       self.report = ReportPanel()
       self.tabs.addTab(self.report, '报告查看')

       self.settings = SettingsPanel()
       self.tabs.addTab(self.settings, '系统设置')

       self.setCentralWidget(self.tabs)
       self.statusBar().showMessage('就绪')

       # Run toolbar
       tb_widget = QWidget()
       tb_layout = QHBoxLayout(tb_widget)
       tb_layout.setContentsMargins(5, 0, 5, 0)
       self.run_btn = QPushButton('▶ 运行')
       self.stop_btn = QPushButton('■ 停止')
       self.stop_btn.setEnabled(False)
       tb_layout.addWidget(self.run_btn)
       tb_layout.addWidget(self.stop_btn)
       tb_layout.addStretch()
       self.addToolBar('运行').addWidget(tb_widget)

   def _connect(self):
       self.suite_list.itemDoubleClicked.connect(self._open_suite)
       self.refresh_btn.clicked.connect(self._refresh_suite)
       self.run_btn.clicked.connect(self._run)
       self.stop_btn.clicked.connect(self._stop)

   def _refresh_suite(self):
       self.suite_list.clear()
       if not SEQUENCES.exists():
           return
       for f in sorted(SEQUENCES.glob('*.yaml')) + sorted(SEQUENCES.glob('*.yml')) + sorted(SEQUENCES.glob('*.json')):
           self.suite_list.addItem(f.name)

   def _open_suite(self, item):
       p = SEQUENCES / item.text()
       if p.exists():
           try:
               self.editor.load_file(str(p))
               self.tabs.setCurrentWidget(self.editor)
           except Exception as e:
               QMessageBox.warning(self, '加载失败', str(e))

   def _run(self):
       seq_file = self.editor.seq_file
       if not seq_file:
           p, _ = QFileDialog.getSaveFileName(self, '保存序列', str(SEQUENCES), 'YAML (*.yaml);;JSON (*.json)')
           if not p:
               return
           self.editor.seq_file = p
           self.editor._save()
           seq_file = p

       cfg = self.settings.get_connection_config()
       try:
           driver = get_driver(cfg.get('type', 'tcp'))
           ok = driver.open(cfg)
           if not ok:
               QMessageBox.warning(self, '连接失败', '无法连接到设备')
               return
           self.monitor.set_driver(driver)
       except Exception as e:
           QMessageBox.warning(self, '驱动错误', str(e))
           return

       self.run_btn.setEnabled(False)
       self.stop_btn.setEnabled(True)
       self.statusBar().showMessage('运行中...')

       self._worker = RunWorker(seq_file, driver, self.cmd_table, self.tm_table)
       self._worker.finished.connect(self._on_done)
       self._worker.error.connect(self._on_err)
       self._worker.start()

   def _stop(self):
       if self._worker and self._worker.isRunning():
           self._worker.terminate()
       self.run_btn.setEnabled(True)
       self.stop_btn.setEnabled(False)
       self.statusBar().showMessage('已中止')

   def _on_done(self, report):
       self.report.set_report(report)
       self.tabs.setCurrentWidget(self.report)
       msg = f'完成: {report.get("passed", 0)} 通过, {report.get("failed", 0)} 失败'
       self.statusBar().showMessage(msg)
       self.run_btn.setEnabled(True)
       self.stop_btn.setEnabled(False)

   def _on_err(self, msg):
       QMessageBox.critical(self, '运行错误', msg)
       self.run_btn.setEnabled(True)
       self.stop_btn.setEnabled(False)
       self.statusBar().showMessage('运行失败')

def main():
   app = QApplication(sys.argv)
   w = MainWindow()
   w.show()
   sys.exit(app.exec())

if __name__ == '__main__':
   main()
