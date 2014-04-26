import ac
import acsys

label1 = 0


def acMain(ac_version):
    global label1

    appWindow = ac.newApp('Racing Line')
    ac.setSize(appWindow, 300, 200)
    label1 = ac.addLabel(appWindow, "Hellow world in a label!")
    ac.setPosition(label1, 10, 50)
    ac.log("I have created the App")

    return "AC Python Tutorial 04"


def acUpdate(deltaT):
    global label1

    position = ac.getCarState(0, acsys.CS.WorldPosition)

    ac.setText(label1, 'Position: %d %d %d' % position)
