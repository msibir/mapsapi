import os
import sys

import requests
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QRadioButton, QLabel
from PyQt5.QtCore import Qt


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)
        self.pushButton.clicked.connect(self.run)
        self.pushButton_2.clicked.connect(self.setOff)
        self.setOff()

    def run(self):
        place = self.lineEdit.text()
        response = requests.get(
            f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json")
        response = response.json()
        response = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        address = response["metaDataProperty"]["GeocoderMetaData"]["text"]
        postal = response["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        self.coords = response["Point"]["pos"]
        self.pt = self.coords
        if self.radioButton.isChecked():
            self.address.setText(f"{address}, {postal}")
        else:
            self.address.setText(f"{address}")
        self.getImage()

    def getImage(self, ispt=True):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(self.coords.split())}&spn={self.spn},{self.spn}&l={self.layer}"
        if ispt:
            map_request += f"&pt={self.pt.split(' ')[0]},{self.pt.split(' ')[1]}"
        print(map_request)
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.img.setPixmap(self.pixmap)
        os.remove(self.map_file)

    def setOff(self):
        self.lineEdit.clear()
        self.address.clear()
        place = "Курган Гоголя 1"
        response = requests.get(
            f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json")
        response = response.json()
        response = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        address = response["metaDataProperty"]["GeocoderMetaData"]["text"]
        self.coords = response["Point"]["pos"]
        self.address.setText(f"{address}")
        self.pt = self.coords
        self.spn = 0.05
        self.layer = "map"
        self.getImage(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.spn = self.spn * 2
            self.spn = min(self.spn, 51.2)
            self.getImage()
        if event.key() == Qt.Key_PageDown:
            self.spn = self.spn / 2
            self.spn = max(self.spn, 0.000009765625)
            self.getImage()
        if event.key() == Qt.Key_Up:
            c = [float(i) for i in self.coords.split(" ")]
            c[1] += self.spn / 10
            c[1] = min(c[1], 85.0)
            self.coords = " ".join([str(i) for i in c])
            self.getImage()
        if event.key() == Qt.Key_Down:
            c = [float(i) for i in self.coords.split(" ")]
            c[1] -= self.spn / 10
            c[1] = max(-85.0, c[1])
            self.coords = " ".join([str(i) for i in c])
            self.getImage()
        if event.key() == Qt.Key_Right:
            c = [float(i) for i in self.coords.split(" ")]
            c[0] += self.spn / 10
            c[0] = min(175, c[0])
            self.coords = " ".join([str(i) for i in c])
            self.getImage()

    def get_click_coord(self, event):
        label_width = 600
        label_height = 400
        pt_0 = float(self.coords.split(' ')[0]) - (self.spn * 2) + self.spn * 4 * (
                (event.x() - self.img.x()) / label_width) - (
                       (label_width / 2 - event.x() - self.img.x()) / 5500 * self.spn)
        pt_1 = float(self.coords.split(' ')[1]) + (
                self.spn * 450 / label_width) - self.spn * label_width / label_height * (
                       (event.y() - self.img.y()) / label_height)
        self.pt = str(pt_0) + ' ' + str(pt_1)

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self.get_click_coord(event)
                self.getImage()

                geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

                geocoder_params = {
                    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                    "geocode": f'{self.pt.replace(" ", ",")}',
                    "format": "json"}

                response = requests.get(geocoder_api_server, params=geocoder_params)

                if not response:
                    pass

                json_response = response.json()
                response_new = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                address = response_new["metaDataProperty"]["GeocoderMetaData"]["text"]
                self.address.setText(address)
            if event.button() == Qt.RightButton:
                pass

        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
