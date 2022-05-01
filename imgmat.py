from json import load
import os
from argparse import ArgumentParser

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QFileDialog, QSpinBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5 import QtCore, Qt


CELL_DIM = (600, 600)


def image_mat(images, rows, cols):
    canvas = Image.new('RGB', (cols * CELL_DIM[0], rows * CELL_DIM[1]), (255, 255, 255))
    # if len(images) != rows * cols:
    #     raise ValueError()
    for r in range(rows):
        for c in range(cols):
            if len(images) <= r * cols + c:
                continue
            img = images[r * cols + c]
            y = r * CELL_DIM[1] + (CELL_DIM[1] - img.size[1]) // 2
            x = c * CELL_DIM[0] + (CELL_DIM[0] - img.size[0]) // 2
            canvas.paste(img, (x, y))
    return canvas


def prepare_image(img, crop):
    x, y = img.size
    if crop > 0:
        img = img.crop((crop, crop, x - crop, y - crop))
        x, y = img.size
    ratio = min(CELL_DIM[0] / x, CELL_DIM[1] / y)
    x = int(x * ratio)
    y = int(y * ratio)
    return img.resize((x, y))


def get_image(images, rows, cols, crop):
    prepared_images = []
    for image in images:
        prepared_images.append(prepare_image(image, crop))
    return image_mat(prepared_images, rows, cols)


class ImageLabel(QLabel):

    def __init__(self, img):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.qim = ImageQt(img)
        self.pixmap = QPixmap.fromImage(self.qim)

    def paintEvent(self, event):
        size = self.size()
        painter = QPainter(self)
        point = QtCore.QPoint(0,0)
        scaledPix = self.pixmap.scaled(size, QtCore.Qt.KeepAspectRatio, transformMode = QtCore.Qt.SmoothTransformation)
        # start painting the label from left upper corner
        point.setX((size.width() - scaledPix.width())//2)
        point.setY((size.height() - scaledPix.height())//2)
        painter.drawPixmap(point, scaledPix)
    
    def onImageChange(self, img):
        self.qim = ImageQt(img)
        self.pixmap = QPixmap.fromImage(self.qim)
        self.repaint()


class ImageLayout(QGridLayout):

    def __init__(self, img):
        super().__init__()
        self.img_label = ImageLabel(img)
        self.addWidget(self.img_label)
        self.setRowStretch(0, 1)
        self.setColumnStretch(0, 1)
    
    def onImageChange(self, img):
        self.img_label.onImageChange(img)
    

class FileList(QListWidget):

    def __init__(self, drop_action) -> None:
        super().__init__()
        self.drop_action = drop_action
        self.setIconSize(QtCore.QSize(50, 50))
    
    def dropEvent(self, event):
        super().dropEvent(event)
        self.drop_action()


class FileListItem(QListWidgetItem):

    def __init__(self, filepath) -> None:
        super().__init__()
        name = os.path.split(filepath)[1]
        self.setText(name)
        self.filepath = filepath
        self.img = Image.open(self.filepath)
        self.img_resized = self.img.resize((50, 50))
        self.qim = ImageQt(self.img_resized)
        self.icon_pixmap = QPixmap.fromImage(self.qim)
        self.icon = QIcon(self.icon_pixmap)
        self.setIcon(self.icon)


class MainWindow(QWidget):

    def __init__(self) -> None:
        super().__init__()
        
        # right control pane
        self.control_layout = QVBoxLayout()
        # load images button
        self.load_button = QPushButton('Load Images')
        self.load_button.clicked.connect(self.getfiles)
        self.control_layout.addWidget(self.load_button)
        # rows, cols and crop
        self.row_col_layout = QGridLayout()
        self.rows = QSpinBox()
        self.rows.setRange(1, 10)
        self.rows.setValue(3)
        self.rows.valueChanged.connect(self.update_image)
        self.row_col_layout.addWidget(QLabel('Rows:'), 0, 0)
        self.row_col_layout.addWidget(self.rows, 0, 1)
        self.cols = QSpinBox()
        self.cols.setRange(1, 10)
        self.cols.setValue(2)
        self.cols.valueChanged.connect(self.update_image)
        self.row_col_layout.addWidget(QLabel('Columns:'), 1, 0)
        self.row_col_layout.addWidget(self.cols, 1, 1)
        self.crop = QSpinBox()
        self.crop.setRange(0, 10)
        self.crop.setValue(0)
        self.crop.valueChanged.connect(self.update_image)
        self.row_col_layout.addWidget(QLabel('Crop:'), 2, 0)
        self.row_col_layout.addWidget(self.crop, 2, 1)
        self.control_layout.addLayout(self.row_col_layout)
        # file list
        self.file_list = FileList(self.update_image)
        self.file_list.setDragDropMode(Qt.QAbstractItemView.InternalMove)
        self.control_layout.addWidget(self.file_list)
        # save button
        self.save_button = QPushButton('Save Result')
        self.save_button.clicked.connect(self.save_result)
        self.control_layout.addWidget(self.save_button)

        # image pane
        self.img = get_image([], self.rows.value(), self.cols.value(), self.crop.value())
        self.img_layout = ImageLayout(self.img)
        
        layout = QHBoxLayout()
        layout.addLayout(self.img_layout, stretch=1)
        layout.addLayout(self.control_layout)
        self.setLayout(layout)
    
    def getfiles(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        filenames, _ = dlg.getOpenFileNames(filter='*.jpg *.png')
        filenames = sorted(filenames, key=lambda p: os.path.split(p)[1].lower())
        while self.file_list.count() > 0:
            self.file_list.takeItem(0)
        for filename in filenames:
            self.file_list.addItem(FileListItem(filename))
        self.update_image()
    
    def update_image(self):
        images = [self.file_list.item(i).img for i in range(self.file_list.count())]
        self.img = get_image(images, self.rows.value(), self.cols.value(), self.crop.value())
        self.img_layout.onImageChange(self.img)
    
    def save_result(self):
        dlg = QFileDialog()
        filename, _ = dlg.getSaveFileName(caption='Save File', filter='*.jpg')
        self.img.save(filename)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
