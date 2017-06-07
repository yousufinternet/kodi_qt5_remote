from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from xbmcjson import PLAYER_VIDEO, XBMC
import shutil
from yalla_shoot_parser import get_matches_list
import time
import sys
import shutil
from functools import partial
import socket
import datetime
import re


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False


class matchesThread(QtCore.QThread):
    readysignal = QtCore.pyqtSignal(list, name='matches_ready')
    statussignal = QtCore.pyqtSignal(str, name='status_string')

    def __init__(self, day_flag='today'):
        super().__init__()
        self.day_flag = day_flag

    def run(self):
        sleep_amount = 60
        while True:
            if internet():
                matches_list = get_matches_list(self.day_flag)
                self.statussignal.emit(
                    'Updated matches list on: ' + datetime.datetime.now().strftime('%H:%M'))
            else:
                matches_list = [['./buttons/error.png', 'Error', 'لا يوجد إنترنت',
                                 'Error', './buttons/error.png', None, 'Error']]
                sleep_amount = 30
                self.statussignal.emit('Failed to connect to the internet')
            self.readysignal.emit(matches_list)
            time.sleep(sleep_amount)


class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.main_box = QtWidgets.QHBoxLayout()
        self.main_box.setSpacing(0)

        self.main_box.addSpacing(30)

        # Matches list widget properties go here
        self.matches_widget = QtWidgets.QTableWidget(0, 3)
        self.matches_widget.setIconSize(QtCore.QSize(64, 64))
        self.matches_widget.horizontalHeader().hide()
        self.matches_widget.verticalHeader().hide()
        # self.matches_widget.setAlternatingRowColors(True)
        self.matches_widget.setEditTriggers(
            QtWidgets.QTableWidget.NoEditTriggers)

        self.addButtons()

        # Expiremental Stylesheet coding

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
            QPushButton#rightsmall {border-bottom-right-radius: 15px;\
            border-top-right-radius: 15px; font: 15px;}\
            QPushButton#leftsmall {border-bottom-left-radius: 15px;\
            border-top-left-radius: 15px; font: 15px;}\
            QPushButton#small {font: 15px;}\
            QTableWidget {background-color:\#232323;}\
            '
        )
        # Starting the matches thread
        self.matches_thread = matchesThread()
        self.matches_thread.readysignal.connect(self.update_match_table)
        self.matches_thread.statussignal.connect(self.status_label_1.setText)
        self.matches_thread.start()

        # window settings
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
            self.matches_widget.setFixedWidth(total_table_width)
        pass

    def updatesub(self):
        subs_list = self.xbmc_conn.Player.GetProperties(
            playerid=PLAYER_VIDEO, properties=['subtitles'])
        subs_list = subs_list['result']['subtitles']
        self.subs_menu.clear()
        off_action = QtWidgets.QAction('Off', self)
        self.subs_menu.addAction(off_action)
        off_action.triggered.connect(lambda: self.xbmc_conn.Player.SetSubtitle(
            playerid=PLAYER_VIDEO, subtitle="off", enable=False))
        for item in subs_list:
            item_action = QtWidgets.QAction(
                item['language'].title(), self.control_buttons[6]['object'])
            item_action.triggered.connect(lambda: self.xbmc_conn.Player.SetSubtitle(
                playerid=PLAYER_VIDEO, subtitle=item['index'], enable=True))
            self.subs_menu.addAction(item_action)

    def addButtons(self):
        # all the boxes layouts that will be added to the main horizontal
        # layout
        vbox1 = QtWidgets.QVBoxLayout()
        vbox2 = QtWidgets.QVBoxLayout()
        vbox3 = QtWidgets.QVBoxLayout()
        vbox4 = QtWidgets.QVBoxLayout()
        vbox5 = QtWidgets.QVBoxLayout()
        vbox6 = QtWidgets.QVBoxLayout()
        hbox1 = QtWidgets.QHBoxLayout()
        hbox2 = QtWidgets.QHBoxLayout()
        hbox3 = QtWidgets.QHBoxLayout()
        hbox4 = QtWidgets.QHBoxLayout()
        hbox5 = QtWidgets.QHBoxLayout()

        vboxes = [vbox1, vbox2, vbox3, vbox4, vbox5]
        hboxes = [hbox1, hbox2, hbox3]
        # we want the buttons to stick to each other
        vbox1.setSpacing(0)
        vbox2.setSpacing(0)
        vbox3.setSpacing(0)
        vbox4.setSpacing(0)

        self.control_buttons = [
            {'name': 'menu', 'object': None, 'style': 'topleft',
                'height': 64, 'Icon': 'menu.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'left', 'object': None, 'style': None,
             'height': 64, 'Icon': 'go-left.png', 'icon-size': 48, 'shortcut': 'Left'},
            {'name': 'osd', 'object': None, 'style': 'botleft',
             'height': 64, 'Icon': 'osd.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'up', 'object': None, 'style': None,
                'height': 64, 'Icon': 'go-up.png', 'icon-size': 48, 'shortcut': 'Up'},
            {'name': 'ok', 'object': None, 'style': None,
                'height': 64, 'Icon': 'ok.png', 'icon-size': 48, 'shortcut': 'Return'},
            {'name': 'down', 'object': None, 'style': None,
                'height': 64, 'Icon': 'go-down.png', 'icon-size': 48, 'shortcut': 'Down'},
            {'name': 'subs', 'object': None, 'style': 'topright',
                'height': 64, 'Icon': 'subtitles.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'right', 'object': None, 'style': None,
                'height': 64, 'Icon': 'go-right.png', 'icon-size': 48, 'shortcut': 'Right'},
            {'name': 'back', 'object': None, 'style': 'botright',
                'height': 64, 'Icon': 'back.png', 'icon-size': 48, 'shortcut': 'Backspace'},
            {'name': 'connect', 'object': None, 'style': 'left',
                'height': 64, 'Icon': 'curve-connector.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'reset', 'object': None, 'style': None,
                'height': 64, 'Icon': 'view-refresh.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'about', 'object': None, 'style': 'right',
                'height': 64, 'Icon': 'help-about.png', 'icon-size': 48, 'shortcut': None},
            {'name': 'play', 'object': None, 'style': 'left',
                'height': 32, 'Icon': 'play.png', 'icon-size': 16, 'shortcut': 'c'},
            {'name': 'stop', 'object': None, 'style': None,
                'height': 32, 'Icon': 'stop.png', 'icon-size': 16, 'shortcut': 'shift+c'},
            {'name': 'rewind', 'object': None, 'style': None,
                'height': 32, 'Icon': 'rewind.png', 'icon-size': 16, 'shortcut': 'x'},
            {'name': 'forward', 'object': None, 'style': 'right',
                'height': 32, 'Icon': 'forward.png', 'icon-size': 16, 'shortcut': 'v'},
            {'name': 'Tomorrow', 'object': None, 'style': 'leftsmall',
                'height': None, 'Icon': None, 'icon-size': 16, 'shortcut': None},
            {'name': 'Today', 'object': None, 'style': 'small',
                'height': None, 'Icon': None, 'icon-size': 16, 'shortcut': None},
            {'name': 'Yesterday', 'object': None, 'style': 'rightsmall',
                'height': None, 'Icon': None, 'icon-size': 16, 'shortcut': None},

        ]

        for item in self.control_buttons:
            item['object'] = QtWidgets.QPushButton()
            if item['Icon'] is not None:
                item['object'].setIcon(
                    QtGui.QIcon('./buttons/' + item['Icon']))
                item['object'].setIconSize(QtCore.QSize(
                    item['icon-size'], item['icon-size']))
            else:
                item['object'].setText(item['name'])
            if item['style'] is not None:
                item['object'].setObjectName(item['style'])
            if item['height'] is not None:
                item['object'].setFixedSize(item['height'], item['height'])
            if item['shortcut'] is not None:
                item['object'].setShortcut(item['shortcut'])
            item['object'].clicked.connect(
                partial(self.commander, item['name']))

        self.subs_menu = QtWidgets.QMenu(self.control_buttons[6]['object'])
        self.control_buttons[6]['object'].setMenu(self.subs_menu)
        self.subs_menu.aboutToShow.connect(self.updatesub)

        for idx, item in enumerate(self.control_buttons[:9]):
            vbox_idx = int(idx / 3)
            item['object'].setDisabled(True)
            if idx % 3 == 0 and idx == 0:
                vboxes[vbox_idx].addStretch()
            elif idx % 3 == 0 and idx > 0:
                vboxes[vbox_idx].addStretch()
                vboxes[vbox_idx - 1].addStretch()
            vboxes[vbox_idx].addWidget(item['object'])

        hbox1.addStretch()
        for idx, item in enumerate(self.control_buttons[9:12]):
            hbox1.addWidget(item['object'])
        hbox1.addStretch()

        hbox2.addStretch()
        for vbox in vboxes[:3]:
            hbox2.addLayout(vbox)
        hbox2.addStretch()

        hbox3.addStretch()
        for idx, item in enumerate(self.control_buttons[12:16]):
            item['object'].setDisabled(True)
            hbox3.addWidget(item['object'])
        hbox3.addStretch()

        self.status_label_1 = QtWidgets.QLabel('Ready')
        self.status_label_1.setFont(QtGui.QFont('Monospace', 7))

        # vbox4.addStretch()
        vbox4.addLayout(hbox1)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox2)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox3)
        vbox.addStretch()

        hbox4.addStretch()
        for item in self.control_buttons[16:]:
            hbox4.addWidget(item['object'])
        hbox4.addStretch()

        vbox5.addLayout(hbox4)
        vbox5.setAlignment(hbox4, QtCore.Qt.AlignHCenter)
        vbox5.addSpacing(30)
        vbox5.addWidget(self.matches_widget)
        vbox5.setAlignment(self.matches_widget, QtCore.Qt.AlignHCenter)

        self.main_box.addLayout(vbox4)
        self.main_box.addSpacing(30)
        self.main_box.addLayout(vbox5)

        vbox6.addLayout(self.main_box)
        vbox6.addSpacing(20)
        vbox6.addWidget(self.status_label_1)

        # self.main_box.addWidget(self.matches_widget)
        # self.main_box.setAlignment(
        # self.matches_widget, QtCore.Qt.AlignHCenter)
        self.setLayout(vbox6)

    def commander(self, name):
        print(name)
        if not internet(host='192.168.1.109', port=8081):
            self.status_label_1.setText('Oops disconnected from kodi server')
            self.xbmc_conn = None
            for button in self.control_buttons[:9]:
                button['object'].setDisabled(True)
            for button in self.control_buttons[12:]:
                button['object'].setDisabled(True)
            return

        if name == 'connect':
            if shutil.os.path.exists('xbmcconf.cfg'):
                with open('xbmcconf.cfg', 'r') as f_obj:
                    xbmc_address = f_obj.read()
                try:
                    self.xbmc_conn = XBMC(xbmc_address)
                    self.status_label_1.setText(
                        'Successfully connected to ' +
                        re.search(r'\d+\.\d+\.\d+\.\d+', xbmc_address).group())
                except:
                    ipdialog = QtWidgets.QInputDialog()
                    text, ok = ipdialog.getText(self, 'KODI IP',
                                                'Please enter your KODI IP:', text="http://192.168.0.0:8080/jsonrpc")
                    if ok:
                        with open('xbmcconf.cfg', 'w') as f_obj:
                            f_obj.write(text)
                        self.xbmc_conn = XBMC(text)
                        self.status_label_1.setText(
                            'Successfully connected to ' +
                            re.search(r'\d+\.\d+\.\d+\.\d+', text).group())
            else:
                ipdialog = QtWidgets.QInputDialog()
                text, ok = ipdialog.getText(self, 'KODI IP',
                                            'Please enter your KODI IP:', text="http://192.168.0.0:8080/jsonrpc")
                if ok:
                    with open('xbmcconf.cfg', 'w+') as f_obj:
                        f_obj.write(text)
                    self.xbmc_conn = XBMC(text)
                    self.status_label_1.setText(
                        'Successfully connected to ' +
                        re.search(r'\d+\.\d+\.\d+\.\d+', text).group())
            for item in self.control_buttons:
                item['object'].setDisabled(False)

        if name == 'reset':
            ipdialog = QtWidgets.QInputDialog()
            text, ok = ipdialog.getText(self, 'KODI IP',
                                        'Please enter your KODI IP:', text="http://192.168.0.0:8080/jsonrpc")
            if ok:
                with open('xbmcconf.cfg', 'w') as f_obj:
                    f_obj.write(text)

        if name == 'about':
            pass

        if name == 'up':
            self.xbmc_conn.Input.Up()

        if name == 'down':
            self.xbmc_conn.Input.Down()

        if name == 'right':
            self.xbmc_conn.Input.Right()

        if name == 'left':
            self.xbmc_conn.Input.Left()

        if name == 'ok':
            self.xbmc_conn.Input.Select()

        if name == 'back':
            self.xbmc_conn.Input.Back()

        if name == 'Tomorrow':
            self.matches_thread.terminate()
            self.matches_thread = matchesThread('tomorrow')
            self.matches_thread.readysignal.connect(self.update_match_table)
            self.matches_thread.statussignal.connect(
                self.status_label_1.setText)
            self.matches_thread.start()

        if name == 'Yesterday':
            self.matches_thread.terminate()
            self.matches_thread = matchesThread('yesterday')
            self.matches_thread.readysignal.connect(self.update_match_table)
            self.matches_thread.statussignal.connect(
                self.status_label_1.setText)
            self.matches_thread.start()

        if name == 'Today':
            self.matches_thread.terminate()
            self.matches_thread = matchesThread()
            self.matches_thread.readysignal.connect(self.update_match_table)
            self.matches_thread.statussignal.connect(
                self.status_label_1.setText)
            self.matches_thread.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    sys.exit(app.exec_())
