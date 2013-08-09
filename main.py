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
" Ninja Nuitka "
__version__ = ' 0.1 '
__license__ = ' Apache '
__author__ = ' juancarlospaco '
__email__ = ' juancarlospaco@ubuntu.com '
__url__ = ''
__date__ = ' 15/08/2013 '
__prj__ = ' nuitka '
__docformat__ = 'html'
__source__ = ''
__full_licence__ = ''


# imports
from os import path
from sip import setapi
from subprocess import check_output as getoutput
try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen  # lint:ok


from PyQt4.QtGui import (QLabel, QCompleter, QDirModel, QPushButton, QWidget,
  QFileDialog, QDockWidget, QVBoxLayout, QCursor, QLineEdit, QIcon, QGroupBox,
  QCheckBox, QGraphicsDropShadowEffect, QGraphicsBlurEffect, QColor, QComboBox,
  QApplication, QMessageBox, QScrollArea, QSpinBox)

from PyQt4.QtCore import Qt, QDir

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
Stable Nuitka is fully supported, if you find a Bug, it will be fixed.
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
        ec = ExplorerContainer()
        super(Main, self).initialize(*args, **kwargs)

        self.editor_s = self.locator.get_service('editor')
        # directory auto completer
        self.completer, self.dirs = QCompleter(self), QDirModel(self)
        self.dirs.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.completer.setModel(self.dirs)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

        self.group0 = QGroupBox()
        self.group0.setTitle(' Source ')
        self.source = QComboBox()
        self.source.addItems(['Clipboard', 'Local File', 'Remote URL', 'Ninja'])
        self.source.currentIndexChanged.connect(self.on_source_changed)
        self.infile = QLineEdit(path.expanduser("~"))
        self.infile.setPlaceholderText(' /full/path/to/file.html ')
        self.infile.setCompleter(self.completer)
        self.open = QPushButton(QIcon.fromTheme("folder-open"), 'Open')
        self.open.setCursor(QCursor(Qt.PointingHandCursor))
        self.open.clicked.connect(lambda: self.infile.setText(str(
            QFileDialog.getOpenFileName(self.dock, "Open a File to read from",
            path.expanduser("~"), ';;'.join(['{}(*.{})'.format(e.upper(), e)
            for e in ['py', 'pyw', 'txt', '*']])))))
        self.inurl = QLineEdit('http://www.')
        self.inurl.setPlaceholderText('http://www.full/url/to/remote/file.html')
        self.output = QTextEdit()
        vboxg0 = QVBoxLayout(self.group0)
        for each_widget in (self.source, self.infile, self.open, self.inurl,
            self.output, ):
            vboxg0.addWidget(each_widget)
        [a.hide() for a in iter((self.infile, self.open, self.inurl))]

        self.group1 = QGroupBox()
        self.group1.setTitle(' General ')
        self.group1.setCheckable(True)
        self.group1.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.group1.graphicsEffect().setEnabled(False)
        self.group1.toggled.connect(self.toggle_gral_group)
        self.ckgrl1 = QCheckBox('Create standalone executable')
        self.ckgrl2 = QCheckBox('Use debug version')
        self.ckgrl3 = QCheckBox('Force compilation for MS Windows')
        self.ckgrl4 = QCheckBox('When compiling, disable the console window')
        self.ckgrl5 = QCheckBox('Use link time optimizations if available')
        self.ckgrl6 = QCheckBox('Force the use of clang')
        self.ckgrl7 = QCheckBox('Allow minor devitations from Python behaviour')
        self.ckgrl8 = QCheckBox('Warnings implicit exceptions at compile time')
        self.pyver = QComboBox()
        self.pyver.addItems(['2.7', '2.6', '3.2', '3.3'])
        self.jobs = QSpinBox()
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
        self.nice = QSpinBox()
        self.nice.setValue(20)
        self.nice.setMaximum(20)
        self.nice.setMinimum(0)
        self.ckxtr1 = QCheckBox('Open Target Directory later')
        self.ckxtr2 = QCheckBox('Save a LOG file to target later')
        try:
            self.vinfo = QLabel('<center> <b> Nuitka Backend Version: </b>' +
                            getoutput('nuitka --version', shell=True).strip())
        except:
            self.vinfo = QLabel('<b>Warning: Failed to query Nuitka Backend!')
        vboxg9 = QVBoxLayout(self.group9)
        for each_widget in (QLabel('Backend CPU Priority'), self.nice,
                            self.ckxtr1, self.ckxtr2, self.vinfo):
            vboxg9.addWidget(each_widget)

        [a.setChecked(True) for a in (self.ckgrl1, self.ckgrl2, self.ckgrl4,
            self.ckgrl5, self.ckgrl6, self.ckgrl7, self.ckgrl8, self.ckrec1,
            self.ckexe1, self.ckcgn2, self.ckdbg1, self.ckdbg3, self.ckdbg4,
            self.ckdbg5, self.cktrc1, self.cktrc2, self.cktrc3, self.ckxtr2)]

        self.button = QPushButton(QIcon.fromTheme("face-cool"), 'Compile Python')
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        self.button.setMinimumSize(100, 50)
        self.button.clicked.connect(self.run)

        def must_glow(widget_list):
            ' apply an glow effect to the widget '
            for glow, each_widget in enumerate(widget_list):
                try:
                    if each_widget.graphicsEffect() is None:
                        glow = QGraphicsDropShadowEffect(self)
                        glow.setOffset(0)
                        glow.setBlurRadius(99)
                        glow.setColor(QColor(99, 255, 255))
                        each_widget.setGraphicsEffect(glow)
                        glow.setEnabled(True)
                except:
                    pass

        must_glow((self.button, ))

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
            self.group5, self.group7, self.group8, self.group9, self.button, ))
        self.scrollable = QScrollArea()
        self.scrollable.setWidgetResizable(True)
        self.scrollable.setWidget(tw)
        self.dock = QDockWidget()
        self.dock.setWindowTitle(__doc__)
        self.dock.setStyleSheet('QDockWidget::title{text-align: center;}')
        self.dock.setMinimumWidth(350)
        self.dock.setWidget(self.scrollable)
        ec.addTab(self.dock, "Nuitka")
        QPushButton(QIcon.fromTheme("help-about"), 'About', self.dock
          ).clicked.connect(lambda: QMessageBox.information(self.dock, __doc__,
            HELPMSG))

    def run(self):
        ' run the string replacing '
        if self.source.currentText() == 'Local File':
            with open(path.abspath(str(self.infile.text()).strip()), 'r') as f:
                txt = f.read()
        elif self.source.currentText() == 'Remote URL':
            txt = urlopen(str(self.inurl.text()).strip()).read()
        elif  self.source.currentText() == 'Clipboard':
            txt = str(self.output.toPlainText()) if str(self.output.toPlainText()) is not '' else str(QApplication.clipboard().text())
        else:
            txt = self.editor_s.get_text()
        self.output.clear()
        txt = txt.lower() if self.chdmp1.isChecked() is True else txt
        self.output.show()
        self.output.setFocus()
        self.output.selectAll()

    def on_source_changed(self):
        ' do something when the desired source has changed '
        if self.source.currentText() == 'Local File':
            self.open.show()
            self.infile.show()
            self.inurl.hide()
            self.output.hide()
        elif  self.source.currentText() == 'Remote URL':
            self.inurl.show()
            self.open.hide()
            self.infile.hide()
            self.output.hide()
        elif  self.source.currentText() == 'Clipboard':
            self.output.show()
            self.open.hide()
            self.infile.hide()
            self.inurl.hide()
            self.output.setText(QApplication.clipboard().text())
        else:
            self.output.show()
            self.open.hide()
            self.infile.hide()
            self.inurl.hide()
            self.output.setText(self.editor_s.get_text())

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


###############################################################################


if __name__ == "__main__":
    print(__doc__)
