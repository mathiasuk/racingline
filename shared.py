# From:
# http://www.assettocorsa.net/forum/index.php?threads/reading-shared-memory-with-python.3774/

# read Assetto Corsa shared memory with Python
# acs.exe must be running
# OMG WAT R THOSE WEIRD \Xfo0 THINGS EVERYWHERE??
#	Some values, strings especially are null (\x00) terminated, anything past the first \x00 is rubbish.
#	You will need to concatenate strings at the first null char, with regex or otherwise. See http://docs.python.org/3/library/re.html

import struct						# for converting from bytes to useful data
import mmap							# for reading shared memory
from collections import namedtuple	# *optional*: converting with struct returns a tuple, this adds keys to make it behave like a dict

# data structures
AcPhysics = namedtuple("AcPhysics", 'packetId gas brake fuel gear rpms steerAngle speedKmh velocityX velocityY velocityZ accGx accGy accGz wheelslipW wheelslipX wheelslipY wheelslipZ \
	wheelLoadW wheelLoadX wheelLoadY wheelLoadZ wheelsPressureW wheelsPressureX wheelsPressureY wheelsPressureZ wheelAngularSpeedW wheelAngularSpeedX wheelAngularSpeedY wheelAngularSpeedZ tyreWearW tyreWearX tyreWearY tyreWearZ tyreDirtyLevelW tyreDirtyLevelX tyreDirtyLevelY tyreDirtyLevelZ tyreCoreTemperatureW tyreCoreTemperatureX tyreCoreTemperatureY tyreCoreTemperatureZ \
	camberRADw camberRADx camberRADy camberRADz suspensionTravelW suspensionTravelX suspensionTravelY suspensionTravelZ drs tc heading pitch roll cgHeight carDamageA carDamageB carDamageC carDamageD carDamageE numberOfTyresOut pitLimiterOn abs')

AcGraphics = namedtuple("AcGraphics", 'packetId status session currentTime lastTime bestTime split completedLaps position iCurrentTime iLastTime ibestTime \
	sessionTimeLeft distanceTraveled isInPit currentSectorIndex lastSectorTime numberOfLaps tyreCompound replayTimeMultiplier normalizedCarPosition \
	carCoordinatesX carCoordinatesY carCoordinatesZ')
	
AcStatic = namedtuple("AcStatic", 'smVersion acVersion numberOfSessions numCars carModel track playerName playerSurname playerNick sectorCount maxTorque \
	maxPower maxRpm maxFuel suspensionMaxTravelW suspensionMaxTravelX suspensionMaxTravelY suspensionMaxTravelZ tyreRadiusW tyreRadiusX tyreRadiusY tyreRadiusZ')

# read shared memory, mmap handles are like file pointers and should be close()d
# see Python docs for unpack format
shmHandle = mmap.mmap(0, 256, "acpmf_physics")
data = shmHandle.read(256)
shmHandle.close()
physics = AcPhysics._asdict(AcPhysics._make(struct.unpack("<LfffLLfffffffffffffffffffffffffffffffffffffffffffffffffffffffLLf", data)))

shmHandle = mmap.mmap(0, 148, "acpmf_graphics")
data = shmHandle.read(148)
shmHandle.close()
graphics = AcGraphics._asdict(AcGraphics._make(struct.unpack("<LLL10s10s10s10sLLLLLffLLLL32sfffff", data)))

shmHandle = mmap.mmap(0, 240, "acpmf_static")
data = shmHandle.read(240)
shmHandle.close()
static = AcStatic._asdict(AcStatic._make(struct.unpack("10s10sLL32s32s32s32s32sLffLfffffffff", data)))
