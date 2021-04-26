import sys

from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QImage, QPen, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QAction, QFileDialog, QSlider, QColorDialog,\
    QPushButton, QInputDialog


class mw(QMainWindow):
    def __init__(self, p):
        super().__init__()
        self.resize(500, 500)
        self.setWindowTitle("MyPaintAnalog")
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.pixmap = QPixmap.fromImage(self.image)

        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.black

        self.brushLine = Qt.SolidLine
        self.currentPoint = self.lastPoint = QPoint()
        self.brushTipe = 0
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("файл")

        brushMenu = mainMenu.addMenu("Размер")

        brushColor = mainMenu.addMenu("Цвет")

        brushLine = mainMenu.addMenu("Линия")

        brush = mainMenu.addMenu("Инструменты")

        SolidAction = QAction("Прямая линия", self)
        brushLine.addAction(SolidAction)
        SolidAction.triggered.connect(self.Solid)

        DashAction = QAction("Пунктирная линия", self)
        brushLine.addAction(DashAction)
        DashAction.triggered.connect(self.Dash)

        DashDotAction = QAction("Пунктир точка", self)
        brushLine.addAction(DashDotAction)
        DashDotAction.triggered.connect(self.DashDot)

        DashDotDotAction = QAction("Пунктир с двойной точкой", self)
        brushLine.addAction(DashDotDotAction)
        DashDotDotAction.triggered.connect(self.DashDotDot)

        pensilAction = QAction("Карандаш", self)
        brush.addAction(pensilAction)
        pensilAction.triggered.connect(self.pensil)
        roundAction = QAction("Овал", self)
        brush.addAction(roundAction)
        roundAction.triggered.connect(self.circle)

        lineAction = QAction("Прямая линия", self)
        brush.addAction(lineAction)
        lineAction.triggered.connect(self.line)

        rectAction = QAction("Прямоугольник", self)
        brush.addAction(rectAction)
        rectAction.triggered.connect(self.rect)

        textAction = QAction("Текст", self)
        brush.addAction(textAction)
        textAction.triggered.connect(self.text)

        blineAction = QAction("Жирная линия", self)
        brush.addAction(blineAction)
        blineAction.triggered.connect(self.bline)

        saveAction = QAction("Сохранить", self)
        saveAction.setShortcut("Cntrl+S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        clearAction = QAction("Очистить", self)
        clearAction.setShortcut("Cntrl+C")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)

        openAction = QAction("Открыть", self)
        openAction.setShortcut("Cntrl+O")
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.open)

        tpAction = QAction("Выбрать толщину", self)
        brushMenu.addAction(tpAction)
        tpAction.triggered.connect(self.tp)

        whiteAction = QAction("Стерка", self)
        brushColor.addAction(whiteAction)
        whiteAction.triggered.connect(self.wColor)

        colorAction = QAction("Выбрать цвет", self)
        brushColor.addAction(colorAction)
        colorAction.triggered.connect(self.bColor)

        fillAction = QAction("Залить экран", self)
        brushColor.addAction(fillAction)
        fillAction.triggered.connect(self.fill)
        self.open(p)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()
            self.currentPoint = event.pos()
            self.repaint()
        elif event.button() == Qt.RightButton and self.brushTipe != 0 and self.brushTipe != 4:
            self.drawing = True
            self.currentPoint = event.pos()
            self.repaint()
            self.drawing = False

    def mouseMoveEvent(self, event):
        # предача текущего значения местоположения курсора если мы рисуем
        if self.drawing:
            self.currentPoint = event.pos()

    def mouseReleazeEvent(self, event):
        # рисование становиться False чтобы при отпуске  кнопки линия переставала рисоваться
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.repait()

    def paintEvent(self, event):
        canvaspainter = QPainter(self)
        canvaspainter.drawImage(self.image.rect(), self.image)
        if self.drawing:
            self.drawLine()

    def drawLine(self):
        painter = QPainter(self.image)
        painter.begin(self.image)
        painter.setPen(QPen(self.brushColor, self.brushSize, self.brushLine, Qt.RoundCap, Qt.RoundJoin))
        if self.brushTipe == 0 or self.brushTipe == 4:
            painter.drawLine(self.lastPoint, self.currentPoint)
            self.lastPoint = self.currentPoint
            painter.end()
            self.update()
        elif self.brushTipe == 1 and self.drawing:
            painter.drawLine(self.lastPoint, self.currentPoint)
            painter.end()
            self.update()
        elif self.brushTipe == 2 and self.drawing:
            painter.drawEllipse(QRect(self.lastPoint, self.currentPoint))
            painter.end()
            self.update()
        elif self.brushTipe == 3 and self.drawing:
            painter.drawRect(QRect(self.lastPoint, self.currentPoint))
            painter.end()
            self.update()
        elif self.brushTipe == 5 and self.drawing:
            x = QInputDialog(self)
            t, ok = x.getText(self, '',
                              'текст для рисовки:')
            x.hide()
            if ok:
                painter.drawText(self.lastPoint, t)
                painter.end()
                self.update()
                self.drawing = False

    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
        if filePath == "":
            return
        else:
            self.image.save(filePath)

    def open(self, *arg):
        if arg != '':
            filePath = arg
        else:
            filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg)")
        if filePath == "":
            return
        else:
            self.image = QImage(filePath)
        self.pixmap = QPixmap.fromImage(self.image)
        p = self.pixmap.scaled(self.height() - self.menuBar().height(), self.width(), Qt.KeepAspectRatio,
                               Qt.FastTransformation)
        self.pixmap = p
        self.image = QImage(self.pixmap)

    def clear(self):
        self.image.fill(Qt.white)
        self.update()

    def tp(self):
        self.bs = BrushSize(self)
        self.bs.show()

    def bColor(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.brushColor = col

    def wColor(self):
        self.brushColor = Qt.white

    def setSize(self, value):
        self.brushSize = value

    def Solid(self):
        self.brushLine = Qt.SolidLine

    def Dash(self):
        self.brushLine = Qt.DashLine

    def DashDot(self):
        self.brushLine = Qt.DashDotLine

    def DashDotDot(self):
        self.brushLine = Qt.DashDotDotLine

    def fill(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.image.fill(col)
            self.update()

    def pensil(self):
        self.brushTipe = 0
        self.brushSize = 2
        self.Solid()

    def line(self):
        self.brushTipe = 1
        self.brushSize = 2
        self.Solid()

    def circle(self):
        self.brushTipe = 2
        self.brushSize = 2
        self.Solid()

    def rect(self):
        self.brushTipe = 3
        self.brushSize = 2
        self.Solid()

    def bline(self):
        self.brushTipe = 4
        self.brushSize = 21
        self.Solid()

    def text(self):
        self.brushTipe = 5
        self.brushSize = 2
        self.Solid()


class BrushSize(QWidget):
    def __init__(self, m):
        super().__init__()
        self.move(50, 20)
        self.resize(50, 100)
        self.slider = QSlider(Qt.Horizontal, self)

        self.slider.setMaximum(20)
        self.slider.setMinimum(1)
        self.slider.valueChanged[int].connect(self.changeValue)

        self.m = m
        if self.m.brushSize == 3:
            self.slider.setMaximum(30)
            self.slider.setMinimum(21)

        self.brushSize = self.m.brushSize
        self.brushColor = self.m.brushColor

        self.btn = QPushButton(self)
        self.btn.resize(20, 20)
        self.btn.setText("Ok")
        self.btn.move(0, 75)
        self.btn.clicked.connect(self.ok)

    def ok(self):
        print(self.brushSize)
        self.m.brushSize = self.brushSize
        self.hide()

    def changeValue(self, value):
        self.brushSize = value
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(QPen(self.brushColor, self.brushSize, self.m.brushLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(0, 50, 100, 50)


def start(name):
    app = QApplication(sys.argv)
    ex = mw(name + '.jpg')
    ex.show()
    sys.exit(app.exec())
