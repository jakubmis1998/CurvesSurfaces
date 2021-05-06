from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import numpy as np

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        title = "Colineation in circular model"
        top = 400
        left = 100
        width = 1200
        height = 700
        self.setWindowTitle(title)
        self.setStyleSheet("background-color: lightblue;")
        self.setGeometry(top, left, width, height) 

        self.points = []
        self.nearest = -1

        self.colineation_matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        
        # (self.width / 2) - 20px <-> 1200 / 2 - 20 = 580
        self.image1 = QImage(QSize(580, 580), QImage.Format_RGB32) 
        self.image1.fill(Qt.black)
        self.image2 = QImage(QSize(580, 580), QImage.Format_RGB32) 
        self.image2.fill(Qt.black)
        self.R = int(self.image1.width() / 2)

        self.painter1 = QPainter(self.image1)
        self.painter2 = QPainter(self.image2)

        self.radius_label = QLabel('Radius [0, 290] ->', self)
        self.radius_label.setGeometry(260, 590, 200, 20)
        self.radius_slider = QSlider(Qt.Horizontal, self)
        self.radius_slider.setGeometry(400, 590, 400, 20)
        self.radius_slider.setMinimum(0)
        self.radius_slider.setMaximum(self.R)
        self.radius_slider.setValue(self.R)
        self.radius_slider.valueChanged[int].connect(self.radius_slider_change_value)

        self.radius_label = QLabel('Angle  [0, 360] ->', self)
        self.radius_label.setGeometry(260, 620, 200, 20)
        self.angle_slider = QSlider(Qt.Horizontal, self)
        self.angle_slider.setGeometry(400, 620, 400, 20)
        self.angle_slider.setMinimum(0)
        self.angle_slider.setMaximum(360)
        self.angle_slider.valueChanged[int].connect(self.angle_slider_change_value)

        self.reset_btn = QPushButton(self)
        self.reset_btn.setGeometry(QRect(550, 650, 100, 30))
        self.reset_btn.setText("Reset")
        self.reset_btn.clicked.connect(self.reset_image)

    # paintEvent for creating blank canvas 
    def paintEvent(self, event): 
        canvasPainter = QPainter(self) 
        canvasPainter.drawImage(0, 0, self.image1)
        # self.width / 2 + 20  <->  600 + 20
        canvasPainter.drawImage(620, 0, self.image2)
        self.draw_center()
        self.update()
    
    def mouseMoveEvent(self, cursor_event):
        x, y = cursor_event.pos().x(), cursor_event.pos().y()
        if (
            self.nearest != -1 and
            x <= self.image1.width() and x >= 0 and
            y <= self.image1.height() and y >= 0
        ):
            self.points[self.nearest] = np.array([x, y])
            self.draw_all()
            self.update()

    def mousePressEvent(self, cursor_event):
        x, y = cursor_event.pos().x(), cursor_event.pos().y()
        self.nearest = self.nearest_point(x, y)
        if (cursor_event.button() == Qt.LeftButton and
            y <= self.image1.height() and y >= 0 and
            x <= self.image1.width() and x >= 0 and
            self.nearest == -1
        ):
            self.painter1.setPen(QPen(
                Qt.white, 10,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            self.points.append(np.array([x, y]))
            self.painter1.drawPoint(x, y)
            self.update()

            if len(self.points) > 1:
                self.draw_all()

    def draw_all(self):
        self.draw_points()
        self.draw_center()
        step = self.get_step_value()
        # t from 0 to 1, step <= N * max
        for t in np.arange(0, 1, 1 / float(step)):
            self.draw_bezier_point_and_colineation(t)
    
    def draw_points(self):
        self.image1.fill(Qt.black)
        self.image2.fill(Qt.black)
        self.painter1.setPen(QPen(
            Qt.white, 10,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        for p in self.points:
            self.painter1.drawPoint(p[0], p[1])

    def draw_bezier_point_and_colineation(self, t):
        if len(self.points) > 0:
            points = self.points.copy()
            while len(points) > 1:
                edges = []
                for i in range(len(points) - 1):
                    edges.append((points[i], points[i + 1]))
                new_points = []
                for edge in edges:
                    point = (1 - t) * edge[0] + t * edge[1]
                    new_points.append(point)
                points = new_points

            # Classic bezier point
            bezier_point = int(points[0][0]), int(points[0][1])

            self.painter1.setPen(QPen(
                Qt.red, 1,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            self.painter1.drawPoint(bezier_point[0], bezier_point[1])
            
            self.painter2.setPen(QPen(
                Qt.green, 1,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))

            # Bezier point after colineation
            colineation_point = self.colineation_matrix.dot(np.array([
                bezier_point[0] - self.R,
                bezier_point[1] - self.R,
                self.radius_slider.value()
            ]))
            self.painter2.drawPoint(
                int(colineation_point[0] + self.R),
                int(colineation_point[1] + self.R)
            )

            self.painter2.setPen(QPen(
                Qt.cyan, 1,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            # Bezier point after colineation in circular model
            ground = np.sqrt(colineation_point[0]**2 + colineation_point[1]**2 + self.radius_slider.value()**2)
            self.painter2.drawPoint(
                int(np.around(self.R + (self.radius_slider.value() * colineation_point[0]) / ground)),
                int(np.around(self.R + (self.radius_slider.value() * colineation_point[1]) / ground))
            )


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
    
    def angle_slider_change_value(self, value):
        angle = (value * np.pi) / 180
        self.colineation_matrix = np.array([
            [np.cos(angle), 0, -np.sin(angle)],
            [0, 1, 0],
            [np.sin(angle), 0, np.cos(angle)]
        ])
        if len(self.points):
            self.draw_all()
    
    def radius_slider_change_value(self, value):
        if len(self.points):
            self.draw_all()
    
    def get_step_value(self):
        edges = []
        edge_lengths = []
        # Create edges between points
        for i in range(len(self.points) - 1):
            edges.append((self.points[i], self.points[i + 1]))
        N = len(edges)
        # Calculate edges lengths
        for edge in edges:
            edge_lengths.append(
                np.sqrt((edge[0][0] - edge[1][0])**2 + (edge[0][1] - edge[1][1])**2)
            )
        # Step <= N * max{edge_lengths}
        return N * np.max(edge_lengths)

    def nearest_point(self, x, y):
        R = 10
        for i, point in enumerate(self.points):
            if (
                point[0] - R <= x and x <= point[0] + R and
                point[1] - R <= y and y <= point[1] + R
            ):
                return i
        return -1
    
    def reset_image(self):
        self.points = []
        self.angle_slider.setValue(0)
        self.radius_slider.setValue(0)
        self.image1.fill(Qt.black)
        self.image2.fill(Qt.black)
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = Window() 
    window.show() 
    sys.exit(app.exec()) 