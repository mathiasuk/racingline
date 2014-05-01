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

from models import Session, Point
from acpmf import AcSharedMemory

import ac
import acsys
import math

# Share memory stuff
acshm = AcSharedMemory(7)

# Time since last data update
export_dir = 'exports'
delta = 0.0
app_size_x = 400
app_size_y = 200
session = None
current_speed_label = None
best_speed_label = None
save_checkbox = None

# colors:
GREEN = (1, 0, 0, 1)
RED = (0, 1, 0, 1)
WHITE = (0, 1, 0, 1)


def log_error(msg):
    '''
    Print an error in the console
    '''
    ac.console('ERROR(racingline): %s')


def acMain(ac_version):
    global session, current_speed_label, best_speed_label, save_checkbox

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
    current_speed_label = ac.addLabel(appWindow, 'Best speed value')
    ac.setText(current_speed_label, '')
    ac.setPosition(current_speed_label, 60, 30)
    best_speed_label = ac.addLabel(appWindow, 'Best speed value')
    ac.setText(best_speed_label, '')
    ac.setPosition(best_speed_label, 60, 50)

    # Create checkbox
    save_checkbox = ac.addCheckBox(appWindow, 'Export data')
    ac.setSize(save_checkbox, 10, 10)
    ac.setPosition(save_checkbox, 10, 180)
    ac.addOnCheckBoxChanged(save_checkbox, save_checkbox_callback)

    # Create session object
    session = Session(ac, acsys)
    session.app_size_x = app_size_x
    session.app_size_y = app_size_y
    session.trackname = ac.getTrackName(0)
    session.carname = ac.getCarName(0)

    session.new_lap(ac.getCarState(0, acsys.CS.LapCount))

    return "Racing Line"


def acUpdate(deltaT):
    global delta
    global session

    # Update the status of the current lap
    session.current_lap.valid = ac.getCarState(0, acsys.CS.LapInvalidated)

    # We only update the data every .1 seconds to prevent filling up
    # the memory with data points
    delta += deltaT
    if delta < 0.1:
        return
    delta = 0

    # Check if we're in a new lap
    lap_count = ac.getCarState(0, acsys.CS.LapCount)
    if lap_count != session.current_lap.count:
        # Record the previous lap time
        session.current_lap.laptime = ac.getCarState(0, acsys.CS.LastLap)

        # Create a new lap
        session.new_lap(lap_count)

    # Get the current car's position and add it to current lap
    position = ac.getCarState(0, acsys.CS.WorldPosition)
    point = Point(*position)
    point.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    point.gas = ac.getCarState(0, acsys.CS.Gas)
    point.brake = ac.getCarState(0, acsys.CS.Brake)
    point.clutch = ac.getCarState(0, acsys.CS.Clutch)
    session.current_lap.points.append(point)


def onFormRender(deltaT):
    # Get current heading:
    heading = math.pi - acshm.readValue("physics", "heading")

    if session.best_lap:
        session.best_lap.render(GREEN, session.current_lap, heading)

    session.current_lap.render(RED, session.current_lap, heading)

    last_point = session.current_lap.last_point
    current_speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    ac.setText(current_speed_label, "{0}".format(round(current_speed, 1)))

    # Get closest point of best lap:
    if session.best_lap:
        point = session.best_lap.closest_point(last_point)
        ac.setText(best_speed_label, "{0}".format(round(point.speed, 1)))
        if point.speed > current_speed:
            ac.setFontColor(current_speed_label, *RED)
        elif point.speed < current_speed:
            ac.setFontColor(current_speed_label, *GREEN)
        else:
            ac.setFontColor(current_speed_label, *WHITE)


def save_checkbox_callback(name, state):
    global session
    if state:
        session.save_data = True
    else:
        session.save_data = False
    ac.console('** %s' % session.save_data)
