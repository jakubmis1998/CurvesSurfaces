from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
import sys
import numpy as np

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        title = "Increase degree of bezier curve"
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

        self.increase_degree_btn = QPushButton(self)
        self.increase_degree_btn.setStyleSheet("background-color: white;")
        self.increase_degree_btn.setGeometry(QRect(320, 500, 140, 30))
        self.increase_degree_btn.setText("Podnieś stopień")
        self.increase_degree_btn.clicked.connect(self.increase_degree)

        self.reset_btn = QPushButton(self)
        self.reset_btn.setStyleSheet("background-color: white;")
        self.reset_btn.setGeometry(QRect(320, 550, 140, 30))
        self.reset_btn.setText("Reset")
        self.reset_btn.clicked.connect(self.reset_image)
    
    def reset_image(self):
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
    
    def draw_bezier_point(self, t):
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

            self.painter.setPen(QPen(
                Qt.red, 1,
                Qt.SolidLine,  
                Qt.RoundCap,
                Qt.RoundJoin
            ))
            self.painter.drawPoint(int(points[0][0]), int(points[0][1]))
            self.update()
    
    def increase_degree(self):
        N = len(self.points) - 1
        if len(self.points) > 2:
            new_points = [self.points[0]]
            
            for i in range(1, len(self.points)):
                x = (i * self.points[i - 1][0] + (N + 1 - i) * self.points[i][0]) / float(N + 1)
                y = (i * self.points[i - 1][1] + (N + 1 - i) * self.points[i][1]) / float(N + 1)
                new_points.append(np.array([int(np.around(x)), int(np.around(y))]))

            new_points.append(self.points[-1])
            self.points = new_points
            self.draw_all()

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

    def draw_edges(self):
        self.painter.setPen(QPen(
            Qt.blue, 1,
            Qt.SolidLine,  
            Qt.RoundCap,
            Qt.RoundJoin
        ))
        for i in range(len(self.points) - 1):
            self.painter.drawLine(
                QPoint(self.points[i][0], self.points[i][1]),
                QPoint(self.points[i + 1][0], self.points[i + 1][1])
            )
    
    def draw_all(self):
        self.draw_points()
        self.draw_edges()
        step = self.get_step_value()
        # T from 0 to 1, step <= N * max
        for t in np.arange(0, 1, 1 / float(step)):
            self.draw_bezier_point(t)

if __name__ == '__main__':
    app = QApplication(sys.argv) 
    window = Window()
    window.show() 
    sys.exit(app.exec()) 
