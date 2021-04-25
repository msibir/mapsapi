import sys

import requests
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QRadioButton, QLabel


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)
        self.pushButton.clicked.connect(self.run)

    def run(self):
        place = self.lineEdit.text()
        response = requests.get(
            f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={place}&format=json")
        response = response.json()
        response = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        address = response["metaDataProperty"]["GeocoderMetaData"]["text"]
        postal = response["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
        coords = response["Point"]["pos"]
        if self.radioButton.isChecked():
            self.address.setText(f"{address}, {postal}")
        else:
            self.address.setText(f"{address}")
        print(address, postal, coords)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
