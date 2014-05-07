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

# Data points frequency in seconds
FREQ = 0.125

app_size_x = 400
app_size_y = 200
session = None


def acMain(ac_version):
    global session

    # Create session object
    session = Session(ac, acsys)
    session.app_size_x = app_size_x
    session.app_size_y = app_size_y
    session.freq = FREQ
    session.trackname = ac.getTrackName(0)
    session.carname = ac.getCarName(0)

    # Load best lap time if it exists for current track and car
    session.load_best_lap()

    # Create App Widget
    appWindow = ac.newApp('Racing Line')
    ac.setSize(appWindow, app_size_x, app_size_y)
    ac.addRenderCallback(appWindow, onFormRender)

#    button = ac.addButton(appWindow, "Export data")
#    ac.setPosition(button, 10, 10)
#    ac.setSize(button, 500, 10)
#    ac.addOnClickedListener(button, export_data_button_callback)

    # Create labels
    label = ac.addLabel(appWindow, 'Current speed')
    ac.setText(label, 'Speed')
    ac.setPosition(label, 10, 30)
    label = ac.addLabel(appWindow, 'Best speed')
    ac.setText(label, 'Best')
    ac.setPosition(label, 10, 50)
    session.current_speed_label = ac.addLabel(appWindow, 'Best speed value')
    ac.setText(session.current_speed_label, '')
    ac.setPosition(session.current_speed_label, 60, 30)
    session.best_speed_label = ac.addLabel(appWindow, 'Best speed value')
    ac.setText(session.best_speed_label, '')
    ac.setPosition(session.best_speed_label, 60, 50)

    # Create checkbox
    session.save_checkbox = ac.addCheckBox(appWindow, 'Export data')
    ac.setSize(session.save_checkbox, 10, 10)
    ac.setPosition(session.save_checkbox, 10, 180)
    ac.addOnCheckBoxChanged(session.save_checkbox, save_checkbox_callback)

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
    session.console('** %s' % session.save_data)
