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

# Time since last data update
delta = 0.0
laps = []
app_size_x = 400
app_size_y = 200


class Point(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.start = False  # Used to start a new line when rendering
        self.end = False    # Used to end a line when rendering


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


def acMain(ac_version):
    global laps

    appWindow = ac.newApp('Racing Line')
    ac.setSize(appWindow, app_size_x, app_size_y)

    ac.addRenderCallback(appWindow, onFormRender)

    laps.append(Lap(ac.getCarState(0, acsys.CS.LapCount)))

    return "Racing Line"


def acUpdate(deltaT):
    global delta
    global laps

    # Update the status of the current lap
    current_lap = laps[-1]
    current_lap.valid = ac.getCarState(0, acsys.CS.LapInvalidated)

    # We only update the data every .5 seconds to prevent filling up
    # the memory with data points
    delta += deltaT
    if delta < 0.5:
        return
    delta = 0

    # Check if we're in a new lap
    lap_count = ac.getCarState(0, acsys.CS.LapCount)
    if lap_count != current_lap.count:
        # Record the previous lap time
        current_lap.laptime = ac.getCarState(0, acsys.CS.LastLap)

        # Create a new lap
        current_lap = Lap(lap_count)
        laps.append(current_lap)

#    # We divide each coordinate by 2 to "zoom out"
#    position = [i / 2 for i in position]

    # Get the current car's position and add it to current lap
    position = ac.getCarState(0, acsys.CS.WorldPosition)
    current_lap.points.append(Point(*position))


def onFormRender(deltaT):
    current_lap = None
    best_lap = None
    for lap in laps:
        # TODO: check we're finding the correct best lap
        if not best_lap or best_lap.laptime > lap.laptime:
            best_lap = lap
    current_lap = lap

    if best_lap and best_lap.laptime:
        color = (1, 0, 0, 1)
        best_lap.render(color, current_lap)

    if current_lap:
        color = (0, 1, 0, 1)
        current_lap.render(color, current_lap)
