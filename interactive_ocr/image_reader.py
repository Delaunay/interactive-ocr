import sys
import os

import PyQt5.Qt as Qt
import PyQt5.QtGui as QtGui
import PIL.ImageQt as ImageQt
import pytesseract
import numpy
import traceback
import cv2
import pandas

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QDockWidget, QStatusBar
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QErrorMessage, QFileDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QToolBar, QPushButton
from PyQt5.Qt import QPixmap, QRect, QPainter, QColor, QBrush, QPen

from PIL import Image

_base = os.path.dirname(os.path.realpath(__file__))
pytesseract.pytesseract.tesseract_cmd = f'{_base}/tesseract-Win64/tesseract.exe'

DEFAULT_FOLDER = r'images'
DEFAULT_EXCEL = 'extracted.xlsx'


class ImageSelector(QLabel):
    """Simple Image with a region selector"""
    newSelection = pyqtSignal(name='newSelection')

    def __init__(self):
        super(ImageSelector, self).__init__()
        self.selecting = False
        self.selection = QRect()
        self.selected = False
        self.setMinimumSize(1240, 680)

    def paintEvent(self, event: QtGui.QPaintEvent):
        super().paintEvent(event)

        if self.selecting:
            painter = QPainter(self)
            painter.setPen(QPen(QBrush(QColor(0, 0, 0, 180)), 1, Qt.Qt.DashLine))
            painter.setBrush(QBrush(QColor(255, 255, 255, 120)))
            painter.drawRect(self.selection)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == Qt.Qt.LeftButton:
            self.selecting = True
            self.selection.setTopLeft(event.pos())
            self.selection.setBottomRight(event.pos())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self.selecting:
            self.selection.setBottomRight(event.pos())
            self.repaint()

    def mouseReleaseEvent(self, a0: QtGui.QMouseEvent):
        if self.selecting:
            self.selecting = False
            self.newSelection.emit()

    def selectedImage(self):
        pix = self.pixmap().copy(self.selection)
        return ImageQt.fromqpixmap(pix)


def getFolder(parent):
    return QFileDialog.getExistingDirectory(
        parent,
        'Dossier d\'image',
        DEFAULT_FOLDER,
        QFileDialog.ShowDirsOnly)


def getFile(parent):
    return QFileDialog.getSaveFileName(
        parent,
        'Fichier Excel',
        DEFAULT_EXCEL)


class Window(QMainWindow):
    def log(self, message):
        print(message)
        self.status.showMessage(message, 5000)

    def __init__(self):
        super(Window, self).__init__()
        # >>> Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        # <<<

        self.label = ImageSelector()

        # >>> Image display
        self.area = QScrollArea()
        self.area.setWidget(self.label)
        # <<<

        # >>> File system View
        folder = getFolder(self)
        self.log(f'Opening {folder}')
        self.files = QFileSystemModel()
        self.files.setRootPath(folder)

        self.file_view = QTreeView()
        self.file_view.setModel(self.files)
        self.file_view.setRootIndex(self.files.index(folder))

        self.dock_files = QDockWidget()
        self.dock_files.setWidget(self.file_view)
        # <<<

        # >>> Table widget
        self.table = QTableWidget(4, 2, self)
        self.rows = 0
        self.cols = 0

        self.dock_table = QDockWidget()
        self.dock_table.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.dock_table.setWidget(self.table)
        # <<<

        # >>> Toolbar
        self.tools = QToolBar()
        self.save_button = QPushButton('Sauvegarder Excel')
        self.tools.addWidget(self.save_button)
        self.addToolBar(self.tools)
        # <<<

        self.label.newSelection.connect(self.processSelection)
        self.file_view.clicked.connect(self.loadImage)
        self.save_button.clicked.connect(self.saveToExcel)

        self.setCentralWidget(self.area)
        self.addDockWidget(Qt.Qt.LeftDockWidgetArea, self.dock_files)
        self.addDockWidget(Qt.Qt.BottomDockWidgetArea, self.dock_table)
        self.setMinimumSize(1240, 680)

    def extractTable(self):
        data = []

        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                item = self.table.item(r, c)
                row.append(item.text())
            data.append(row)

        return data

    def saveToExcel(self):
        self.log('Save to Excel')
        self.setDisabled(True)
        try:
            file = getFile(self)[0]
            data = pandas.DataFrame(self.extractTable())
            data.to_excel(file, index=False)

        except:
            error = traceback.format_exc()
            msg = QErrorMessage(self)
            msg.showMessage(error)

        self.setDisabled(False)

    def loadImage(self, i):
        """Load an image from the file system view"""
        path = self.files.filePath(i)
        self.log(f'Loading image {path}')

        reader = QImageReader(path)
        image = reader.read()

        if not image.isNull():
            self.label.setPixmap(QPixmap.fromImage(image))
            self.label.adjustSize()
        else:
            msg = QErrorMessage(self)
            msg.showMessage(f'{path} is not a supported image format try a PNG image')

        self.status.clearMessage()

    def processSelection(self):
        """Read the selected region and try to decode the text from it"""
        try:
            self.setDisabled(True)
            img = self.label.selectedImage()
            self.log(f'Processing selection {self.label.selection}')

            # Post Processing
            cv_img = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # debug save
            cv2.imwrite('tmp/tmp.png', gray)

            # OCR
            img = Image.fromarray(gray)
            text = pytesseract.image_to_string(img)
            self.addRow(text)

        except:
            error = traceback.format_exc()
            msg = QErrorMessage(self)
            msg.showMessage(error)

        self.status.clearMessage()
        self.setDisabled(False)

    def addRow(self, data):
        cols = list(filter(lambda x: x, data.split('\n')))
        self.cols = max(self.cols, len(cols))

        # resize if necessary
        self.table.setColumnCount(max(self.table.columnCount(), self.cols))
        self.table.setRowCount(max(self.table.rowCount(), self.rows + 1))

        for col, value in enumerate(cols):
            item = QTableWidgetItem(value)
            self.table.setItem(self.rows, col, item)

            if self.rows == 0:
                self.table.setColumnWidth(col, len(value) * 12)

        # increment
        self.rows += 1
        self.table.verticalScrollBar().setValue(self.table.verticalScrollBar().maximum())


def main():
    os.makedirs('tmp', exist_ok=True)

    app = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
