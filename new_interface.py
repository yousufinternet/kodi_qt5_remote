from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from kodijson import PLAYER_VIDEO, Kodi
import shutil
from yalla_shoot_parser import get_matches_list
import time
import sys
import webbrowser
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

    def create_buttons(self, buttons_list):
        for item in buttons_list:
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

    def initUI(self):

        self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_box = QtWidgets.QHBoxLayout()
        self.main_box.setSpacing(0)

        self.main_box.addSpacing(30)

        # Matches list widget properties go here
        self.matches_widget = QtWidgets.QTableWidget(0, 3)
        self.matches_widget.setIconSize(QtCore.QSize(64, 64))
        self.matches_widget.horizontalHeader().hide()
        self.matches_widget.verticalHeader().hide()
        self.matches_widget.setLayoutDirection(QtCore.Qt.RightToLeft)
        # self.matches_widget.setAlternatingRowColors(True)
        self.matches_widget.setEditTriggers(
            QtWidgets.QTableWidget.NoEditTriggers)
        self.matches_widget.cellClicked.connect(
            lambda: webbrowser.open_new_tab(self.matches_list[self.matches_widget.currentRow()][5]))

        self.addButtons()

        # Expiremental Stylesheet coding

        self.setStyleSheet(
            'QWidget {background-color:\#232323; padding: 0px;}\
            QPushButton {background-color: black;\
            color: white;\
            border-style: outset;\
            border-width: 2px;\
            border-color: white;\
            font: bold 24px;\
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
            QPushButton#small:hover {font: normal 15px;}\
            QPushButton#small:pressed {font: normal 15px;}\
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
            QPushButton#rightred {border-bottom-right-radius: 15px;\
            border-top-right-radius: 15px; background-color: \#5a0000}\
            QPushButton#rightred:hover {background-color: \#b90000}\
            QPushButton#rightred:pressed {background-color: \#1d0000}\
            QPushButton#leftred {border-bottom-left-radius: 15px;\
            border-top-left-radius: 15px; background-color: \#5a0000}\
            QPushButton#leftred:hover {background-color: \#b90000}\
            QPushButton#leftred:pressed {background-color: \#1d0000}\
            QPushButton#leftsmall {border-bottom-left-radius: 15px;\
            border-top-left-radius: 15px; font: 15px;}\
            QPushButton#small {font: 15px; min-width: 40px;}\
            QTableWidget {background-color:\#232323; color: white;}\
            QSlider:groove{border: 1px solid white;\
            width: 8px;\
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:1 \#2a2a2a, stop:0 \#8d0000);}\
            QSlider:handle {border: 1px solid white;\
            background: black;\
            height: 20px;\
            width: 20px;\
            margin: -1px -5;\
            border-radius: 5px; }\
            QRadioButton{color: white;}\
            QLabel{color: white;}\
            '
        )
        # Starting the matches thread
        self.matches_thread = matchesThread()
        self.matches_thread.readysignal.connect(self.update_match_table)
        self.matches_thread.statussignal.connect(self.status_label_1.setText)
        self.matches_thread.start()

        self.oldPos = self.pos()

        # window settings
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowIcon(QtGui.QIcon('./Images/kodi_icon.png'))
        self.show()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    # def mouseMoveEvent(self, event):
    #     delta = QtCore.QPoint(
    #         (event.globalPos() - self.oldPos) * 2)
    #     self.move(self.x() + delta.x(), self.y() + delta.y())
    #     self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        delta = QtCore.QPoint(
            (event.globalPos() - self.oldPos) * self.devicePixelRatio())
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def update_match_table(self, matches_list):
        self.matches_list = matches_list
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

        # we want the buttons to stick to each other
        vboxes = [vbox1, vbox2, vbox3, vbox4, vbox5]
        hboxes = [hbox1, hbox2, hbox3, hbox4, hbox5]
        for vbox, hbox in zip(vboxes, hboxes):
            vbox.setSpacing(0)
            vbox.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
            hbox.setSpacing(0)
            hbox.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self.control_buttons = [
            # 1
            {'name': 'menu', 'object': None, 'style': 'topleft',
                'height': 64, 'Icon': 'menu.png', 'icon-size': 48, 'shortcut': None},
            # 2
            {'name': 'left', 'object': None, 'style': None,
             'height': 64, 'Icon': 'go-left.png', 'icon-size': 48, 'shortcut': 'Left'},
            # 3
            {'name': 'osd', 'object': None, 'style': 'botleft',
             'height': 64, 'Icon': 'osd.png', 'icon-size': 48, 'shortcut': None},
            # 4
            {'name': 'up', 'object': None, 'style': None,
                'height': 64, 'Icon': 'go-up.png', 'icon-size': 48, 'shortcut': 'Up'},
            # 5
            {'name': 'ok', 'object': None, 'style': None,
                'height': 64, 'Icon': 'ok.png', 'icon-size': 48, 'shortcut': 'Return'},
            # 6
            {'name': 'down', 'object': None, 'style': None,
                'height': 64, 'Icon': 'go-down.png', 'icon-size': 48, 'shortcut': 'Down'},
            # 7
            {'name': 'subs', 'object': None, 'style': 'topright',
                'height': 64, 'Icon': 'subtitles.png', 'icon-size': 48, 'shortcut': None},
            # 8
            {'name': 'right', 'object': None, 'style': None,
                'height': 64, 'Icon': 'go-right.png', 'icon-size': 48, 'shortcut': 'Right'},
            # 9
            {'name': 'back', 'object': None, 'style': 'botright',
                'height': 64, 'Icon': 'back.png', 'icon-size': 48, 'shortcut': 'Backspace'},
            # 10
            {'name': 'connect', 'object': None, 'style': 'left',
                'height': 64, 'Icon': 'curve-connector.png', 'icon-size': 48, 'shortcut': None},
            # 11
            {'name': 'reset', 'object': None, 'style': None,
                'height': 64, 'Icon': 'view-refresh.png', 'icon-size': 48, 'shortcut': None},
            # 12
            {'name': 'about', 'object': None, 'style': 'right',
                'height': 64, 'Icon': 'help-about.png', 'icon-size': 48, 'shortcut': None},
            # 13
            {'name': 'play', 'object': None, 'style': 'left',
                'height': 32, 'Icon': 'play.png', 'icon-size': 16, 'shortcut': 'c'},
            # 14
            {'name': 'stop', 'object': None, 'style': None,
                'height': 32, 'Icon': 'stop.png', 'icon-size': 16, 'shortcut': 'shift+c'},
            # 15
            {'name': 'rewind', 'object': None, 'style': None,
                'height': 32, 'Icon': 'rewind.png', 'icon-size': 16, 'shortcut': 'x'},
            # 16
            {'name': 'forward', 'object': None, 'style': 'right',
                'height': 32, 'Icon': 'forward.png', 'icon-size': 16, 'shortcut': 'v'},
            # 17
            {'name': 'Tomorrow', 'object': None, 'style': 'leftsmall',
                'height': None, 'Icon': None, 'icon-size': 16, 'shortcut': None},
            # 18
            {'name': 'Today', 'object': None, 'style': 'small',
                'height': None, 'Icon': None, 'icon-size': 16, 'shortcut': None},
            # 19
            {'name': 'Yesterday', 'object': None, 'style': 'rightsmall',
                'height': None, 'Icon': None, 'icon-size': 16, 'shortcut': None},
            # 20
            {'name': 'quit_kodi', 'object': None, 'style': 'leftred',
                'height': 32, 'Icon': 'exit_kodi.png', 'icon-size': 24, 'shortcut': None},
            # 21
            {'name': 'minimize', 'object': None, 'style': None,
                'height': 32, 'Icon': 'minimize.png', 'icon-size': 24, 'shortcut': None},
            # 22
            {'name': 'close', 'object': None, 'style': 'rightred',
                'height': 32, 'Icon': 'error.png', 'icon-size': 24, 'shortcut': None},
        ]

        self.channels_buttons = [{'name': 'Ch%s' % i, 'object': None, 'style': 'small', 'height': 32,
                                  'Icon': None, 'icon-size': None, 'shortcut': None} for i in range(1, 26)]

        # create the QPushButton objects using the specified settings
        self.create_buttons(self.control_buttons)
        self.create_buttons(self.channels_buttons)

        # Subtitles menu object, see also updatesub function
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

        # channels quality and organization code starts here
        vbox8 = QtWidgets.QVBoxLayout()
        vbox8.setSpacing(0)
        options_hbox = QtWidgets.QHBoxLayout()
        self.option_240 = QtWidgets.QRadioButton('240')
        self.option_360 = QtWidgets.QRadioButton('360')
        self.option_720 = QtWidgets.QRadioButton('720')
        options_hbox.addStretch()
        options_hbox.addWidget(self.option_240)
        options_hbox.addWidget(self.option_360)
        options_hbox.addWidget(self.option_720)
        options_hbox.addStretch()
        vbox8.addLayout(options_hbox)

        for idx, item in enumerate(self.channels_buttons):
            if idx % 5 == 0:
                if hbox:
                    hbox.addStretch()
                hbox = QtWidgets.QHBoxLayout()
                hbox.setSpacing(0)
                hbox.addStretch()
                vbox8.addLayout(hbox)
            item['object'].setCheckable(True)
            item['object'].setDisabled(True)
            hbox.addWidget(item['object'])
        hbox.addStretch()

        main_box2 = QtWidgets.QHBoxLayout()
        vbox7 = QtWidgets.QVBoxLayout()
        self.open_url = QtWidgets.QPushButton('Play a URL')
        self.send_text = QtWidgets.QPushButton('Send text')
        vbox7.addWidget(self.open_url)
        vbox7.addWidget(self.send_text)
        main_box2.addLayout(vbox8)
        main_box2.addLayout(vbox7)
        # channels quality and organization code ends here

        for idx, item in enumerate(self.control_buttons[9:12]):
            hbox1.addWidget(item['object'])

        # Volume slider and the mute button
        self.volume_slider = QtWidgets.QSlider()
        self.volume_slider.setValue(100)
        self.volume_slider.setMinimumHeight(200)
        self.mutebutton = QtWidgets.QPushButton()
        self.mutebutton.setFlat(True)
        self.mutebutton.setIcon(QtGui.QIcon('buttons/volume_full.png'))
        self.mutebutton.setStyleSheet('background-color: #232323;\
        border-width: 0px;')

        vbox7 = QtWidgets.QVBoxLayout()
        vbox7.addStretch()
        vbox7.addWidget(self.volume_slider)
        vbox7.setAlignment(self.volume_slider, QtCore.Qt.AlignHCenter)
        vbox7.addWidget(self.mutebutton)
        vbox7.setSpacing(0)
        vbox7.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        vbox7.addStretch()
        vbox7.setGeometry(QtCore.QRect(0, 0, 100, 80))

        for vbox in vboxes[:3]:
            hbox2.addLayout(vbox)

        for idx, item in enumerate(self.control_buttons[12:16]):
            item['object'].setDisabled(True)
            hbox3.addWidget(item['object'])

        self.status_label_1 = QtWidgets.QLabel('Ready')
        self.status_label_1.setFont(QtGui.QFont('Monospace', 7))

        vbox4.addLayout(hbox1)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox2)
        vbox4.addSpacing(30)
        vbox4.addLayout(hbox3)
        vbox.addStretch()

        hbox4.addStretch()
        for item in self.control_buttons[16:19]:
            hbox4.addWidget(item['object'])
        hbox4.addStretch()

        hbox5.addStretch()
        for item in self.control_buttons[19:]:
            hbox5.addWidget(item['object'])
            hbox5.setAlignment(item['object'], QtCore.Qt.AlignTop)

        vbox5.addLayout(hbox5)
        vbox5.addSpacing(30)
        vbox5.addLayout(hbox4)
        vbox5.setAlignment(hbox4, QtCore.Qt.AlignHCenter)
        vbox5.addSpacing(30)
        vbox5.addWidget(self.matches_widget)
        vbox5.setAlignment(self.matches_widget, QtCore.Qt.AlignHCenter)

        self.main_box.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))
        self.main_box.addLayout(vbox7)
        self.main_box.addSpacing(20)
        self.main_box.addLayout(vbox4)
        self.main_box.addSpacing(30)
        self.main_box.addLayout(vbox5)
        self.main_box.setSpacing(0)

        vbox6.addLayout(self.main_box)
        vbox6.addLayout(main_box2)
        vbox6.addSpacing(20)
        vbox6.addWidget(self.status_label_1)

        self.setLayout(vbox6)

    def setvolume(self, volume):
        self.xbmc_conn.Application.setVolume(volume=volume)
        if volume >= 66:
            self.mutebutton.setIcon(QtGui.QIcon('buttons/volume_full.png'))
        elif volume >= 33:
            self.mutebutton.setIcon(QtGui.QIcon('buttons/volume_med.png'))
        elif volume > 0:
            self.mutebutton.setIcon(QtGui.QIcon('buttons/volume_low.png'))
        elif volume == 0:
            self.mutebutton.setIcon(QtGui.QIcon('buttons/volume_mute.png'))

    def openurlf(self):
        ipdialog = QtWidgets.QInputDialog()
        text, ok = ipdialog.getText(self, 'URL',
                                    'Please enter the URL you want to play:', text="")
        if ok:
            self.xbmc_conn.Player.Open(item={"file": text})

    def commander(self, name):
        print(name)
        if not internet(host='192.168.1.109', port=8081, timeout=5):
            self.status_label_1.setText('Oops disconnected from kodi server')
            self.xbmc_conn = None
            for button in self.control_buttons[:9]:
                button['object'].setDisabled(True)
            for button in self.control_buttons[12:16]:
                button['object'].setDisabled(True)
            return

        if 'Ch' in name:
            for channel in self.channels_buttons:
                if channel['name'] != name:
                    channel['object'].setChecked(False)
                else:
                    channel['object'].setChecked(True)

        if 'Ch' in name and self.option_240.isChecked():
            self.xbmc_conn.Player.Open(
                item={"file": 'http://stream.elcld.com:6001/ch%s/stream_240p/stream.m3u8' % re.match(r'Ch(\d+)', name).group(1)})

        if 'Ch' in name and self.option_360.isChecked():
            self.xbmc_conn.Player.Open(
                item={"file": 'http://stream.elcld.com:6001/ch%s/stream_360p/stream.m3u8' % re.match(r'Ch(\d+)', name).group(1)})

        if 'Ch' in name and self.option_720.isChecked():
            self.xbmc_conn.Player.Open(
                item={"file": 'http://stream.elcld.com:6001/ch%s/stream_720p/stream.m3u8' % re.match(r'Ch(\d+)', name).group(1)})

        if name == 'connect':
            if shutil.os.path.exists('xbmcconf.cfg'):
                with open('xbmcconf.cfg', 'r') as f_obj:
                    xbmc_address = f_obj.read()
                try:
                    self.xbmc_conn = Kodi(xbmc_address)
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
                        self.xbmc_conn = Kodi(text)
                        self.status_label_1.setText(
                            'Successfully connected to ' +
                            re.search(r'\d+\.\d+\.\d+\.\d+', text).group())
                    else:
                        return
            else:
                ipdialog = QtWidgets.QInputDialog()
                text, ok = ipdialog.getText(self, 'KODI IP',
                                            'Please enter your KODI IP:', text="http://192.168.0.0:8080/jsonrpc")
                if ok:
                    with open('xbmcconf.cfg', 'w+') as f_obj:
                        f_obj.write(text)
                    self.xbmc_conn = Kodi(text)
                    self.status_label_1.setText(
                        'Successfully connected to ' +
                        re.search(r'\d+\.\d+\.\d+\.\d+', text).group())
                else:
                    return

            self.open_url.clicked.connect(self.openurlf)
            self.volume_slider.valueChanged[int].connect(self.setvolume)
            for item in self.control_buttons:
                item['object'].setDisabled(False)
            for item in self.channels_buttons:
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

        if name == 'quit_kodi':
            self.xbmc_conn.Application.Quit()

        if name == 'close':
            QtWidgets.qApp.quit()

        if name == 'minimize':
            self.showMinimized()

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

        if name == 'osd':
            self.xbmc_conn.Input.ShowOSD()

        if name == 'menu':
            self.xbmc_conn.Input.ContextMenu()

        if name == 'stop':
            self.xbmc_conn.Player.Stop([PLAYER_VIDEO])

        if name == 'play':
            self.xbmc_conn.Player.PlayPause([PLAYER_VIDEO])

        if name == 'rewind':
            self.xbmc_conn.Input.ExecuteAction(action="rewind")

        if name == 'forward':
            self.xbmc_conn.Input.ExecuteAction(action="fastforward")

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
