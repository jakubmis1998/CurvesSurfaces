from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import numpy as np

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        title = "Circular model"
        top = 400
        left = 100
        width = 1200
        height = 650
        self.setWindowTitle(title)
        self.setStyleSheet("background-color: lightblue;")
        self.setGeometry(top, left, width, height) 

        self.points = []
        self.nearest = -1
        
        # (self.width / 2) - 20px <-> 1200 / 2 - 20 = 580
        self.image1 = QImage(QSize(580, 580), QImage.Format_RGB32) 
        self.image1.fill(Qt.black)
        self.image2 = QImage(QSize(580, 580), QImage.Format_RGB32) 
        self.image2.fill(Qt.black)

        self.painter1 = QPainter(self.image1)
        self.painter2 = QPainter(self.image2)

        self.reset_btn = QPushButton(self)
        self.reset_btn.setGeometry(QRect(550, 600, 100, 30))
        self.reset_btn.setText("Reset")
        self.reset_btn.clicked.connect(self.reset_image)
    
    def reset_image(self):
        self.points = []
        self.image1.fill(Qt.black)
        self.image2.fill(Qt.black)
        self.update()

    # paintEvent for creating blank canvas 
    def paintEvent(self, event): 
        canvasPainter = QPainter(self) 
        canvasPainter.drawImage(0, 0, self.image1)
        # self.width / 2 + 20  <->  600 + 20
        canvasPainter.drawImage(620, 0, self.image2)
        self.draw_center()

    def mousePressEvent(self, cursor_event):
        x, y = cursor_event.pos().x(), cursor_event.pos().y()
        self.nearest = self.nearest_point(x, y)
        if (
            cursor_event.button() == Qt.LeftButton and
            y <= self.image1.height() and y >= 0 and
            x <= self.image1.width() and x >= 0 and
            len(self.points) < 2
        ):
            self.painter1.setPen(QPen(
                Qt.white, 10,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            self.points.append(np.array([x, y]))
            self.painter1.drawPoint(cursor_event.pos())
            self.update()

            if len(self.points) == 2:
                self.points[self.nearest] = np.array([x, y])
                self.draw_points_and_line()
                self.update()
    
    def mouseMoveEvent(self, cursor_event):
        x, y = cursor_event.pos().x(), cursor_event.pos().y()
        if (
            self.nearest != -1 and
            x <= self.image1.width() and x >= 0 and
            y <= self.image1.height() and y >= 0
        ):
            self.points[self.nearest] = np.array([x, y])
            self.draw_points_and_line()
            self.update()

    def draw_center(self):
        self.painter1.setPen(QPen(
            Qt.yellow, 15,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        self.painter2.setPen(QPen(
            Qt.yellow, 15,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        self.painter1.drawPoint(QPoint(int(self.image1.width() / 2), int(self.image1.height() / 2)))
        self.painter2.drawPoint(QPoint(int(self.image2.width() / 2), int(self.image2.height() / 2)))
        self.update()

    def draw_points_and_line(self):
        R = int(self.image1.width() / 2)
        self.image1.fill(Qt.black)
        self.image2.fill(Qt.black)
        self.draw_center()
        self.painter1.setPen(QPen(
            Qt.white, 10,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        for p in self.points:
            self.painter1.drawPoint(p[0], p[1])

        self.painter1.setPen(QPen(
            Qt.red, 1,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        self.painter2.setPen(QPen(
            Qt.red, 1,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        # -R, move center to (0, 0). Map points from (0, 580) - > (-290, 290)
        x1, x2 = self.points[0][0] - R, self.points[1][0] - R
        y1, y2 = self.points[0][1] - R, self.points[1][1] - R
        distance = int(np.sqrt((x1 - x2)**2 + (y1 - y2)**2))
        """
        x = x1 + d * (x2 - x1) / distance
        y = y1 + d * (y2 - y1) / distance
        """
        for d in range(distance + 1):
            x = int(np.around(x1 + (d * (x2 - x1)) / distance))
            y = int(np.around(y1 + (d * (y2 - y1)) / distance))
            ground = np.sqrt(x**2 + y**2 + R**2)
            self.painter1.drawPoint(x + R, y + R)
            self.painter2.drawPoint(
                int(np.around(R + (R * x) / ground)),
                int(np.around(R + (R * y) / ground))
            )

    def nearest_point(self, x, y):
        R = 10
        for i, point in enumerate(self.points):
            if (
                point[0] - R <= x and x <= point[0] + R and
                point[1] - R <= y and y <= point[1] + R
            ):
                return i
        return -1


if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = Window() 
    window.show() 
    sys.exit(app.exec()) 
