from PyQt5 import QtWidgets, QtCore, QtGui, Qt
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
        # self.main_box.setAlignment(Qt.Qt.AlignCenter)
        self.setLayout(self.main_box)

        self.setStyleSheet(
            'QWidget {background-color:\#232323;}\
            QPushButton {background-color: black;\
            border-style: outset;\
            border-width: 2px;\
            border-color: white;\
            font: bold t4px;\
            min-width: 1em;\
            padding: 5px;}\
            QPushButton:hover {background-color: \#414141;\
            border-style: outset;\
            border-width: 5px;\
            border-color: white;\
            font: bold 24px;\
            min-width: 1em;\
            padding: 5px;}\
            QPushButton:pressed {background-color: \#232323;\
            border-style: outset;\
            border-width: 5px;\
            border-color: white;\
            font: bold 24px;\
            min-width: 1em;\
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
            self.matches_widget.setMinimumWidth(total_table_width)
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
        hbox3 = QtWidgets.QHBoxLayout()

        vboxes = [vbox1, vbox2, vbox3, vbox4, vbox5]
        hboxes = [hbox1, hbox2, hbox3]
        # we want the buttons to stick to each other
        vbox1.setSpacing(0)
        vbox2.setSpacing(0)
        vbox3.setSpacing(0)

        control_buttons = [
            {'name': 'menu', 'object': None, 'style': 'topleft',
                'height': None, 'Icon': 'menu.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'right', 'object': None, 'style': None,
             'height': None, 'Icon': 'go-left.png', 'icon-size': 48, 'shortcut': 'Right'},
            {'name': 'osd', 'object': None, 'style': 'botleft',
             'height': None, 'Icon': 'osd.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'up', 'object': None, 'style': None,
                'height': None, 'Icon': 'go-up.png', 'icon-size': 48, 'shortcut': 'Up'},
            {'name': 'ok', 'object': None, 'style': None,
                'height': None, 'Icon': 'ok.png', 'icon-size': 48, 'shortcut': 'Return'},
            {'name': 'down', 'object': None, 'style': None,
                'height': None, 'Icon': 'go-down.png', 'icon-size': 48, 'shortcut': 'Down'},
            {'name': 'subs', 'object': None, 'style': 'topright',
                'height': None, 'Icon': 'subtitles.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'right', 'object': None, 'style': None,
                'height': None, 'Icon': 'go-right.png', 'icon-size': 48, 'shortcut': 'Right'},
            {'name': 'back', 'object': None, 'style': 'botright',
                'height': None, 'Icon': 'back.png', 'icon-size': 48, 'shortcut': 'Backspace'},
        ]

        for item in control_buttons:
            item['object'] = QtWidgets.QPushButton()
            item['object'].setIcon(QtGui.QIcon('./buttons/' + item['Icon']))
            item['object'].setIconSize(QtCore.QSize(
                item['icon-size'], item['icon-size']))
            if item['style'] is not None:
                item['object'].setObjectName(item['style'])
            if item['height'] is not None:
                item['object'].setFixedHeight(item['height'])

        for idx, item in enumerate(control_buttons):
            vbox_idx = int(idx / 3)
            if idx % 3 == 0 and idx == 0:
                vboxes[vbox_idx].addStretch()
            elif idx % 3 == 0 and idx > 0:
                vboxes[vbox_idx].addStretch()
                vboxes[vbox_idx - 1].addStretch()
            vboxes[vbox_idx].addWidget(item['object'])

        hbox2.addStretch()
        for vbox in vboxes[:3]:
            hbox2.addLayout(vbox)
        hbox2.addStretch()

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

        play_button = QtWidgets.QPushButton('')
        play_button.setIcon(QtGui.QIcon('./buttons/play.png'))
        play_button.setIconSize(QtCore.QSize(16, 16))
        play_button.setObjectName('left')
        play_button.setFixedSize(32, 32)
        stop_button = QtWidgets.QPushButton('')
        stop_button.setIcon(QtGui.QIcon('./buttons/stop.png'))
        stop_button.setIconSize(QtCore.QSize(16, 16))
        stop_button.setFixedHeight(40)
        rewind_button = QtWidgets.QPushButton('')
        rewind_button.setIcon(QtGui.QIcon('./buttons/rewind.png'))
        rewind_button.setIconSize(QtCore.QSize(16, 16))
        rewind_button.setFixedHeight(32)
        forward_button = QtWidgets.QPushButton('')
        forward_button.setIcon(QtGui.QIcon('./buttons/forward.png'))
        forward_button.setIconSize(QtCore.QSize(16, 16))
        forward_button.setObjectName('right')
        forward_button.setFixedHeight(40)

        hbox1.addStretch()
        hbox1.addWidget(connect_button)
        hbox1.addWidget(reset_button)
        hbox1.addWidget(about_button)
        hbox1.addStretch()

        # up_button.setDisabled(True)

        # vbox1.addStretch()
        # vbox1.addWidget(menu_button)
        # vbox1.addWidget(left_button)
        # vbox1.addWidget(osd_button)
        # vbox1.addStretch()

        # vbox2.addStretch()
        # vbox2.addWidget(up_button)
        # vbox2.addWidget(ok_button)
        # vbox2.addWidget(down_button)
        # vbox2.addStretch()

        # vbox3.addStretch()
        # vbox3.addWidget(subs_button)
        # vbox3.addWidget(right_button)
        # vbox3.addWidget(back_button)
        # vbox3.addStretch()

        # hbox2.addStretch()
        # hbox2.addLayout(vbox1)
        # hbox2.addLayout(vbox2)
        # hbox2.addLayout(vbox3)
        # hbox2.addStretch()

        hbox3.addStretch()
        hbox3.addWidget(play_button)
        hbox3.addWidget(stop_button)
        hbox3.addWidget(rewind_button)
        hbox3.addWidget(forward_button)
        hbox3.addStretch()

        vbox4.addStretch()
        vbox4.addLayout(hbox1)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox2)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox3)
        vbox4.addStretch()

        self.main_box.addLayout(vbox4)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    sys.exit(app.exec_())
