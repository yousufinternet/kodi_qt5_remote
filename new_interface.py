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

        self.main_box.addSpacing(30)

        # Matches list widget properties go here
        self.matches_widget = QtWidgets.QTableWidget(0, 3)
        self.matches_widget.setIconSize(QtCore.QSize(64, 64))
        self.matches_widget.horizontalHeader().hide()
        self.matches_widget.verticalHeader().hide()
        # self.matches_widget.setAlternatingRowColors(True)
        self.matches_widget.setEditTriggers(
            QtWidgets.QTableWidget.NoEditTriggers)

        # Expiremental Stylesheet coding

        self.main_box.addWidget(self.matches_widget)
        self.setLayout(self.main_box)

        self.setStyleSheet(
            'QWidget {background-color:\#232323;}\
            QPushButton {background-color: black;\
            border-style: outset;\
            border-width: 2px;\
            border-color: white;\
            font: bold 24px;\
            min-width: 3em;\
            padding: 5px;}\
            QPushButton:hover {background-color: \#414141;\
            border-style: outset;\
            border-width: 5px;\
            border-color: white;\
            font: bold 24px;\
            min-width: 3em;\
            padding: 5px;}\
            QPushButton:pressed {background-color: \#232323;\
            border-style: outset;\
            border-width: 5px;\
            border-color: white;\
            font: bold 24px;\
            min-width: 3em;\
            padding: 5px;}\
            QPushButton:disabled {background-color: \#606060;}\
            QPushButton#topleft { border-top-left-radius: 15px;}\
            QPushButton#topright { border-top-right-radius: 15px;}\
            QPushButton#botright { border-bottom-right-radius: 15px;}\
            QPushButton#botleft { border-bottom-left-radius: 15px;}\
            QPushButton#left {border-bottom-left-radius: 15px;\
            border-top-left-radius: 15px;}\
            QPushButton#right {border-bottom-right-radius: 15px;\
            border-top-right-radius: 15px;}\
            QTableWidget {background-color:\#232323;}\
            '
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowIcon(QtGui.QIcon('./Images/kodi_icon.png'))
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
        # all the boxes layouts that will be added to the main horizontal
        # layout
        vbox1 = QtWidgets.QVBoxLayout()
        vbox2 = QtWidgets.QVBoxLayout()
        vbox3 = QtWidgets.QVBoxLayout()
        vbox4 = QtWidgets.QVBoxLayout()
        vbox5 = QtWidgets.QVBoxLayout()
        hbox1 = QtWidgets.QHBoxLayout()
        hbox2 = QtWidgets.QHBoxLayout()

        # we want the buttons to stick to each other
        vbox1.setSpacing(0)
        vbox2.setSpacing(0)
        vbox3.setSpacing(0)

        up_button = QtWidgets.QPushButton('')
        up_button.setIcon(QtGui.QIcon('./buttons/go-up.png'))
        up_button.setIconSize(QtCore.QSize(48, 48))
        down_button = QtWidgets.QPushButton('')
        down_button.setIcon(QtGui.QIcon('./buttons/go-down.png'))
        down_button.setIconSize(QtCore.QSize(48, 48))
        left_button = QtWidgets.QPushButton('')
        left_button.setIcon(QtGui.QIcon('./buttons/go-left.png'))
        left_button.setIconSize(QtCore.QSize(48, 48))
        right_button = QtWidgets.QPushButton('')
        right_button.setIcon(QtGui.QIcon('./buttons/go-right.png'))
        right_button.setIconSize(QtCore.QSize(48, 48))
        menu_button = QtWidgets.QPushButton('')
        menu_button.setIcon(QtGui.QIcon('./buttons/menu.png'))
        menu_button.setIconSize(QtCore.QSize(48, 48))
        menu_button.setObjectName('topleft')
        osd_button = QtWidgets.QPushButton('')
        osd_button.setIcon(QtGui.QIcon('./buttons/osd.png'))
        osd_button.setIconSize(QtCore.QSize(48, 48))
        osd_button.setObjectName('botleft')
        back_button = QtWidgets.QPushButton('')
        back_button.setIcon(QtGui.QIcon('./buttons/back.png'))
        back_button.setIconSize(QtCore.QSize(48, 48))
        back_button.setObjectName('botright')
        subs_button = QtWidgets.QPushButton('')
        subs_button.setIcon(QtGui.QIcon('./buttons/subtitles.png'))
        subs_button.setIconSize(QtCore.QSize(48, 48))
        subs_button.setObjectName('topright')
        ok_button = QtWidgets.QPushButton('')
        ok_button.setIcon(QtGui.QIcon('./buttons/ok.png'))
        ok_button.setIconSize(QtCore.QSize(48, 48))
        ok_button.setObjectName('center')

        connect_button = QtWidgets.QPushButton('')
        connect_button.setIcon(QtGui.QIcon('./buttons/curve-connector.png'))
        connect_button.setIconSize(QtCore.QSize(48, 48))
        connect_button.setObjectName('left')
        reset_button = QtWidgets.QPushButton('')
        reset_button.setIcon(QtGui.QIcon('./buttons/view-refresh.png'))
        reset_button.setIconSize(QtCore.QSize(48, 48))
        about_button = QtWidgets.QPushButton('')
        about_button.setIcon(QtGui.QIcon('./buttons/help-about.png'))
        about_button.setIconSize(QtCore.QSize(48, 48))
        about_button.setObjectName('right')

        hbox1.addStretch()
        hbox1.addWidget(connect_button)
        hbox1.addWidget(reset_button)
        hbox1.addWidget(about_button)
        hbox1.addStretch()

        up_button.setDisabled(True)

        vbox1.addStretch()
        vbox1.addWidget(menu_button)
        vbox1.addWidget(left_button)
        vbox1.addWidget(osd_button)
        vbox1.addStretch()

        vbox2.addStretch()
        vbox2.addWidget(up_button)
        vbox2.addWidget(ok_button)
        vbox2.addWidget(down_button)
        vbox2.addStretch()

        vbox3.addStretch()
        vbox3.addWidget(subs_button)
        vbox3.addWidget(right_button)
        vbox3.addWidget(back_button)
        vbox3.addStretch()

        hbox2.addStretch()
        hbox2.addLayout(vbox1)
        hbox2.addLayout(vbox2)
        hbox2.addLayout(vbox3)
        hbox2.addStretch()

        vbox4.addStretch()
        vbox4.addLayout(hbox1)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox2)
        vbox4.addStretch()

        self.main_box.addLayout(vbox4)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    sys.exit(app.exec_())
