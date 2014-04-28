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

import ac
import acsys
from datetime import datetime
import json
import os

# Time since last data update
export_dir = 'exports'
delta = 0.0
laps = []
app_size_x = 400
app_size_y = 200
session = None


def log_error(msg):
    '''
    Print an error in the console
    '''
    ac.console('ERROR(racingline): %s')


class Session(object):
    '''
    Represent a racing sessions, stores laps, etc.
    '''
    def __init__(self):
        self.laps = []
        self.trackname = ''
        self.carname = ''

    def add_lap(self, count):
        self.laps.append(Lap(count))

    @property
    def current_lap(self):
        try:
            return self.laps[-1]
        except IndexError:
            log_error('No current lap!')
            return None

    def dumps(self):
        '''
        Returns a JSON representation of the Session
        '''
        return json.dumps({
            'trackname': self.trackname,
            'carname': self.carname,
            'laps': [lap.dumps() for lap in self.laps],
        })

    def export_data(self):
        '''
        Export the Session data to a file in the plugin's directory
        '''
        current_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = os.path.join(current_dir, export_dir)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        filename = '%s-%s-%s.json' % (datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                   self.trackname, self.carname)
        f = open(os.path.join(target_dir, filename), 'w')
        f.write(self.dumps())
        f.close()
        ac.console('Exported session data to: %s' % os.path.join(target_dir, filename))


class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.speed = 0      # Speed in Km/h
        self.gas = 0
        self.brake = 0
        self.clutch = 0
        self.start = False  # Used to start a new line when rendering
        self.end = False    # Used to end a line when rendering

    def dumps(self):
        '''
        Returns a JSON representation of the Point
        '''
        return json.dumps({
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'speed': self.speed,
            'gas': self.gas,
            'brake': self.brake,
            'clutch': self.clutch,
        })


class Lap(object):
    def __init__(self, count):
        self.count = count
        self.points = []
        self.valid = 1
        self.laptime = 0

    def last(self):
        '''
        Returns the last point from the lap
        '''
        if self.points:
            return self.points[-1]
        else:
            return None

    def normalise(self, current_lap):
        '''
        Return a normalised version of the points based on the widget
        size, zoom level and last position of current lap
        '''
        last = current_lap.last()
        if not last:
            # We don't have any data yet
            return None
        result = []

        # TODO: handle "zoom"

        # Calculate the shift to fit the points within the widget
        if last.x > app_size_x / 2:
            diff_x = -(last.x - app_size_x / 2)
        else:
            diff_x = app_size_x / 2 - last.x
        if last.z > app_size_y / 2:
            diff_z = -(last.z - app_size_y / 2)
        else:
            diff_z = app_size_y / 2 - last.z

        # Shift the points, only keep the one that actually fit
        # in the widget
        out = False  # Whether or not the last point was outside the widget
        for point in self.points:
            x = point.x + diff_x
            y = point.y  # We ignore y for now
            z = point.z + diff_z

            if x > app_size_x or x < 0 or z > app_size_y or z < 0:
                out = True
                if result:
                    result[-1].end = True
                continue

            point = Point(x, y, z)
            if out:
                point.start = True
                out = False

            result.append(point)

        return result

    def render(self, color, current_lap):
        '''
        Renders the lap
        '''
        ac.glColor4f(*color)
        ac.glBegin(acsys.GL.LineStrip)
        for point in self.normalise(current_lap):
            if point.end:
                ac.glEnd()
            if point.start:
                ac.glBegin(acsys.GL.LineStrip)
            ac.glVertex2f(point.x, point.z)
        ac.glEnd()

    def dumps(self):
        '''
        Returns a JSON representation of the Lap
        '''
        return json.dumps({
            'count': self.count,
            'valid': self.valid,
            'laptime': self.laptime,
            'points': [point.dumps() for point in self.points],
        })


def acMain(ac_version):
    global session

    # Create App Widget
    appWindow = ac.newApp('Racing Line')
    ac.setSize(appWindow, app_size_x, app_size_y)
    ac.addRenderCallback(appWindow, onFormRender)

    button = ac.addButton(appWindow, "Export data")
    ac.setPosition(button, 10, 10)
    ac.setSize(button, 500, 10)
    ac.addOnClickedListener(button, export_data_button_callback)

    # Create session object
    session = Session()
    session.trackname = ac.getTrackName(0)
    session.carname = ac.getCarName(0)

    session.add_lap(ac.getCarState(0, acsys.CS.LapCount))

    return "Racing Line"


def acUpdate(deltaT):
    global delta
    global session

    # Update the status of the current lap
    session.current_lap.valid = ac.getCarState(0, acsys.CS.LapInvalidated)

    # We only update the data every .5 seconds to prevent filling up
    # the memory with data points
    delta += deltaT
    if delta < 0.5:
        return
    delta = 0

    # Check if we're in a new lap
    lap_count = ac.getCarState(0, acsys.CS.LapCount)
    if lap_count != session.current_lap.count:
        # Record the previous lap time
        session.current_lap.laptime = ac.getCarState(0, acsys.CS.LastLap)

        # Create a new lap
        session.add_lap(lap_count)

    # Get the current car's position and add it to current lap
    position = ac.getCarState(0, acsys.CS.WorldPosition)
    point = Point(*position)
    point.speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    point.gas = ac.getCarState(0, acsys.CS.Gas)
    point.brake = ac.getCarState(0, acsys.CS.Brake)
    point.clutch = ac.getCarState(0, acsys.CS.Clutch)
    session.current_lap.points.append(point)


def onFormRender(deltaT):
    best_lap = None
    for lap in session.laps:
        # TODO: check we're finding the correct best lap
        if not best_lap or best_lap.laptime > lap.laptime:
            best_lap = lap

    if best_lap and best_lap.laptime:
        color = (1, 0, 0, 1)
        best_lap.render(color, session.current_lap)

    color = (0, 1, 0, 1)
    session.current_lap.render(color, session.current_lap)


def export_data_button_callback(x, y):
    session.export_data()
