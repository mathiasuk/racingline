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

from datetime import datetime
import json
import math
import os


class Session(object):
    '''
    Represent a racing sessions, stores laps, etc.
    '''
    def __init__(self, ac=None, acsys=None):
        '''
        We pass ac and acsys so we don't have to import them here,
        that way we can test the code without AC modules
        '''
        self.ac = ac
        self.acsys = acsys
        self.current_lap = None
        self.best_lap = None
        self.trackname = ''
        self.carname = ''
        self.app_size_x = 0
        self.app_size_y = 0
        self.save_data = False
        self.start_time = datetime.now()

    def _get_export_filepath(self):
        '''
        Return the data filename for the current session
        '''

    def new_lap(self, count):
        # Check if current_lap is faster than previous best
        if self.current_lap:
            if not self.best_lap or \
               self.best_lap.laptime > self.current_lap.laptime:
                self.best_lap = self.current_lap

        # Save the current lap to file if necessary
        if self.save_data:
            self.export_data()

        # Create new lap
        self.current_lap = Lap(self, count)

    def json_dumps(self):
        '''
        Returns a JSON representation of the Session
        '''
        return json.dumps({
            'trackname': self.trackname,
            'carname': self.carname,
        })

    def export_data(self):
        '''
        Export the Session data to a file in the plugin's directory
        Returns the path to the file
        '''
        current_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = os.path.join(current_dir, 'exports')

        # Create the export directory if it doesn't already exists
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        filename = '%s-%s-%s.json' % (datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                                      self.trackname, self.carname)

        f = open(os.path.join(target_dir, filename), 'a')

        # Check the position in the file, if we're at 0 then the file
        # is new and write the session headers
        if f.tell() == 0:
            f.write(self.json_dumps() + '\n')

        # Write the current lap to file
        f.write(self.current_lap.json_dumps() + '\n')
        f.close()

        self.ac.console('Saved lap %d to file %s.' % (self.current_lap.count,
                                                      filename))

        return os.path.join(target_dir, filename)


class Point(object):
    def __init__(self, x, y, z, speed=0, gas=0, brake=0, clutch=0):
        self.x = x
        self.y = y
        self.z = z
        self.speed = speed      # Speed in Km/h
        self.gas = gas
        self.brake = brake
        self.clutch = clutch
        self.start = False  # Used to start a new line when rendering
        self.end = False    # Used to end a line when rendering

    def equal_coords(self, point):
        '''
        Return trues if the given point has the same x, y and z coordinates
        '''
        return self.x == point.x and self.y == point.y and self.z == point.z

    def dumps(self):
        '''
        Returns a dict representation of the Point that can be passed to JSON
        '''
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'speed': self.speed,
            'gas': self.gas,
            'brake': self.brake,
            'clutch': self.clutch,
        }


class Lap(object):
    def __init__(self, session, count):
        self.session = session  # Reference to the current session
        self.count = count
        self.points = []
        self.valid = 1
        self.laptime = 0

    @property
    def last_point(self):
        '''
        Returns the last point from the lap
        '''
        if self.points:
            return self.points[-1]
        else:
            return None

    def normalise(self, current_lap, heading):
        '''
        Return a normalised version of the points based on the widget
        size, zoom level and last position of current lap
        '''
        last_point = current_lap.last_point
        if not last_point:
            # We don't have any data yet
            return None
        result = []

        # TODO: handle "zoom"

        # Calculate the shift to fit the points within the widget
        if last_point.x > self.session.app_size_x / 2:
            diff_x = -(last_point.x - self.session.app_size_x / 2)
        else:
            diff_x = self.session.app_size_x / 2 - last_point.x
        if last_point.z > self.session.app_size_y / 2:
            diff_z = -(last_point.z - self.session.app_size_y / 2)
        else:
            diff_z = self.session.app_size_y / 2 - last_point.z

        # Shift the points, only keep the one that actually fit
        # in the widget
        out = False  # Whether or not the last point was outside the widget
        for point in self.points:
            # Rotate the point by 'heading' rad around the center (last point)
            x = math.cos(heading) * (point.x - last_point.x) - math.sin(heading) * (point.z - last_point.z) + last_point.x
            z = math.sin(heading) * (point.x - last_point.x) + math.cos(heading) * (point.z - last_point.z) + last_point.z

            x = x + diff_x
            y = point.y  # We ignore y for now
            z = z + diff_z

            if x > self.session.app_size_x or x < 0 or \
               z > self.session.app_size_y or z < 0:
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

    def render(self, color, current_lap, heading):
        '''
        Renders the lap
        '''
        self.session.ac.glColor4f(*color)
        self.session.ac.glBegin(self.session.acsys.GL.LineStrip)
        for point in self.normalise(current_lap, heading):
            if point.end:
                self.session.ac.glEnd()
            if point.start:
                self.session.ac.glBegin(self.session.acsys.GL.LineStrip)
            self.session.ac.glVertex2f(point.x, point.z)
        self.session.ac.glEnd()

    def json_dumps(self):
        '''
        Returns a JSON representation of the Lap
        '''
        return json.dumps({
            'count': self.count,
            'valid': self.valid,
            'laptime': self.laptime,
            'points': [point.dumps() for point in self.points],
        })

    def closest_point(self, ref_point):
        '''
        Returns the point from the lap closest to the given point
        '''
        distance = None
        closest = None
        for point in self.points:
            d = (point.x - ref_point.x) ** 2 + \
                (point.y - ref_point.y) ** 2 + \
                (point.z - ref_point.z) ** 2
            d = abs(d)

            if distance is None or d < distance:
                distance = d
                closest = point

        return closest
