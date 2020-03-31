import os

from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton, QLineEdit, QFileDialog

cwd = os.getcwd()

DEFAULT_FOLDER = os.path.join(cwd, r'images')
DEFAULT_EXCEL = os.path.join(cwd, r'extracted.xlsx')


def getFolder(parent, default):
    os.makedirs(default, exist_ok=True)

    return QFileDialog.getExistingDirectory(
        parent,
        'Dossier d\'image',
        default,
        QFileDialog.ShowDirsOnly)


def getFile(parent, default):
    os.makedirs(os.path.dirname(default), exist_ok=True)

    return QFileDialog.getSaveFileName(
        parent,
        'Fichier Excel',
        default)[0]


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent=parent)
        self.layout = QGridLayout()

        self.input_path = QLineEdit(DEFAULT_FOLDER)
        self.output_path = QLineEdit(DEFAULT_EXCEL)

        self._input()
        self._output()
        self._close()

        self.setLayout(self.layout)
        self.setMinimumSize(1240, 240)

    def _close(self):
        close = QPushButton('Suivant')
        self.layout.addWidget(close, 2, 2)
        close.clicked.connect(lambda : self.close())

    def _input(self):
        label = QLabel('Dossier d\'Image')
        browse = QPushButton('Parcourir')
        browse.clicked.connect(lambda : self.input_path.setText(getFolder(self, self.input)))

        self.layout.addWidget(label, 0, 0)
        self.layout.addWidget(self.input_path, 0, 1)
        self.layout.addWidget(browse, 0, 2)

    def _output(self):
        label = QLabel('Fichier Excel')
        browse = QPushButton('Parcourir')
        browse.clicked.connect(lambda:  self.output_path.setText(getFile(self, self.output)))

        self.layout.addWidget(label, 1, 0)
        self.layout.addWidget(self.output_path, 1, 1)
        self.layout.addWidget(browse, 1, 2)

    @property
    def input(self):
        return self.input_path.text()

    @property
    def output(self):
        return self.output_path.text()


def getInputOutput(parent=None):
    window = ConfigDialog(parent)
    window.exec()
    return window.input, window.output


def main():
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    print(getInputOutput(None))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

