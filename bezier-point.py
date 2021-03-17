from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import numpy as np

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        title = "Bezier point"
        top = 500
        left = 200
        width = 800
        height = 600
        self.setWindowTitle(title)
        self.setStyleSheet("background-color: gray;")
        self.setGeometry(top, left, width, height) 

        self.points = []
        
        self.image = QImage(QSize(self.width(), int(0.8 * self.height())), QImage.Format_RGB32) 
        self.image.fill(Qt.black)

        self.painter = QPainter(self.image)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setGeometry(200, 510, 400, 20)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged[int].connect(self.slider_change_value)

        self.reset_btn = QPushButton(self)
        self.reset_btn.setGeometry(QRect(350, 540, 100, 30))
        self.reset_btn.setText("Reset")
        self.reset_btn.clicked.connect(self.reset_image)
    
    def reset_image(self):
        self.slider.setValue(0)
        self.points = []
        self.image.fill(Qt.black)
        self.update()

    # paintEvent for creating blank canvas 
    def paintEvent(self, event): 
        canvasPainter = QPainter(self) 
        canvasPainter.drawImage(0, 0, self.image) 

    def mousePressEvent(self, cursor_event):
        pos = cursor_event.pos()
        if cursor_event.button() == Qt.LeftButton and pos.y() <= self.image.height():
            self.painter.setPen(QPen(
                Qt.white, 10,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            self.points.append(np.array([pos.x(), pos.y()]))
            self.painter.drawPoint(cursor_event.pos())
            self.update()

            if len(self.points) > 1:
                t = self.slider.value() / 100.0
                self.handle_bezier_point(t)
    
    def slider_change_value(self, value):
        self.handle_bezier_point(value / 100.0)

    def draw_points(self):
        self.image.fill(Qt.black)
        self.painter.setPen(QPen(
            Qt.white, 10,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        for p in self.points:
            self.painter.drawPoint(p[0], p[1])
    
    def handle_bezier_point(self, t):
        if len(self.points) > 0:
            self.draw_points()
            pts = self.points.copy()
            while len(pts) > 1:
                lines = []
                for i in range(len(pts) - 1):
                    lines.append((pts[i], pts[i + 1]))
                new_points = []
                for o in lines:
                    point = (1 - t) * o[0] + t * o[1]
                    new_points.append(point)
                pts = new_points

            self.painter.setPen(QPen(
                Qt.red, 10,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            self.painter.drawPoint(int(pts[0][0]), int(pts[0][1]))
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = Window() 
    window.show() 
    sys.exit(app.exec()) 
