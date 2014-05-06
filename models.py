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

from acpmf import AcSharedMemory

from datetime import datetime
import json
import math
import os
import sys

# colors:
RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)
WHITE = (0, 1, 0, 1)
GREY_30 = (0.3, 0.3, 0.3, 1)
GREY_60 = (0.6, 0.6, 0.6, 1)


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
        self.current_data = {}
        self.delta = 0.0  # Time since last data update
        self.freq = 0.5
        self.laps = []  # This is only used when running outside of AC

        # Labels
        self.current_speed_label = None
        self.best_speed_label = None
        self.save_checkbox = None

    def console(self, msg):
        '''
        Prints to AC console if available or to terminal if in test mode
        '''
        if self.ac:
            self.ac.console(msg)
        else:
            sys.stdout.write('%s\n' % msg)

    def new_lap(self, count):
        '''
        Create a new lap, save best lap if previous lap was faster
        than current best
        '''
        # Check if current_lap is faster than previous best
        if self.current_lap:
            if not self.best_lap or \
               self.current_lap.laptime > 0 and self.current_lap.laptime < self.best_lap.laptime:
                self.best_lap = self.current_lap

        # Save the current lap to file if necessary
        if self.save_data:
            self.export_data()

        # Create new lap
        self.current_lap = Lap(self, count)

    def _get_wheels_lock(self):
        wheel_angular_speed = self.current_data['wheel_angular_speed']
        tyre_radius = self.current_data['tyre_radius']
        current_speed = self.current_data['current_speed']

        # Calculate the wheel speed:
        # Angular_speed (radians) * radius = m/s converted to km/h
        wheel_speed = []
        for speed, radius in zip(wheel_angular_speed, tyre_radius):
            wheel_speed.append(speed * radius * 3600 / 1000)

        # Calculate the locking ratio
        if current_speed > 1:
            lock_ratios = [1 - w / current_speed for w in wheel_speed]
        else:
            # The car is stopped, we ignore wheel lock
            lock_ratios = [0 for w in wheel_speed]

        return lock_ratios

    def update_data(self, deltaT):
        '''
        Called by acUpdate, updates internal data
        '''
        # Cself if we're in a new lap
        lap_count = self.ac.getCarState(0, self.acsys.CS.LapCount)
        if lap_count != self.current_lap.count:
            # Create a new lap
            self.new_lap(lap_count)

        # Update the status of the current lap
        self.current_lap.invalid = self.ac.getCarState(0, self.acsys.CS.LapInvalidated)
        self.current_lap.laptime = self.ac.getCarState(0, self.acsys.CS.LapTime)

        # Save some current data for rendering
        self.current_data['current_speed'] = self.ac.getCarState(0, self.acsys.CS.SpeedKMH)
        self.current_data['tyre_radius'] = self.ac.getCarState(0, self.acsys.CS.TyreRadius)
        self.current_data['wheel_angular_speed'] = self.ac.getCarState(0, self.acsys.CS.WheelAngularSpeed)

        acshm = AcSharedMemory(7)
        acshm.readValue("physics", "heading")
        self.current_data['heading'] = math.pi - acshm.shm["physics"].memStruct["heading"]["val"]
        # wheelSlip is currently unused, left here for reference
        # acshm.readValue("physics", "wheelSlip")
        # self.current_data['wheels_slip'] = [ acshm.shm["physics"].memStruct["wheelSlip"]["val"]

        # We only update the rest of the data every FREQ seconds to
        # prevent filling up the memory with data points
        self.delta += deltaT
        if self.delta < self.freq:
            return
        self.delta = 0

        # Get the current car's position and add it to current lap
        position = self.ac.getCarState(0, self.acsys.CS.WorldPosition)
        point = Point(*position)
        point.speed = self.ac.getCarState(0, self.acsys.CS.SpeedKMH)
        point.gas = self.ac.getCarState(0, self.acsys.CS.Gas)
        point.brake = self.ac.getCarState(0, self.acsys.CS.Brake)
        point.clutch = self.ac.getCarState(0, self.acsys.CS.Clutch)
        point.gear = self.ac.getCarState(0, self.acsys.CS.Gear)

        # If we have a best lap get the speed at the closest point
        if self.best_lap:
            closest_point = self.best_lap.closest_point(point)
            if closest_point:
                point.best_speed = closest_point.speed

        self.current_lap.points.append(point)

    def render_tyres_slip(self):
        '''
        Render the tyres slip widget
        '''
        # Get the tyres slip ratio
        lock_ratios = self._get_wheels_lock()

        self.ac.glColor4f(*get_color_from_ratio(lock_ratios[0], fade_in=True))
        self.ac.glQuad(380, 30, 5, 10)
        self.ac.glColor4f(*get_color_from_ratio(lock_ratios[1], fade_in=True))
        self.ac.glQuad(390, 30, 5, 10)
        self.ac.glColor4f(*get_color_from_ratio(lock_ratios[2], fade_in=True))
        self.ac.glQuad(380, 50, 5, 10)
        self.ac.glColor4f(*get_color_from_ratio(lock_ratios[3], fade_in=True))
        self.ac.glQuad(390, 50, 5, 10)

    def render(self):
        '''
        Renders the widget
        '''
        heading = self.current_data['heading']

        if self.best_lap:
            self.best_lap.render(self.current_lap, heading, GREY_60)

        self.current_lap.render(self.current_lap, heading)

        last_point = self.current_lap.last_point
        if not last_point:
            return
        current_speed = self.current_data['current_speed']
        self.ac.setText(self.current_speed_label, "{0}".format(round(current_speed, 1)))

        # Print the speed of the closest point of the best lap if any
        if last_point.best_speed is not None:
            self.ac.setText(self.best_speed_label, "{0}".format(round(last_point.best_speed, 1)))
            if last_point.best_speed > current_speed + 1:  # +1 is to avoid flickering
                self.ac.setFontColor(self.current_speed_label, *RED)
            elif last_point.best_speed < current_speed - 1:
                self.ac.setFontColor(self.current_speed_label, *GREEN)
            else:
                self.ac.setFontColor(self.current_speed_label, *WHITE)

        self.render_tyres_slip()

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

        filename = '%s-%s-%s.json' % (self.start_time.strftime('%Y-%m-%d-%H-%M-%S'),
                                      self.trackname, self.carname)

        f = open(os.path.join(target_dir, filename), 'a')

        # Check the position in the file, if we're at 0 then the file
        # is new and write the session headers
        if f.tell() == 0:
            f.write(self.json_dumps() + '\n')

        # Write the current lap to file
        f.write(self.current_lap.json_dumps() + '\n')
        f.close()

        self.console('Saved lap %d to file %s.' % (self.current_lap.count,
                                                   filename))

        return os.path.join(target_dir, filename)

    def import_data(self, filename):
        '''
        Import a session from file. This is not meant to be called in AC
        '''
        try:
            f = open(filename)
        except Exception as e:
            self.console('Can\'t open file "%s": %s' % (filename, e))

        # Read session_data
        data = f.readline()
        data = json.loads(data)
        for key, value in data.items():
            setattr(self, key, value)

        # Read laps data
        for i, line in enumerate(f):
            lap = Lap(self, i)
            data = json.loads(line)
            lap.json_loads(data)
            self.laps.append(lap)


class Point(object):
    def __init__(self, x, y, z, s=0, g=0, b=0, c=0, r=0):
        self.x = x
        self.y = y
        self.z = z
        self.speed = s      # Speed in Km/h
        self.gas = g
        self.brake = b
        self.clutch = c
        self.gear = r
        self.best_speed = None  # Speed at the closet point
                                # of the best lap if any
        self.start = False  # Used to start a new line when rendering
        self.end = False    # Used to end a line when rendering

    def __repr__(self):
        return 'x: %f, z: %f' % (self.x, self.z)

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
            'x': round(self.x, 2),
            'y': round(self.y, 2),
            'z': round(self.z, 2),
            's': round(self.speed, 2),
            'g': self.gas,
            'b': self.brake,
            'c': self.clutch,
            'r': self.gear,
        }


class Lap(object):
    def __init__(self, session, count):
        self.session = session  # Reference to the current session
        self.count = count
        self.points = []
        self.invalid = 0
        self.laptime = 0

    def human_laptime(self):
        '''
        Returns the laptime under the format: m:s.ms
        '''
        s, ms = divmod(self.laptime, 1000)
        m, s = divmod(s, 60)
        return '%d:%d:%d' % (m, s, ms)

    def __repr__(self):
        return '%d: %s%s' % (self.count, self.human_laptime(),
                             '*' if self.invalid else '')

    @property
    def last_point(self):
        '''
        Returns the last point from the lap
        '''
        try:
            return self.points[-1]
        except IndexError:
            # This can happen before the first lap is recorded, but also happens
            # "randomly" at given points on the track...
            # so we check if we actually have points.
            # Note that this is a dirty hack and it SHOULDN'T work!
            if self.points:
                return self.points[-1]
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

            p = Point(x, y, z)
            p.speed = point.speed
            p.best_speed = point.best_speed
            if out:
                p.start = True
                out = False

            result.append(p)

        return result

    def render(self, current_lap, heading, color=None):
        '''
        Renders the lap, if no color is given we use green for fast sectors
        and red for slow sectors, and all green if no best_speed is available
        '''
        self.session.ac.glBegin(self.session.acsys.GL.LineStrip)

        for point in self.normalise(current_lap, heading):
            if point.start:
                self.session.ac.glBegin(self.session.acsys.GL.LineStrip)

            self.session.ac.glVertex2f(point.x, point.z)

            if color:
                self.session.ac.glColor4f(*color)
            elif point.best_speed is not None:
                if point.speed < point.best_speed:
                    self.session.ac.glColor4f(*RED)
                else:
                    self.session.ac.glColor4f(*GREEN)
            else:
                self.session.ac.glColor4f(*GREEN)

            if point.end:
                self.session.ac.glEnd()

        self.session.ac.glEnd()

    def json_dumps(self):
        '''
        Returns a JSON representation of the Lap
        '''
        return json.dumps({
            'count': self.count,
            'invalid': self.invalid,
            'laptime': self.laptime,
            'points': [point.dumps() for point in self.points],
        })

    def json_loads(self, data):
        '''
        Update the lap with the given JSON data
        '''
        self.invalid = data['invalid']
        self.laptime = data['laptime']
        for point_data in data['points']:
            point = Point(**point_data)
            self.points.append(point)

    def svg_path(self):
        '''
        Returns a SVG path version of the current lap points
        '''
        path = 'M %f,%f' % (self.points[0].x, self.points[0].z)

        for point in self.points:
            path += ' L %f,%f' % (point.x, point.z)

        return path

    def write_svg(self, filename):
        '''
        Write a SVG path of the current lap to filename
        '''
        data = '''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 140" class="racing-line">
    <title>%s</title>

    <path d="%s"
            stroke="#000000"
            fill="none"
            class="racing-line-lap" />
</svg>
''' % (self.human_laptime(), self.svg_path())

        try:
            f = open(filename, 'w')
        except Exception as e:
            self.console('Can\'t open file "%s": %s' % (filename, e))

        f.write(data)
        f.close()

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


def get_color_from_ratio(ratio, fade_in=False, mode='yr'):
    '''
    Return a color based on ratio
    Ratios greater than 1 are considered as 1
    If fade_in then ratio also affects alpha channel from 0 to 1
    Modes:
        yr: yellow to red
        gr: green to red
    '''
    if ratio > 1:
        ratio = 1
    if fade_in:
        alpha = ratio
    else:
        alpha = 1

    if mode == 'gr':
        if ratio <= 0.5:
            return (ratio * 2, 1, 0, alpha)
        else:
            return (1, 1 - (ratio - 0.5) * 2, 0, alpha)

    # Default to mode 'yr'
    return (1, 1 - ratio, 0, alpha)
