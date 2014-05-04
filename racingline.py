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

from models import Session, Point, colors
from acpmf import AcSharedMemory

import ac
import acsys
import math

# Share memory stuff
acshm = AcSharedMemory(7)

# Data points frequency in seconds
FREQ = 0.125

delta = 0.0  # Time since last data update
app_size_x = 400
app_size_y = 200
session = None
current_speed_label = None
best_speed_label = None
save_checkbox = None


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

    # Check if we're in a new lap
    lap_count = ac.getCarState(0, acsys.CS.LapCount)
    if lap_count != session.current_lap.count:
        # Create a new lap
        session.new_lap(lap_count)

    # Update the status of the current lap
    session.current_lap.valid = ac.getCarState(0, acsys.CS.LapInvalidated)
    session.current_lap.laptime = ac.getCarState(0, acsys.CS.LapTime)

    # Save some current data for rendering
    session.current_data['current_speed'] = ac.getCarState(0, acsys.CS.SpeedKMH)
    session.current_data['tyre_radius'] = ac.getCarState(0, acsys.CS.TyreRadius)
    session.current_data['wheel_angular_speed'] = ac.getCarState(0, acsys.CS.WheelAngularSpeed)
    # wheelSlip is currently unused, left here for reference
    # acshm.readValue("physics", "wheelSlip")
    # session.current_data['wheels_slip'] = [ acshm.shm["physics"].memStruct["wheelSlip"]["val"]

    # We only update the rest of the data every FREQ seconds to
    # prevent filling up the memory with data points
    delta += deltaT
    if delta < FREQ:
        return
    delta = 0

    # Get the current car's position and add it to current lap
    position = ac.getCarState(0, acsys.CS.WorldPosition)
    point = Point(*position)
    point.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    point.gas = ac.getCarState(0, acsys.CS.Gas)
    point.brake = ac.getCarState(0, acsys.CS.Brake)
    point.clutch = ac.getCarState(0, acsys.CS.Clutch)

    # If we have a best lap get the speed at the closest point
    if session.best_lap:
        closest_point = session.best_lap.closest_point(point)
        if closest_point:
            point.best_speed = closest_point.speed

    session.current_lap.points.append(point)


def onFormRender(deltaT):
    global session

    # Get current heading:
    acshm.readValue("physics", "heading")
    heading = math.pi - acshm.shm["physics"].memStruct["heading"]["val"]

    if session.best_lap:
        session.best_lap.render(session.current_lap, heading, colors['GREY_60'])

    session.current_lap.render(session.current_lap, heading)

    last_point = session.current_lap.last_point
    if not last_point:
        return
    current_speed = session.current_data['current_speed']
    ac.setText(current_speed_label, "{0}".format(round(current_speed, 1)))

    # Print the speed of the closest point of the best lap if any
    if last_point.best_speed is not None:
        ac.setText(best_speed_label, "{0}".format(round(last_point.best_speed, 1)))
        if last_point.best_speed > current_speed + 1:  # +1 is to avoid flickering
            ac.setFontColor(current_speed_label, *colors['RED'])
        elif last_point.best_speed < current_speed - 1:
            ac.setFontColor(current_speed_label, *colors['GREEN'])
        else:
            ac.setFontColor(current_speed_label, *colors['WHITE'])

    session.render_tyres_slip()


def save_checkbox_callback(name, state):
    global session
    if state:
        session.save_data = True
    else:
        session.save_data = False
    session.console('** %s' % session.save_data)
