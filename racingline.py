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


class Lap(object):
    def __init__(self, count):
        self.count = count
        self.points = []
        self.valid = 1
        self.laptime = 0

    def _last(self):
        if self.points:
            return self.points[-1]
        else:
            return None

    def normalise(self):
        '''
        Return a normalised version of the points based on the widget
        size and zoom level
        '''
        last = self._last()
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
        for point in self.points:
            # ac.console('%d:%d %d:%d %d:%d' % (x, z, diff_x, diff_z, last[0], last[2]))
            x = point.x + diff_x
            y = point.y  # We ignore y for now
            z = point.z + diff_z
            # ac.console('-** %d:%d - %d' % (x, z, last[0] + app_size_x / 2))
            if x > app_size_x or x < 0:
                break
            if z > app_size_y or z < 0:
                break
            ac.console('** %d:%d' % (x, z))
            result.append(Point(x, y, z))


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
    current_lap.points.append(position)


def onFormRender(deltaT):
    for i, lap in enumerate(laps):
        if i == len(lap) - 1:
            ac.glColor4f(0, 1, 0, 1)
        else:
            ac.glColor4f(1, 0, 0, 1)
        ac.glBegin(acsys.GL.LineStrip)
        for point in lap.normalise():
            ac.glVertex2f(point.x, point.z)
        ac.glEnd()
