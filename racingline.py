# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2014 - Mathias Andre

from models import Session

import ac
import acsys

import os

# Data points frequency in seconds
FREQ = 0.125

app_size_x = 400
app_size_y = 200
session = None


class UI(object):
    '''
    Object that deals with everything related to the app's widget
    '''
    def __init__(self, session):
        self.session = session
        self.widget = None
        self.labels = {}
        self.chkboxes = {}
        self.buttons = {}

        self._create_widget()
        self._create_labels()

        self._create_checkbox('export_data', 'Export Data', 10, 180,
                              10, 10, save_checkbox_callback)

        self._create_button('zoomout', 370, 185, 10, 10, zoomout_callback,
                            texture='zoomout.png')
        self._create_button('zoomin', 385, 185, 10, 10, zoomin_callback,
                            texture='zoomin.png')

    def _create_widget(self):
        self.widget = ac.newApp('Racing Line')
        ac.setSize(self.widget, app_size_x, app_size_y)
        ac.addRenderCallback(self.widget, onFormRender)

    def _create_label(self, name, text, x, y):
        label = ac.addLabel(self.widget, name)
        ac.setText(label, text)
        ac.setPosition(label, x, y)
        self.labels[name] = label

    def _create_checkbox(self, name, text, x, y, size_x, size_y, callback):
        checkbox = ac.addCheckBox(self.widget, text)
        ac.setPosition(checkbox, x, y)
        ac.setSize(checkbox, size_x, size_y)
        ac.addOnCheckBoxChanged(checkbox, callback)
        self.chkboxes[name] = checkbox

    def _create_button(self, name, x, y, size_x, size_y, callback,
                       border=0, opacity=0, texture=None):
        button = ac.addButton(self.widget, '')
        ac.setPosition(button, x, y)
        ac.setSize(button, size_x, size_y)
        ac.addOnClickedListener(button, callback)
        ac.drawBorder(button, border)
        ac.setBackgroundOpacity(button, opacity)
        if texture:
            texture = os.path.join(session.app_path, 'img', texture)
            ac.setBackgroundTexture(button, texture)
        self.buttons[name] = button

    def _create_labels(self):
        self._create_label('current_speed', 'Speed', 10, 30)
        self._create_label('best_speed', 'Best', 10, 50)
        self._create_label('current_speed_val', '', 60, 30)
        self._create_label('best_speed_val', '', 60, 50)


def acMain(ac_version):
    global session

    # Create session object
    session = Session(ac, acsys)
    session.app_size_x = app_size_x
    session.app_size_y = app_size_y
    session.freq = FREQ
    session.trackname = ac.getTrackName(0)
    session.carname = ac.getCarName(0)

    # Initialise UI:
    ui = UI(session)
    session.ui = ui

    # Load best lap time if it exists for current track and car
    session.load_best_lap()

    # Create first lap
    session.new_lap(ac.getCarState(0, acsys.CS.LapCount))

    return "Racing Line"


def acUpdate(deltaT):
    global session

    session.update_data(deltaT)


def onFormRender(deltaT):
    global session

    session.render()


def save_checkbox_callback(name, state):
    global session
    if state:
        session.save_data = True
    else:
        session.save_data = False


def zoomin_callback(x, y):
    global session
    session.zoom_in()


def zoomout_callback(x, y):
    global session
    session.zoom_out()
