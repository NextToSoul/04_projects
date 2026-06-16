import json, os
from PySide6.QtWidgets import (
   QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget,
   QPushButton, QScrollArea, QFormLayout, QLineEdit, QComboBox,
   QLabel, QDoubleSpinBox, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from src.engine.sequence_loader import SequenceLoader

class EditorPanel(QWidget):
   def __init__(self, cmd_table, parent=None):
       super().__init__(parent)
       self.cmd_table = cmd_table
       self.loader = SequenceLoader()
       self.seq_file = None
       self.seq_data = {'name': '', 'steps': []}
       self._modified = False
       self._build_ui()
       self._on_step_selected(-1)

   def _build_ui(self):
       layout = QVBoxLayout(self)

       # Toolbar
       tb = QHBoxLayout()
       self.open_btn = QPushButton('打开')
       self.save_btn = QPushButton('保存')
       self.new_btn = QPushButton('新建')
       tb.addWidget(self.open_btn)
       tb.addWidget(self.save_btn)
       tb.addWidget(self.new_btn)
       tb.addStretch()
       layout.addLayout(tb)

       # Splitter: step list (left) + props (right)
       split = QSplitter(Qt.Horizontal)

       # Left: step list
       left = QWidget()
       lv = QVBoxLayout(left)
       lv.setContentsMargins(0, 0, 0, 0)
       self.step_list = QListWidget()
       self.step_list.setMinimumWidth(180)
       lv.addWidget(self.step_list)

       sb = QHBoxLayout()
       self.add_btn = QPushButton('+')
       self.del_btn = QPushButton('-')
       sb.addWidget(self.add_btn)
       sb.addWidget(self.del_btn)
       lv.addLayout(sb)

       mb = QHBoxLayout()
       self.up_btn = QPushButton('▲')
       self.down_btn = QPushButton('▼')
       mb.addWidget(self.up_btn)
       mb.addWidget(self.down_btn)
       lv.addLayout(mb)
       split.addWidget(left)

       # Right: scrollable property form
       scroll = QScrollArea()
       scroll.setWidgetResizable(True)
       self.form = QWidget()
       self.fl = QFormLayout(self.form)

       self.id_edit = QLineEdit()
       self.name_edit = QLineEdit()
       self.cmd_combo = QComboBox()
       self._fill_cmd()
       self.params_edit = QLineEdit()
       self.type_label = QLabel('')
       self.timeout_spin = QDoubleSpinBox()
       self.timeout_spin.setRange(0.5, 120)
       self.timeout_spin.setValue(5)
       self.fail_combo = QComboBox()
       self.fail_combo.addItems(['continue', 'skip', 'abort'])

       self.fl.addRow('ID:', self.id_edit)
       self.fl.addRow('名称:', self.name_edit)
       self.fl.addRow('指令:', self.cmd_combo)
       self.fl.addRow('参数:', self.params_edit)
       self.fl.addRow('值类型:', self.type_label)
       self.fl.addRow('超时(s):', self.timeout_spin)
       self.fl.addRow('失败:', self.fail_combo)

       scroll.setWidget(self.form)
       split.addWidget(scroll)
       split.setSizes([200, 500])
       layout.addWidget(split)

       # Signals
       self.step_list.currentRowChanged.connect(self._on_step_selected)
       self.add_btn.clicked.connect(self._add_step)
       self.del_btn.clicked.connect(self._del_step)
       self.up_btn.clicked.connect(self._move_up)
       self.down_btn.clicked.connect(self._move_down)
       self.open_btn.clicked.connect(self._open)
       self.save_btn.clicked.connect(self._save)
       self.new_btn.clicked.connect(self._new)
       self.id_edit.editingFinished.connect(self._sync_step)
       self.name_edit.editingFinished.connect(self._sync_step)
       self.cmd_combo.currentIndexChanged.connect(self._on_cmd_changed)
       self.params_edit.editingFinished.connect(self._sync_step)
       self.timeout_spin.valueChanged.connect(self._sync_step)
       self.fail_combo.currentIndexChanged.connect(self._sync_step)

   def _fill_cmd(self):
       if not self.cmd_table:
           return
       for cmd in self.cmd_table.all():
           name = str(cmd.get('指令代号', '') or '').strip()
           if name:
               self.cmd_combo.addItem(name)

   def _add_step(self):
       idx = len(self.seq_data['steps'])
       sid = 'S' + str(idx + 1).zfill(2)
       self.seq_data['steps'].append({'id': sid, 'command': ''})
       self.step_list.addItem(sid)
       self.step_list.setCurrentRow(self.step_list.count() - 1)
       self._modified = True

   def _del_step(self):
       r = self.step_list.currentRow()
       if r < 0:
           return
       self.step_list.takeItem(r)
       del self.seq_data['steps'][r]
       self._modified = True

   def _move_up(self):
       r = self.step_list.currentRow()
       if r <= 0:
           return
       item = self.step_list.takeItem(r)
       self.step_list.insertItem(r - 1, item)
       self.step_list.setCurrentRow(r - 1)
       self.seq_data['steps'][r], self.seq_data['steps'][r - 1] = \
           self.seq_data['steps'][r - 1], self.seq_data['steps'][r]
       self._modified = True

   def _move_down(self):
       r = self.step_list.currentRow()
       if r < 0 or r >= self.step_list.count() - 1:
           return
       item = self.step_list.takeItem(r)
       self.step_list.insertItem(r + 1, item)
       self.step_list.setCurrentRow(r + 1)
       self.seq_data['steps'][r], self.seq_data['steps'][r + 1] = \
           self.seq_data['steps'][r + 1], self.seq_data['steps'][r]
       self._modified = True

   def _on_step_selected(self, row):
       enable = 0 <= row < len(self.seq_data['steps'])
       for w in [self.id_edit, self.name_edit, self.cmd_combo,
                 self.params_edit, self.timeout_spin, self.fail_combo]:
           w.setEnabled(enable)
       if not enable:
           for w in [self.id_edit, self.name_edit, self.params_edit]:
               w.clear()
           self.cmd_combo.setCurrentIndex(-1)
           self.type_label.setText('')
           return
       step = self.seq_data['steps'][row]
       self.id_edit.setText(step.get('id', ''))
       self.name_edit.setText(step.get('name', ''))
       cmd = step.get('command', '')
       ci = self.cmd_combo.findText(cmd)
       if ci >= 0:
           self.cmd_combo.setCurrentIndex(ci)
       self.params_edit.setText(str(step.get('params', '')))
       to = step.get('expect', [{}])[0].get('timeout', 5) if step.get('expect') else 5
       self.timeout_spin.setValue(to)
       fc = step.get('on_failure', '')
       fi = self.fail_combo.findText(fc)
       if fi >= 0:
           self.fail_combo.setCurrentIndex(fi)
       self._update_type(cmd)

   def _on_cmd_changed(self, idx):
       self._update_type(self.cmd_combo.currentText())
       self._sync_step()

   def _update_type(self, cmd_name):
       if not cmd_name or not self.cmd_table:
           self.type_label.setText('')
           return
       try:
           cmd = self.cmd_table.lookup(cmd_name)
           self.type_label.setText(str(cmd.get('值类型', '') or ''))
       except KeyError:
           self.type_label.setText('(未知)')

   def _sync_step(self):
       r = self.step_list.currentRow()
       if r < 0:
           return
       step = self.seq_data['steps'][r]
       step['id'] = self.id_edit.text()
       step['name'] = self.name_edit.text()
       step['command'] = self.cmd_combo.currentText()
       p = self.params_edit.text()
       if p:
           step['params'] = p
       elif 'params' in step:
           del step['params']
       step['on_failure'] = self.fail_combo.currentText()
       if 'expect' not in step:
           step['expect'] = [{}]
       step['expect'][0]['timeout'] = self.timeout_spin.value()
       item = self.step_list.item(r)
       if item:
           item.setText(step['id'])
       self._modified = True

   def _open(self):
       path, _ = QFileDialog.getOpenFileName(
           self, '打开序列', '', '序列 (*.yaml *.yml *.json)')
       if not path:
           return
       try:
           self.seq_data = self.loader.load(path)
           self.seq_file = path
           self._refresh()
           self._modified = False
       except Exception as e:
           QMessageBox.warning(self, '加载失败', str(e))

   def _save(self):
       if not self.seq_file:
           path, _ = QFileDialog.getSaveFileName(
               self, '保存序列', '', 'YAML (*.yaml);;JSON (*.json)')
           if not path:
               return
           self.seq_file = path
       self._sync_step()
       with open(self.seq_file, 'w', encoding='utf-8') as f:
           if self.seq_file.endswith(('.yaml', '.yml')):
               try:
                   import yaml
                   yaml.dump(self.seq_data, f, allow_unicode=True,
                             default_flow_style=False, sort_keys=False)
                   return
               except ImportError:
                   pass
           json.dump(self.seq_data, f, indent=2, ensure_ascii=False)
       self._modified = False

   def _new(self):
       self.seq_data = {'name': '新建测试', 'steps': []}
       self.seq_file = None
       self._refresh()
       self._modified = False

   def _refresh(self):
       self.step_list.blockSignals(True)
       self.step_list.clear()
       for step in self.seq_data.get('steps', []):
           self.step_list.addItem(step.get('id', '?'))
       self.step_list.blockSignals(False)
       self._on_step_selected(-1)

   def get_sequence(self) -> dict:
       return self.seq_data

   def is_modified(self) -> bool:
       return self._modified
