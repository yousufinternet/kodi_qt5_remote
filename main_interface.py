#!/usr/bin/env python
import sys
from PyQt5.QtWidgets import (QWidget, QGridLayout, QInputDialog,
                             QPushButton, QSlider, QTableWidget, QTableWidgetItem,
                             QApplication, QLabel, QVBoxLayout, QMenu, QAction,
                             QHBoxLayout, QSizePolicy, QStatusBar, QAbstractButton)
from PyQt5.QtGui import QFont, QIcon, QPainter, QPixmap
from PyQt5.QtCore import Qt, QSize, QRect

from xbmcjson import XBMC, PLAYER_VIDEO
from yalla_shoot_parser import get_matches_list
import shutil
import time
import threading
import webbrowser

# added a note to see how git behaves
# new change on a specific branch, now merged with master
# this one is to test commiting from visual studio code

class PicButton(QAbstractButton):
    def __init__(self, icon):
        super().__init__()
        self.pixmap = QPixmap('./buttons/weird.png')
        self.pixmap_hover = QPixmap('./buttons/weird_hover.png')
        self.pixmap_pressed = QPixmap('./buttons/weird-pressed.png')
        self.icon = icon

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)
        painter.drawPixmap(event.rect(), self.icon)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(100, 100)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.day_flag = 'today'
        self.grid = QGridLayout()
        self.hbox = QHBoxLayout()
        self.yalla_vbox = QVBoxLayout()
        self.grid.setSpacing(20)
        self.setLayout(self.grid)
        self.xbmc_conn = None

        self.button_map = {}
        self.createbuttons()
        self.button_map['Play/Pause'].setCheckable(True)
        # the match list toggle button
        self.match_list_toggle = QPushButton('<')
        self.match_list_toggle.setSizePolicy(QSizePolicy().Fixed, QSizePolicy().Expanding)
        self.match_list_toggle.setMaximumWidth(40)
        self.grid.addWidget(self.match_list_toggle, 1, 4, 4, 1)
        self.match_list_toggle.clicked.connect(self.toggle_matches)

        # Volume Slider
        volumeslider = QSlider(Qt.Vertical, self)
        volumeslider.setFixedWidth(40)
        volumeslider.setValue(100)
        volumeslider.valueChanged[int].connect(self.setvolume)
        self.grid.addWidget(volumeslider, 1, 3, 3, 1)

        # the math list part
        self.matches_font = QFont('Noto Sans', 20)
        self.matches_list_widget = QTableWidget(0, 3)
        self.matches_list_widget.setSortingEnabled(False)
        self.matches_list_widget.horizontalHeader().hide()
        self.matches_list_widget.verticalHeader().hide()
        self.matches_list_widget.setFont(self.matches_font)
        self.matches_list_widget.setAlternatingRowColors(True)
        # matches_list_widget.setFont(matches_font)
        self.yalla_vbox.addWidget(self.matches_list_widget)
        self.grid.addLayout(self.yalla_vbox, 0, 5, 5, 4)
        self.matches_list_widget.setIconSize(QSize(64, 64))
        # self.matches_list_widget.setSelectionMode(0)
        self.matches_list_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.matches_list_widget.setLayoutDirection(Qt.RightToLeft)
        self.matches_list_widget.cellClicked.connect(self.openmatch)

        # Status label

        self.grid.setVerticalSpacing(0)
        self.grid.setHorizontalSpacing(0)

        # Subs menu related coding
        self.menu_obj = QMenu(self.button_map['Subs'])
        self.button_map['Subs'].setMenu(self.menu_obj)
        self.menu_obj.aboutToShow.connect(self.updatesubsmenu)

        # General Window settings
        # self.setGeometry(300, 300, 1200, 300)
        self.setGeometry(300, 300, 1200, 300)
        self.updateGeometry()
        self.setWindowTitle('Kodi Remote Control')
        self.show()
        self.dthread_stop = threading.Event()
        self.download_thread = threading.Thread(
            target=self.updatematchlist, args=[self.dthread_stop])
        self.download_thread.daemon = True
        self.download_thread.start()

    def updatematchlist(self, stop_event):
        while (not stop_event.is_set()):
            # Add Matches to the list widget
            self.matches_list = get_matches_list(self.day_flag)
            self.matches_list_widget.setRowCount(len(self.matches_list))
            # self.matches_list_widget.clear()
            for idx, match in enumerate(self.matches_list):
                print('refreshing')
                self.matches_list_widget.setRowHeight(idx, 70)
                right_icon = QIcon(match[0])
                left_icon = QIcon(match[4])
                right_item = QTableWidgetItem(right_icon, '')
                right_item.setToolTip(match[1])
                left_item = QTableWidgetItem(left_icon, '')
                left_item.setToolTip(match[3])
                match_time = QTableWidgetItem(match[2])
                match_time.setToolTip(match[6])
                self.matches_list_widget.setItem(idx, 1, match_time)
                self.matches_list_widget.setItem(idx, 0, right_item)
                self.matches_list_widget.setItem(idx, 2, left_item)
                self.matches_list_widget.resizeColumnsToContents()
                total_table_width = sum([self.matches_list_widget.columnWidth(i)
                                         for i in range(0, 3)])
                self.matches_list_widget.setMinimumWidth(total_table_width + 2)
            stop_event.wait(60)

    def openmatch(self, row, column):
        webbrowser.open_new_tab(self.matches_list[row][5])
        print(self.matches_list[row][5])

    def updatesubsmenu(self):
        if self.xbmc_conn is not None:
            subs_list = self.xbmc_conn.Player.GetProperties(
                playerid=PLAYER_VIDEO, properties=['subtitles'])
            subs_list = subs_list['result']['subtitles']
            self.menu_obj.clear()
            off_action = QAction('Off', self)
            self.menu_obj.addAction(off_action)
            off_action.triggered.connect(lambda: self.xbmc_conn.Player.SetSubtitle(
                playerid=PLAYER_VIDEO, subtitle="off", enable=False))
            for item in subs_list:
                item_action = QAction(item['language'].title(), self.button_map['Subs'])
                item_action.triggered.connect(lambda: self.xbmc_conn.Player.SetSubtitle(
                    playerid=PLAYER_VIDEO, subtitle=item['index'], enable=True))
                self.menu_obj.addAction(item_action)

    def createbuttons(self):
        names = ['Menu', 'Up', 'Subs',
                 'Left', 'OK', 'Right',
                 'OSD', 'Down', 'Back']
        positions = [(i, j) for i in range(1, 4) for j in range(3)]

        for position, name in zip(positions, names):
            button = QPushButton(name)
            button.clicked.connect(self.commander)
            button.setDisabled(True)
            self.save_button(button)
            self.grid.addWidget(button, *position)
        self.button_map['Up'].setShortcut('Up')
        self.button_map['Up']
        self.button_map['Down'].setShortcut('Down')
        self.button_map['Right'].setShortcut('Right')
        self.button_map['Left'].setShortcut('Left')
        self.button_map['OK'].setShortcut('Return')
        self.button_map['Back'].setShortcut('BackSpace')

        # PLayback buttons
        playback = ['Play/Pause', 'Stop', 'Forward', 'Rewind', 'Info']
        for item in playback:
            button = QPushButton(item)
            button.clicked.connect(self.commander)
            button.setDisabled(True)
            self.save_button(button)
            self.hbox.addWidget(button)
        self.grid.addLayout(self.hbox, 4, 0, 1, 4)
        self.button_map['Play/Pause'].setShortcut('Space')

        # yalla-shoot table control buttons
        self.yalla_box = QHBoxLayout()
        yalla_buttons = ['⇐', 'Today', '⇒']
        for item in yalla_buttons:
            button = QPushButton(item)
            button.setCheckable(True)
            button.clicked.connect(self.commander)
            self.save_button(button)
            self.yalla_box.addWidget(button)
        self.yalla_vbox.addLayout(self.yalla_box)

        # Connect to KODI button
        hbox = QHBoxLayout()
        self.connect_btn = PicButton(QPixmap('./buttons/curve-connector.png'))
        self.connect_btn.setFixedSize(self.connect_btn.sizeHint())
        self.connect_btn.setToolTip('Connect to Kodi')
        # self.connect_btn.setIcon(QIcon('./buttons/curve-connector.svg'))
        hbox.addWidget(self.connect_btn)
        self.connect_btn.clicked.connect(self.loadconfig)

        # Delete xbmc_conf file button
        delete_config_btn = QPushButton('Reset Conf')
        delete_config_btn.clicked.connect(self.delete_config)
        hbox.addWidget(delete_config_btn)
        # About Button
        about_btn = QPushButton('About')
        about_btn.clicked.connect(self.aboutdialog)
        hbox.addWidget(about_btn)
        self.grid.addLayout(hbox, 0, 0, 1, 3)

    def save_button(self, obj):
        self.button_map[obj.text()] = obj

    def setsubtitle(self, subtitle, enabled):
        if self.xbmc_conn is not None:
            self.xbmc_conn.Player.SetSubtitle(
                playerid=PLAYER_VIDEO, subtitle=subtitle, enabled=enabled)

    def commander(self):
        button_text = self.sender().text()
        if button_text == 'Up':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Up()

        if button_text == 'Down':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Down()

        if button_text == 'Left':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Left()

        if button_text == 'Right':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Right()

        if button_text == 'OK':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Select()

        if button_text == 'Back':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Back()

        if button_text == 'OSD':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.ShowOSD()

        if button_text == 'Subs':
            pass

        if button_text == 'Info':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.Info()

        if button_text == 'Menu':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.ContextMenu()

        if button_text == 'Play/Pause' or button_text == 'Playing' or button_text == 'Paused':
            if self.xbmc_conn is not None:
                current_speed = self.xbmc_conn.Player.GetProperties(
                    playerid=PLAYER_VIDEO, properties=['speed'])
                print(PLAYER_VIDEO)
                if current_speed['result']['speed'] == 0:
                    self.button_map['Play/Pause'].setChecked = True
                    self.button_map['Play/Pause'].setText("Playing")
                else:
                    self.button_map['Play/Pause'].setChecked = False
                    self.button_map['Play/Pause'].setText("Paused")
                self.xbmc_conn.Player.PlayPause([PLAYER_VIDEO])
                print(current_speed)

        if button_text == 'Stop':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Player.Stop([PLAYER_VIDEO])

        if button_text == 'Forward':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.ExecuteAction(action="fastforward")

        if button_text == 'Rewind':
            if self.xbmc_conn is not None:
                self.xbmc_conn.Input.ExecuteAction(action="rewind")

        if button_text == 'Today':
            self.dthread_stop.set()
            self.dthread_stop.clear()
            self.button_map['⇐'].setChecked(False)
            self.button_map['⇒'].setChecked(False)
            self.day_flag = 'today'
            self.matches_list_widget.update()

        if button_text == '⇐':
            self.dthread_stop.set()
            self.dthread_stop.clear()
            self.button_map['Today'].setChecked(False)
            self.button_map['⇒'].setChecked(False)
            self.day_flag = 'tomorrow'
            self.matches_list_widget.update()

        if button_text == '⇒':
            self.dthread_stop.set()
            self.dthread_stop.clear()
            self.button_map['Today'].setChecked(False)
            self.button_map['⇐'].setChecked(False)
            self.day_flag = 'yesterday'
            self.matches_list_widget.update()

    def aboutdialog(self):
        if self.xbmc_conn is not None:
            self.xbmc_conn.GUI.ShowNotification(title="About Kodi Remote",
                                                message="Programmed by YUSUF MOHAMMAD,\n\
        using Python 3.6, xbmc_json PyQt5 modules.")

    def setvolume(self, value):
        if self.xbmc_conn is not None:
            self.xbmc_conn.Application.SetVolume(volume=value)

    def delete_config(self):
        if shutil.os.path.exists('xbmcconf.cfg'):
            shutil.os.remove('xbmcconf.cfg')

    def toggle_matches(self):
        if not self.matches_list_widget.isHidden():
            self.matches_list_widget.setHidden(not self.matches_list_widget.isHidden())
            self.grid.removeWidget(self.matches_list_widget)
            self.match_list_toggle.setText('>')
        else:
            self.grid.addWidget(self.matches_list_widget, 0, 5, 4, 4)
            self.matches_list_widget.setHidden(not self.matches_list_widget.isHidden())
            self.match_list_toggle.setText('<')

    def loadconfig(self):
        try:
            with open('xbmcconf.cfg', 'r') as xbmcconf_obj:
                xbmc_content = xbmcconf_obj.read()

            if xbmc_content != '':
                self.xbmc_conn = XBMC(xbmc_content)
                for text, button in self.button_map.items():
                    button.setDisabled(False)
            else:
                ipdialog = QInputDialog()
                ipdialog.setLabelText('Please enter your KODI IP:')
                ipdialog.setTextValue('http://192.168.0.0:8080/jsonrpc')
                text, ok = ipdialog.getText(self, 'KODI IP',
                                            'Please enter your KODI IP:')
                if ok:
                    with open('xbmcconf.cfg', 'w+') as xbmcconf_obj:
                        xbmcconf_obj.write(str(text))
                    self.xbmc_conn = XBMC(text)
                    for text, button in self.button_map.items():
                        button.setDisabled(False)

        except:
            ipdialog = QInputDialog()
            ipdialog.setLabelText('Please enter your KODI IP:')
            ipdialog.setTextValue('http://192.168.0.0:8080/jsonrpc')
            text, ok = ipdialog.getText(self, 'KODI IP',
                                        'Please enter your KODI IP:', text="http://192.168.0.0:8080/jsonrpc")
            if ok:
                with open('xbmcconf.cfg', 'w+') as xbmcconf_obj:
                    xbmcconf_obj.write(str(text))
                self.xbmc_conn = XBMC(text)
                for text, button in self.button_map.items():
                    button.setDisabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
