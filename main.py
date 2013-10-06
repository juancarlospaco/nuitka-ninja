# -*- coding: utf-8 -*-
# PEP8:NO, LINT:OK, PY3:OK


#############################################################################
## This file may be used under the terms of the GNU General Public
## License version 2.0 or 3.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following information to ensure GNU
## General Public Licensing requirements will be met:
## http:#www.fsf.org/licensing/licenses/info/GPLv2.html and
## http:#www.gnu.org/copyleft/gpl.html.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#############################################################################


# metadata
" Nuitka Ninja "
__version__ = ' 0.4 '
__license__ = ' Apache '
__author__ = ' juancarlospaco '
__email__ = ' juancarlospaco@ubuntu.com '
__url__ = ''
__date__ = ' 10/10/2013 '
__prj__ = ' nuitka '
__docformat__ = 'html'
__source__ = ''
__full_licence__ = ''


# imports
from os import path, linesep, chmod
from datetime import datetime
from sip import setapi

try:
    from commands import getoutput
except ImportError:
    from subprocess import check_output as getoutput  # lint:ok

try:
    from os import startfile
except ImportError:
    from subprocess import Popen

from PyQt4.QtGui import (QLabel, QCompleter, QDirModel, QPushButton, QWidget,
  QFileDialog, QDockWidget, QVBoxLayout, QCursor, QLineEdit, QIcon, QGroupBox,
  QCheckBox, QGraphicsDropShadowEffect, QGraphicsBlurEffect, QColor, QComboBox,
  QMessageBox, QScrollArea, QSpinBox)

from PyQt4.QtCore import Qt, QDir, QProcess

try:
    from PyKDE4.kdeui import KTextEdit as QTextEdit
except ImportError:
    from PyQt4.QtGui import QTextEdit  # lint:ok

from ninja_ide.gui.explorer.explorer_container import ExplorerContainer
from ninja_ide.core import plugin


# API 2
(setapi(a, 2) for a in ("QDate", "QDateTime", "QString", "QTime", "QUrl",
                        "QTextStream", "QVariant"))


# constans
HELPMSG = '''
<h3>Ninja Nuitka</h3>
Nuitka is a replacement for the Python interpreter and compiles every construct
of CPython 2 and 3. It translates Python to C++.
<br><br>
258% speed performance increase for the PyStone benchmark. <br>
Stable Nuitka fully supported, if you Report a Bug, it will be fixed.
<br><br>
Nuitka Stable and Develop Packages are available for Ubuntu, Debian, Arch,
OpenSuse, Fedora, CentOS, Red Hat, Generic Linux and MS Windows.
<br><br>
Nuitka Stable and Develop Source Code are available on PyPI, GitHub, Gitorious,
Bitbucket, Google Code, and Git.Nuitka.net/Nuitka.git
<ul>
<li>Please visit <a href="http://nuitka.net">Nuitka.net</a> Home
<li>Please visit <a href="https://github.com/kayhayen/Nuitka">Nuitka GitHub</a>
<li>Please consider <a href="http://nuitka.net/pages/donations.html">Donate</a>
<li>Nuitka is idea of Kay Hayen(Germany), GUI idea of Juan Carlos(Argentina)
<br><br>
''' + ''.join((__doc__, __version__, __license__, 'by', __author__, __email__))


###############################################################################


class Main(plugin.Plugin):
    " Main Class "
    def initialize(self, *args, **kwargs):
        " Init Main Class "
        super(Main, self).initialize(*args, **kwargs)
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.readOutput)
        self.process.readyReadStandardError.connect(self.readErrors)
        self.process.finished.connect(self._process_finished)
        self.process.error.connect(self._process_finished)
        self.editor_s = self.locator.get_service('editor')
        self.completer, self.dirs = QCompleter(self), QDirModel(self)
        self.dirs.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.completer.setModel(self.dirs)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

        self.group0 = QGroupBox()
        self.group0.setTitle(' Source ')
        self.infile = QLineEdit(path.expanduser("~"))
        self.infile.setPlaceholderText(' /full/path/to/file.html ')
        self.infile.setCompleter(self.completer)
        self.open = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        self.open.setCursor(QCursor(Qt.PointingHandCursor))
        self.open.clicked.connect(lambda: self.infile.setText(str(
            QFileDialog.getOpenFileName(self.dock, "Open a File to read from",
            path.expanduser("~"), ';;'.join(['{}(*.{})'.format(e.upper(), e)
            for e in ['py', 'pyw', 'txt', '*']])))))
        self.output = QTextEdit()
        vboxg0 = QVBoxLayout(self.group0)
        for each_widget in (self.infile, self.open, self.output):
            vboxg0.addWidget(each_widget)

        self.group1 = QGroupBox()
        self.group1.setTitle(' General ')
        self.group1.setCheckable(True)
        self.group1.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.group1.graphicsEffect().setEnabled(False)
        self.group1.toggled.connect(self.toggle_gral_group)
        self.ckgrl1 = QCheckBox('Create standalone executable')
        self.ckgrl2 = QCheckBox('Use Python debug')
        self.ckgrl3 = QCheckBox('Force compilation for MS Windows')
        self.ckgrl4 = QCheckBox('When compiling, disable the console window')
        self.ckgrl5 = QCheckBox('Use link time optimizations if available')
        self.ckgrl6 = QCheckBox('Force the use of clang')
        self.ckgrl7 = QCheckBox('Allow minor devitations from Python behaviour')
        self.ckgrl8 = QCheckBox('Warnings implicit exceptions at compile time')
        self.pyver, self.jobs = QComboBox(), QSpinBox()
        self.pyver.addItems(['2.7', '2.6', '3.2', '3.3'])
        self.jobs.setValue(1)
        self.jobs.setMaximum(12)
        self.jobs.setMinimum(1)
        vboxg1 = QVBoxLayout(self.group1)
        for each_widget in (self.ckgrl1, self.ckgrl2, self.ckgrl3, self.ckgrl4,
            self.ckgrl5, self.ckgrl6, self.ckgrl7, self.ckgrl8,
            QLabel('Python Version to Target'), self.pyver,
            QLabel('Multi-Processing Parallel Workers'), self.jobs):
            vboxg1.addWidget(each_widget)
            try:
                each_widget.setToolTip(each_widget.text())
            except:
                pass

        self.group2 = QGroupBox()
        self.group2.setTitle(' Recursion Control ')
        self.ckrec0 = QCheckBox('Descend to imported modules from standard lib')
        self.ckrec1 = QCheckBox('Force not descend to any imported modules')
        self.ckrec2 = QCheckBox('Try to descend into all imported modules')
        vboxg2 = QVBoxLayout(self.group2)
        for each_widget in (self.ckrec0, self.ckrec1, self.ckrec2):
            vboxg2.addWidget(each_widget)
            each_widget.setToolTip(each_widget.text())

        self.group3 = QGroupBox()
        self.group3.setTitle(' Execution after compilation ')
        self.ckexe0 = QCheckBox('Execute created binary (or import the module)')
        self.ckexe1 = QCheckBox('When executing binary dont reset PYTHONPATH')
        vboxg2 = QVBoxLayout(self.group3)
        for each_widget in (self.ckexe0, self.ckexe1):
            vboxg2.addWidget(each_widget)
            each_widget.setToolTip(each_widget.text())

        self.group4, self.dumptree = QGroupBox(), QTextEdit()
        self.group4.setTitle(' Dump of internal tree ')
        QVBoxLayout(self.group4).addWidget(self.dumptree)

        self.group5 = QGroupBox()
        self.group5.setTitle(' Code generation ')
        self.chdmp1 = QCheckBox('Statements shall have their line numbers set')
        self.chdmp2 = QCheckBox('Disable all unnecessary Python optimization')
        vboxg5 = QVBoxLayout(self.group5)
        for each_widget in (self.chdmp1, self.chdmp2):
            vboxg5.addWidget(each_widget)
            each_widget.setToolTip(each_widget.text())

        self.group6 = QGroupBox()
        self.group6.setTitle(' Output ')
        self.outdir = QLineEdit(path.expanduser("~"))
        self.outdir.setPlaceholderText(' /full/path/to/target/directory ')
        self.outdir.setCompleter(self.completer)
        self.open2 = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        self.open2.setCursor(QCursor(Qt.PointingHandCursor))
        self.open2.clicked.connect(lambda: self.outdir.setText(str(
            QFileDialog.getExistingDirectory(self.dock, "Open Target Folder",
            path.expanduser("~")))))
        self.ckcgn2 = QCheckBox('Remove build dir after compile module or exe')
        vboxg6 = QVBoxLayout(self.group6)
        for each_widget in (QLabel('Target Output Directory'), self.outdir,
                            self.open2, self.ckcgn2):
            vboxg6.addWidget(each_widget)
            each_widget.setToolTip(each_widget.text())

        self.group7 = QGroupBox()
        self.group7.setTitle(' Debug ')
        self.ckdbg1 = QCheckBox('Execute self checks to find errors in Nuitka')
        self.ckdbg2 = QCheckBox('Keep debug info in resulting file')
        self.ckdbg3 = QCheckBox('Traced execution output')
        self.ckdbg4 = QCheckBox('Allow compile edited C++ file, debug changes')
        self.ckdbg5 = QCheckBox('Use experimental features')
        vboxg7 = QVBoxLayout(self.group7)
        for each_widget in (self.ckdbg1, self.ckdbg2, self.ckdbg3,
                            self.ckdbg4, self.ckdbg5):
            vboxg7.addWidget(each_widget)
            each_widget.setToolTip(each_widget.text())

        self.group8 = QGroupBox()
        self.group8.setTitle(' Tracing ')
        self.cktrc1 = QCheckBox('Show Scons in non-quiet mode, showing command')
        self.cktrc2 = QCheckBox('Show Progress information and statistics')
        self.cktrc3 = QCheckBox('Show Verbose output details')
        vboxg8 = QVBoxLayout(self.group8)
        for each_widget in (self.cktrc1, self.cktrc2, self.cktrc3):
            vboxg8.addWidget(each_widget)
            each_widget.setToolTip(each_widget.text())

        self.group9 = QGroupBox()
        self.group9.setTitle(' Extras ')
        self.group9.setCheckable(True)
        self.group9.toggled.connect(self.group9.hide)
        self.nice = QSpinBox()
        self.nice.setValue(20)
        self.nice.setMaximum(20)
        self.nice.setMinimum(0)
        self.ckxtr1 = QCheckBox('Open Target Directory later')
        self.ckxtr2 = QCheckBox('Save a LOG file to target later')
        self.ckxtr3 = QCheckBox('Save SH Bash script to reproduce Nuitka build')
        try:
            self.vinfo = QLabel('<center> <b> Nuitka Backend Version: </b>' +
                            getoutput('nuitka --version',).strip())
        except:
            self.vinfo = QLabel('<b>Warning: Failed to query Nuitka Backend!')
        vboxg9 = QVBoxLayout(self.group9)
        for each_widget in (QLabel('Backend CPU Priority'), self.nice,
                            self.ckxtr1, self.ckxtr2, self.ckxtr3, self.vinfo):
            vboxg9.addWidget(each_widget)

        self.group10 = QGroupBox()
        self.group10.setTitle(' Documentation ')
        self.group10.setCheckable(True)
        self.group10.toggled.connect(self.group10.hide)
        vboxg10 = QVBoxLayout(self.group10)
        for each_widget in (QLabel('''<a href=
            "file:///usr/share/doc/nuitka/README.pdf.gz">
            <small><center> Nuitka User Documentation Local PDF </a>'''),
            QLabel('''<a href=
            "file:///usr/share/doc/nuitka/Developer_Manual.pdf.gz">
            <small><center> Nuitka Developer Documentation Local PDF </a>'''),
            QLabel('''<a href="http://nuitka.net/doc/user-manual.html">
            <small><center> Nuitka User Documentation On Line HTML </a>'''),
            QLabel('''<a href="http://nuitka.net/doc/developer-manual.html">
            <small><center> Nuitka Developer Documentation On Line HTML </a>''')
             ):
            vboxg10.addWidget(each_widget)
            each_widget.setOpenExternalLinks(True)
            each_widget.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

        [a.setChecked(True) for a in (self.ckgrl1, self.ckgrl2, self.ckgrl4,
            self.ckgrl5, self.ckgrl6, self.ckgrl7, self.ckgrl8, self.ckrec0,
            self.ckrec1, self.ckrec2, self.ckexe1, self.ckcgn2, self.ckdbg1,
            self.ckdbg3, self.ckdbg4, self.ckdbg5, self.cktrc1, self.cktrc2,
            self.cktrc3, self.ckxtr1, self.ckxtr2, self.ckxtr3,)]

        self.button = QPushButton(QIcon.fromTheme("face-cool"),
                                  'Compile Python')
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        self.button.setMinimumSize(100, 50)
        self.button.clicked.connect(self.run)
        glow = QGraphicsDropShadowEffect(self)
        glow.setOffset(0)
        glow.setBlurRadius(99)
        glow.setColor(QColor(99, 255, 255))
        self.button.setGraphicsEffect(glow)

        class TransientWidget(QWidget):
            ' persistant widget thingy '
            def __init__(self, widget_list):
                ' init sub class '
                super(TransientWidget, self).__init__()
                vbox = QVBoxLayout(self)
                for each_widget in widget_list:
                    vbox.addWidget(each_widget)

        tw = TransientWidget((
            QLabel('<b>Python Code to Binary Executable Compiler'), self.group0,
            self.group6, self.group1, self.group2, self.group3, self.group4,
            self.group5, self.group7, self.group8, self.group9, self.group10,
            self.button, ))
        self.scrollable, self.dock = QScrollArea(), QDockWidget()
        self.scrollable.setWidgetResizable(True)
        self.scrollable.setWidget(tw)
        self.dock.setWindowTitle(__doc__)
        self.dock.setStyleSheet('QDockWidget::title{text-align: center;}')
        self.dock.setWidget(self.scrollable)
        ExplorerContainer().addTab(self.dock, "Nuitka")
        QPushButton(QIcon.fromTheme("help-about"), 'About', self.dock
          ).clicked.connect(lambda: QMessageBox.information(self.dock, __doc__,
            HELPMSG))

    def run(self):
        ' run the compile '
        target = path.abspath(str(self.infile.text()).strip())
        self.button.setDisabled(True)
        self.output.clear()
        self.output.show()
        self.output.setFocus()
        self.output.append(self.formatInfoMsg('INFO:{}'.format(datetime.now())))
        self.output.append(self.formatInfoMsg(' INFO: Dumping Internal Tree'))
        try:
            self.dumptree.setPlainText(
                getoutput('nuitka --dump-tree {}'.format(target)))
            self.dumptree.setMinimumSize(100, 500)
        except:
            self.output.append(self.formatErrorMsg('ERROR:FAIL: Internal Tree'))
        self.output.append(self.formatInfoMsg(' INFO: OK: Parsing Arguments'))
        cmd = ' '.join(('nice --adjustment={} nuitka'.format(self.nice.value()),

            # output
            '--remove-output' if self.ckcgn2.isChecked() is True else '',

            # general
            '--exe' if self.ckgrl1.isChecked() is True else '',
            '--python-debug' if self.ckgrl2.isChecked() is True else '',
            '--verbose' if self.cktrc3.isChecked() is True else '',
            '--windows-target' if self.ckgrl3.isChecked() is True else '',
            '--windows-disable-console' if self.ckgrl4.isChecked() is True else '',
            '--lto' if self.ckgrl5.isChecked() is True else '',
            '--clang' if self.ckgrl6.isChecked() is True else '',
            '--improved' if self.ckgrl7.isChecked() is True else '',
            '--warn-implicit-exceptions' if self.ckgrl8.isChecked() is True else '',

            # recursion control
            '--recurse-stdlib' if self.ckrec0.isChecked() is True else '',
            '--recurse-none' if self.ckrec1.isChecked() is True else '',
            '--recurse-all' if self.ckrec2.isChecked() is True else '',

            # execution after compilation
            '--execute' if self.ckexe0.isChecked() is True else '',
            '--keep-pythonpath' if self.ckexe1.isChecked() is True else '',

            # code generation
            '--code-gen-no-statement-lines' if self.chdmp1.isChecked() is True else '',
            '--no-optimization' if self.chdmp2.isChecked() is True else '',

            # debug
            '--debug' if self.ckdbg1.isChecked() is True else '',
            '--unstripped' if self.ckdbg2.isChecked() is True else '',
            '--trace-execution' if self.ckdbg3.isChecked() is True else '',
            '--c++-only' if self.ckdbg4.isChecked() is True else '',
            '--experimental' if self.ckdbg5.isChecked() is True else '',

            # tracing
            '--show-scons' if self.cktrc1.isChecked() is True else '',
            '--show-progress' if self.cktrc2.isChecked() is True else '',
            '--verbose' if self.cktrc3.isChecked() is True else '',

            # non boolean parametrization
            '--python-version={}'.format(self.pyver.currentText()),
            '--jobs={}'.format(self.jobs.value()),
            '--output-dir="{}"'.format(self.outdir.text()),
            target))
        self.output.append(self.formatInfoMsg(' INFO: Command: {}'.format(cmd)))
        self.output.append(self.formatInfoMsg(' INFO: OK: Starting to Compile'))
        self.process.start(cmd)
        if not self.process.waitForStarted():
            self.output.append(self.formatErrorMsg('ERROR: FAIL: Compile Fail'))
            self.output.append(self.formatErrorMsg('ERROR:FAIL:{}'.format(cmd)))
            self.button.setEnabled(True)
            return
        # write a .sh bash script file on target
        if self.ckxtr3.isChecked() is True:
            sh_file = 'nuitka_compile_python_to_cpp.sh'
            with open(path.join(str(self.outdir.text()), sh_file), 'w') as _sh:
                self.output.append(self.formatInfoMsg('''INFO: OK: Writing Bash:
                    {}'''.format(sh_file)))
                _sh.write('#!/usr/bin/env bash {}{}'.format(linesep, cmd))
                _sh.close()
            self.output.append(self.formatInfoMsg('INFO: OK: Bash chmod: 775'))
            try:
                chmod(path.join(str(self.outdir.text()), sh_file), 0775)  # Py2
            except:
                chmod(path.join(str(self.outdir.text()), sh_file), 0o775)  # Py3

    def _process_finished(self):
        """sphinx-build finished sucessfully"""
        self.output.append(self.formatInfoMsg('INFO:{}'.format(datetime.now())))
        if self.ckxtr2.isChecked() is True:
            log_file = 'nuitka_ninja.log'
            with open(path.join(str(self.outdir.text()), log_file), 'w') as log:
                self.output.append(self.formatInfoMsg('''INFO: OK: Writing LOG:
                    {}'''.format(log_file)))
                log.write(self.output.toPlainText())
        if self.ckxtr1.isChecked() is True:
            try:
                startfile(path.abspath(str(self.outdir.text())))
            except:
                Popen(["xdg-open", path.abspath(str(self.outdir.text()))])
        self.button.setDisabled(False)
        self.output.show()
        self.output.setFocus()
        self.output.selectAll()

    def toggle_gral_group(self):
        ' toggle on or off the checkboxes '
        if self.group1.isChecked() is True:
            [a.setChecked(True) for a in (self.ckgrl1, self.ckgrl2, self.ckgrl4,
            self.ckgrl5, self.ckgrl6, self.ckgrl7, self.ckgrl8)]
            self.group1.graphicsEffect().setEnabled(False)
        else:
            [a.setChecked(False) for a in (self.ckgrl1, self.ckgrl2,
            self.ckgrl4, self.ckgrl5, self.ckgrl6, self.ckgrl7, self.ckgrl8)]
            self.group1.graphicsEffect().setEnabled(True)

    def readOutput(self):
        """Read and append sphinx-build output to the logBrowser"""
        self.output.append(str(self.process.readAllStandardOutput()))

    def readErrors(self):
        """Read and append sphinx-build errors to the logBrowser"""
        self.output.append(self.formatErrorMsg(str(
                                        self.process.readAllStandardError())))

    def formatErrorMsg(self, msg):
        """Format error messages in red color"""
        return self.formatMsg(msg, 'red')

    def formatInfoMsg(self, msg):
        """Format informative messages in blue color"""
        return self.formatMsg(msg, 'green')

    def formatMsg(self, msg, color):
        """Format message with the given color"""
        return '<font color="{}">{}</font>'.format(color, msg)


###############################################################################


if __name__ == "__main__":
    print(__doc__)
