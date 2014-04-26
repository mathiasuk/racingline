import ac
import acsys

# Time since last data update
delta = 0.0
points = []
app_size = [400, 200]


def acMain(ac_version):
    global points, app_size

    appWindow = ac.newApp('Racing Line')
    ac.setSize(appWindow, app_size[0], app_size[1])
    ac.log("I have created the App")

    ac.addRenderCallback(appWindow, onFormRender)

    return "AC Python Tutorial 04"


def acUpdate(deltaT):
    global points
    global delta

    # We only update the data every .5 seconds to prevent filling up 
    # the memory with data points
    delta += deltaT
    if delta < 0.5:
        return
    delta = 0

    ac.console('%d' % (len(points)))

    position = ac.getCarState(0, acsys.CS.WorldPosition)
    # We divide each coordinate by 2 to "zoom out"
    position = [ i / 2 for i in position ] 
    points.append(position)


def normalise_array(array):
    global app_size
    result = []
    last = array[-1]
    if last[0] > app_size[0]/2:
        diff_x = -(last[0] - app_size[0]/2)
    else: 
        diff_x = app_size[0]/2 - last[0]
    if last[2] > app_size[1]/2:
        diff_z = -(last[2] - app_size[1]/2)
    else: 
        diff_z = app_size[1]/2 - last[2]
    for x, y, z in reversed(array):
        ac.console('%d:%d %d:%d %d:%d' % ( x, z, diff_x, diff_z, last[0], last[2]))
        x += diff_x
        z += diff_z
        ac.console('-** %d:%d - %d' % (x, z, last[0] + app_size[0]/2))
        if x > app_size[0] or x < 0:
            break
        if z > app_size[1] or z < 0:
            break
        ac.console('** %d:%d' % (x, z))
        result.append([x, z])
    return result
        

def onFormRender(deltaT):
    global points

    ac.glColor4f(1,0,0,1)
    ac.glBegin(acsys.GL.LineStrip)
    for x, z in normalise_array(points):
        ac.console('--%d:%d' % ( x, z))
        ac.glVertex2f(x, z)
    ac.glEnd()
