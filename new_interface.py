from PyQt5 import QtWidgets, QtCore, QtGui
from xbmcjson import PLAYER_VIDEO, XBMC
import shutil
from yalla_shoot_parser import get_matches_list
import time
import sys


class matchesThread(QtCore.QThread):
    readysignal = QtCore.pyqtSignal(list, name='matches_ready')

    def __init__(self, day_flag='today'):
        super().__init__()
        self.day_flag = day_flag

    def run(self):
        while True:
            matches_list = get_matches_list(self.day_flag)
            self.readysignal.emit(matches_list)
            time.sleep(60)


class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Starting the matches thread
        self.matches_thread = matchesThread()
        self.matches_thread.readysignal.connect(self.update_match_table)
        self.matches_thread.start()

        self.main_box = QtWidgets.QHBoxLayout()
        self.main_box.setSpacing(0)

        self.addButtons()

        # Matches list widget properties go here
        self.matches_widget = QtWidgets.QTableWidget(0, 3)
        self.matches_widget.setIconSize(QtCore.QSize(64, 64))

        # Expiremental Stylesheet coding

        self.main_box.addWidget(self.matches_widget)
        self.setLayout(self.main_box)

        self.show()
    
    def update_match_table(self, matches_list):
        self.matches_widget.setRowCount(len(matches_list))
        for idx, match in enumerate(matches_list):
            right_icon = QtGui.QIcon(match[0])
            left_icon = QtGui.QIcon(match[4])
            right_item = QtWidgets.QTableWidgetItem(right_icon, '')
            right_item.setToolTip(match[1])
            left_item = QtWidgets.QTableWidgetItem(left_icon, '')
            left_item.setToolTip(match[3])
            match_time = QtWidgets.QTableWidgetItem(match[2])
            match_time.setToolTip(match[6])
            self.matches_widget.setItem(idx, 1, match_time)
            self.matches_widget.setItem(idx, 0, right_item)
            self.matches_widget.setItem(idx, 2, left_item)
            self.matches_widget.resizeColumnsToContents()
            self.matches_widget.resizeRowsToContents()
            total_table_width = sum([self.matches_widget.columnWidth(i)
                                        for i in range(0, 3)])
            self.matches_widget.setMinimumWidth(total_table_width + 2)
        pass



    def addButtons(self):
        vbox1 = QtWidgets.QVBoxLayout()
        vbox2 = QtWidgets.QVBoxLayout()
        vbox3 = QtWidgets.QVBoxLayout()
        vbox4 = QtWidgets.QVBoxLayout()
        vbox5 = QtWidgets.QVBoxLayout()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    sys.exit(app.exec_())