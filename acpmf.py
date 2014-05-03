# v0.11
# Changes from v0.1:
# NEW: readValues()
#	reads a set of values

import struct
import mmap

# Global params for creating the base object.
AC_PHYSICS = 1
AC_GRAPHICS = 2
AC_STATIC = 4

# Globals from shared mem docs.
AC_OFF = 0
AC_REPLAY = 1
AC_LIVE = 2
AC_PAUSE = 3

AC_UNKNOWN = -1
AC_PRACTICE = 0
AC_QUALIFY = 1
AC_RACE = 2
AC_HOTLAP = 3
AC_TIME_ATTACK = 4
AC_DRIFT = 5
AC_DRAG = 6

# Physics struct.
class AcPhysics(object):
	memStruct = {"packetId": 				{"offset": 0, "size": 4, "type": "L", "val": 0},
				"gas": 						{"offset": 4, "size": 4, "type": "f", "val": 0},
				"brake": 					{"offset": 8, "size": 4, "type": "f", "val": 0},
				"fuel": 					{"offset": 12, "size": 4, "type": "f", "val": 0},
				"gear": 					{"offset": 16, "size": 4, "type": "L", "val": 0},
				"rpms": 					{"offset": 20, "size": 4, "type": "L", "val": 0},
				"steerAngle": 				{"offset": 24, "size": 4, "type": "f", "val": 0},
				"speedKmh": 				{"offset": 28, "size": 4, "type": "f", "val": 0},
				"velocity":					{"offset": 32, "size": 4, "type": "f", "num": 3, "val":	{"x": 0, 
																									"y": 0, 
																									"z": 0}},
				"accG":						{"offset": 44, "size": 4, "type": "f", "num": 3, "val":	{"x": 0, 
																									"y": 0, 
																									"z": 0}},
				"wheelSlip":				{"offset": 56, "size": 4, "type": "f", "num": 4, "val": {"w": 0, 
																									"x": 0, 
																									"y": 0, 
																									"z": 0}},
				"wheelLoad":				{"offset": 72, "size": 4, "type": "f", "num": 4, "val": {"w": 0, 
																									"x": 0, 
																									"y": 0, 
																									"z": 0}},
				"wheelsPressure":			{"offset": 88, "size": 4, "type": "f", "num": 4, "val": {"w": 0, 
																									"x": 0, 
																									"y": 0, 
																									"z": 0}},
				"wheelAngularSpeed":		{"offset": 108, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																										"x": 0, 
																										"y": 0, 
																										"z": 0}},
				"tyreWear":				{"offset": 120, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																										"x": 0, 
																										"y": 0, 
																										"z": 0}},
				"tyreDirtyLevel":			{"offset": 136, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																										"x": 0, 
																										"y": 0, 
																										"z": 0}},
				"tyreCoreTemperature":		{"offset": 152, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																										"x": 0, 
																										"y": 0, 
																										"z": 0}},
				"camberRad":				{"offset": 168, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																										"x": 0, 
																										"y": 0, 
																										"z": 0}},
				"suspensionTravel":			{"offset": 184, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																										"x": 0, 
																										"y": 0, 
																										"z": 0}},
				"drs": 						{"offset": 200, "size": 4, "type": "f", "val": 0},
				"tc": 						{"offset": 204, "size": 4, "type": "f", "val": 0},
				"heading": 					{"offset": 208, "size": 4, "type": "f", "val": 0},
				"pitch": 					{"offset": 212, "size": 4, "type": "f", "val": 0},
				"roll": 					{"offset": 216, "size": 4, "type": "f", "val": 0},
				"cgHeight": 				{"offset": 220, "size": 4, "type": "f", "val": 0},
				"carDamage":			{"offset": 224, "size": 4, "type": "f", "num": 5, "val":	{"left": 0, 
																									"front": 0, 
																									"chassis": 0,
																									"rear": 0,
																									"right": 0}},
				"numberOfTyresOut": 		{"offset": 244, "size": 4, "type": "L", "val": 0},
				"pitLimiterOn": 			{"offset": 248, "size": 4, "type": "L", "val": 0},
				"abs": 						{"offset": 252, "size": 4, "type": "f", "val": 0}
				}
	size = 256
	
	# Open memory handle.
	def __init__(self):
		self.handle = mmap.mmap(0, self.size, "acpmf_physics")
	
	# Close memory handle automagically when all is done.
	def __del__(self):
		self.handle.close()
		
		
class AcGraphics(object):
	memStruct = {"packetId": 				{"offset": 0, "size": 4, "type": "L", "val": 0},
				"status": 					{"offset": 4, "size": 4, "type": "L", "val": 0},
				"session": 					{"offset": 8, "size": 4, "type": "L", "val": 0},
				"currentTime": 				{"offset": 12, "size": 10, "type": "10s", "val": ""},
				"lastTime": 				{"offset": 22, "size": 10, "type": "10s", "val": ""},
				"bestTime": 				{"offset": 32, "size": 10, "type": "10s", "val": ""},
				"split": 					{"offset": 42, "size": 10, "type": "10s", "val": ""},
				"completedLaps": 			{"offset": 52, "size": 4, "type": "L", "val": 0},
				"position": 				{"offset": 56, "size": 4, "type": "L", "val": 0},
				"iCurrentTime": 			{"offset": 60, "size": 4, "type": "L", "val": 0},
				"iLastTime": 				{"offset": 64, "size": 4, "type": "L", "val": 0},
				"iBestTime": 				{"offset": 68, "size": 4, "type": "L", "val": 0},
				"sessionTimeLeft": 			{"offset": 72, "size": 4, "type": "f", "val": 0},
				"distanceTraveled": 		{"offset": 76, "size": 4, "type": "f", "val": 0},
				"isInPit": 					{"offset": 80, "size": 4, "type": "L", "val": 0},
				"currentSectorIndex": 		{"offset": 84, "size": 4, "type": "L", "val": 0},
				"lastSectorTime": 			{"offset": 88, "size": 4, "type": "L", "val": 0},
				"numberOfLaps": 			{"offset": 92, "size": 4, "type": "L", "val": 0},
				"tyreCompound": 			{"offset": 96, "size": 32, "type": "32s", "val": ""},
				"replayTimeMultiplier": 	{"offset": 128, "size": 4, "type": "f", "val": 0},
				"normalizedCarPosition":	{"offset": 132, "size": 4, "type": "f", "val": 0},
				"carCoordinates":			{"offset": 136, "size": 4, "type": "f", "num": 3, "val":	{"x": 0, 
																										"y": 0, 
																										"z": 0}}
				}
	size = 148
	
	def __init__(self):
		self.handle = mmap.mmap(0, self.size, "acpmf_graphics")
		
	def __del__(self):
		self.handle.close()
		

class AcStatic(object):
	memStruct = {"smVersion": 			{"offset": 0, "size": 10, "type": "10s", "val": ""},
				"acVersion": 			{"offset": 10, "size": 10, "type": "10s", "val": ""},
				"numberOfSessions": 	{"offset": 20, "size": 4, "type": "L", "val": 0},
				"numCars": 				{"offset": 24, "size": 4, "type": "L", "val": 0},
				"carModel": 			{"offset": 28, "size": 32, "type": "32s", "val": ""},
				"track": 				{"offset": 60, "size": 32, "type": "32s", "val": ""},
				"playerName": 			{"offset": 92, "size": 32, "type": "32s", "val": ""},
				"playerSurname": 		{"offset": 124, "size": 32, "type": "32s", "val": ""},
				"playerNick": 			{"offset": 156, "size": 32, "type": "32s", "val": ""},
				"sectorCount": 			{"offset": 188, "size": 4, "type": "L", "val": 0},
				"maxTorque": 			{"offset": 192, "size": 4, "type": "f", "val": 0},
				"maxPower": 			{"offset": 196, "size": 4, "type": "f", "val": 0},
				"maxRpm": 				{"offset": 200, "size": 4, "type": "L", "val": 0},
				"maxFuel": 				{"offset": 204, "size": 4, "type": "f", "val": 0},
				"suspensionMaxTravel":	{"offset": 208, "size": 4, "type": "f", "num": 4, "val":	{"w": 0, 
																									"x": 0, 
																									"y": 0, 
																									"z": 0}},
				"tyreRadius":			{"offset": 224, "size": 4, "type": "f", "num": 4, "val": 	{"w": 0, 
																									"x": 0, 
																									"y": 0, 
																									"z": 0}}
				}
	size = 240
	
	def __init__(self):
		self.handle = mmap.mmap(0, self.size, "acpmf_static")
		
	def __del__(self):
		self.handle.close()

# Base object that holds the individual struct instances 
class AcSharedMemory(object):
	def __init__(self, mode=0x7):
		self.shm = {}
		# Init only the necessary structs.
		if mode & 0x1:
			self.shm["physics"] = AcPhysics()
		if mode & 0x2:
			self.shm["graphics"] = AcGraphics()
		if mode & 0x4:
			self.shm["static"] = AcStatic()
	
	# Read a single value to the object instance. If the variable is a struct in itself (i.e. with x,y,z etc. components) then all of those are updated.
	def readValue(self,key,name):
		self.shm[key].handle.seek(self.shm[key].memStruct[name]["offset"])
		if type(self.shm[key].memStruct[name]["val"]) == dict:
			# The variable has subcomponents.
			for k in self.shm[key].memStruct[name]["val"]:
				val = struct.unpack("<"+self.shm[key].memStruct[name]["type"], self.shm[key].handle.read(self.shm[key].memStruct[name]["size"]))[0]
				if self.shm[key].memStruct[name]["type"].find("s") != -1:
					# Convert to string when we have one.
					self.shm[key].memStruct[name]["val"][k] = self.bytesToString(val)
				else:
					self.shm[key].memStruct[name]["val"][k] = val
		else:
			# The variable doesn't have subcomponents.
			self.shm[key].handle.seek(self.shm[key].memStruct[name]["offset"])
			val = struct.unpack("<"+self.shm[key].memStruct[name]["type"], self.shm[key].handle.read(self.shm[key].memStruct[name]["size"]))[0] 
			if self.shm[key].memStruct[name]["type"].find("s") != -1:
				self.shm[key].memStruct[name]["val"] = self.bytesToString(val)
			else:
				self.shm[key].memStruct[name]["val"] = val
				
	def readValues(self,set):
		for section in set:
			for i in range(1,len(section)):
				self.readValue(section[0],section[i])
			
	def readSection(self, key):
		#self.shm[key].handle.seek(0)
		bytes = self.shm[key].handle.read(self.shm[key].size)
		for name in self.shm[key].memStruct:
			self.readValue(key,name)

	def readAll(self):
		for key in self.shm.keys():
			self.readSection(key)
		
	def bytesToString(self, bytes):
		return bytes.split(b"\x00")[0].decode()
