import carla, time, numpy as np, traceback, math
from scipy.interpolate import interp1d
from matplotlib import pyplot as plt

worldSensors = [] #global variable to make sure the sensor objects don't go out of scope in memory once executing function call

class CustomDriveCycle:
    
    interpolate = True
    timeWaypoints = []
    velocityWaypoints = []
    
    def __init__(self, waypoints=[], interpolate=True):
        self.timeWaypoints = []
        self.velocityWaypoints = []
        self.interpolate = interpolate
        for waypoint in waypoints:
            self.timeWaypoints.append(waypoint[0])
            self.velocityWaypoints.append(waypoint[1])
    
    def addWaypoint(self, time, velocity):
        self.timeWaypoints.append(time)
        self.velocityWaypoints.append(velocity)
        
    def getVelocity(self, currTime):
        
        if self.interpolate and currTime < self.timeWaypoints[len(self.timeWaypoints) - 1]:
            interpolateFnc = interp1d(self.timeWaypoints, self.velocityWaypoints)
            return interpolateFnc(currTime).item()
        else:
            timeIdx = len(self.timeWaypoints) - 1
            for i in range(len(self.timeWaypoints)):
                if self.timeWaypoints[i] > currTime: 
                    timeIdx = i - 1
                    break
                
            return self.velocityWaypoints[timeIdx]

class CavSensor:
    
    world = None
    sensor = None
    transform = None
    cavActor = None
    blueprint = None
    data = None

    def __init__(self, world, transform, cavActor, sensorBPName):
        self.world = world
        self.blueprint = self.world.get_blueprint_library().find(sensorBPName)
        self.transform = transform
        self.cavActor = cavActor

    def spawnSensor(self):
        
        global worldSensors
        
        self.sensor = self.world.spawn_actor(self.blueprint, self.transform, attach_to=self.cavActor.actor)
        self.sensor.listen(lambda data: self.setData(data))
        
        worldSensors.append(self.sensor) #store to global variable so does not go out of memory scope

    def destroySensor(self):
        if self.sensor != None: 
            self.sensor.stop()
            if self.sensor.is_alive: self.sensor.destroy()
        
    def setData(self, data):
        self.data = data
        
    def getSensorData(self):
        return self.data

class RGBCameraSensor(CavSensor):

    def __init__(self, world, transform, cavActor):
        super().__init__(world, transform, cavActor,"sensor.camera.rgb")
        
    def processAndGetData(self):
        #self.data = np.frombuffer(point_cloud.raw_data, dtype=np.float32).reshape(-1, 4)
        #self.data.save_to_disk('./cam_data/%.6d.png' % time.time())
        return np.frombuffer(self.data.raw_data, dtype=np.dtype("uint8")) # 1d vector with rgb repeating for n pixels

class RadarSensor(CavSensor):

    def __init__(self, world, transform, cavActor):
        super().__init__(world, transform, cavActor,"sensor.other.radar")
        
    def processAndGetData(self):
        #self.data = np.frombuffer(point_cloud.raw_data, dtype=np.float32).reshape(-1, 4)
        return np.frombuffer(self.data.raw_data, dtype=np.float32) # 1d vector with vel,azimuth,altitude,depth repeating for n points

class LidarSensor(CavSensor):

    def __init__(self, world, transform, cavActor):
        super().__init__(world, transform, cavActor,"sensor.lidar.ray_cast")
        self.blueprint.set_attribute('range', '100')
        self.blueprint.set_attribute('sensor_tick', '0.05')
        self.blueprint.set_attribute('rotation_frequency', '20')
        self.blueprint.set_attribute('channels', '64')
        self.blueprint.set_attribute('points_per_second', '112000')
        
    def processAndGetData(self):
        #self.data = np.frombuffer(point_cloud.raw_data, dtype=np.float32).reshape(-1, 4)
        #self.data.save_to_disk('./lidar_data/%.6d.ply' % time.time())
        #print(self.data.transform)
        return np.frombuffer(self.data.raw_data, dtype=np.float32) # 1d vector with x,y,z,i repeating for n points

class CavActor:
    
    world = None
    blueprint = None
    spawnTransform = None
    updateStrategy = "velocity"
    actor = None
    stepTime = 0
    
    targetTransform = None
    targetVelocityVector = None
    customDriveCycle = None
    
    sensors = {}
    
    def __init__(self, world, blueprint, spawnTransform, updateStrategy, driveCycle=None):
        self.world = world
        self.stepTime = self.world.get_settings().fixed_delta_seconds
        self.blueprint = blueprint
        self.spawnTransform = spawnTransform
        self.targetTransform = spawnTransform
        self.updateStrategy = updateStrategy
        self.customDriveCycle = driveCycle
        self.setTargetVelocity(0,0,0)
        
    def spawn(self):
        self.actor = self.world.spawn_actor(self.blueprint, self.spawnTransform)
        for sensor in self.sensors.values(): sensor.spawnSensor()
        
    def destroy(self):
        for sensor in self.sensors.values(): sensor.destroySensor() 
        if self.actor != None: self.actor.destroy()

    def addSensor(self, sensorName, sensorType, offset_x=0, offset_y=0, offset_z=0, pitch=0, yaw=0, roll=0):
     
        transform = carla.Transform(carla.Location(x = offset_x, y = offset_y, z = offset_z), carla.Rotation(pitch, yaw, roll))

        if sensorType == "lidar":
            lidar = LidarSensor(self.world, transform, self)
            self.sensors[sensorName] = lidar
        elif sensorType == "radar":
            radar = RadarSensor(self.world, transform, self)
            self.sensors[sensorName] = radar
        elif sensorType == "rgbcam":
            cam = RGBCameraSensor(self.world, transform, self)
            self.sensors[sensorName] = cam

    def getSensor(self, sensorName):
        return self.sensors[sensorName]
    
    def getActorVelocity(self): 
        return self.actor.get_velocity()
    
    def getActorTransform(self):
        return self.actor.get_transform()

    def setTargetVelocity(self, x=0, y=0, z=0):
        self.targetVelocityVector = carla.Vector3D(x, y, z)
        
    def setTargetTransform(self, x=0, y=0, z=0, pitch=0, yaw=0, roll=0):
        
        # only updating x, y, and yaw from plant model for now
        currTranform = self.actor.get_transform()
        correctedX = x + self.spawnTransform.location.x
        correctedY = y + self.spawnTransform.location.y
        correctedZ = currTranform.location.z
        correctedPitch = currTranform.rotation.pitch
        correctedYaw = yaw + self.spawnTransform.rotation.yaw
        correctedRoll = currTranform.rotation.roll
        
        self.targetTransform = carla.Transform(
            carla.Location(correctedX, correctedY, correctedZ), 
            carla.Rotation(correctedPitch, correctedYaw, correctedRoll))
        
  
    def setDriveCycle(self, driveCycle):
        self.customDriveCycle = driveCycle
        
    def update(self, currTime):
        
        # get speed source -- checks if drive cycle exists, otherwise uses target.
        targetVel = 0
        if self.customDriveCycle != None:
            xVel = self.customDriveCycle.getVelocity(currTime)
            self.setTargetVelocity(xVel, 0, 0)
        
        if self.actor != None:
            if self.updateStrategy == "velocity":
                self.actor.set_target_velocity(self.targetVelocityVector)
                
            elif self.updateStrategy == "positionByVelocity":
                actorLoc = self.actor.get_location()
                actorLoc.x += self.targetVelocityVector.x * self.stepTime
                actorLoc.y += self.targetVelocityVector.y * self.stepTime
                actorLoc.z += self.targetVelocityVector.z * self.stepTime
                self.actor.set_location(actorLoc)
                
            elif self.updateStrategy == "positionByTransform":
                self.actor.set_transform(self.targetTransform)

            else:
                print("invalid update strategy.")

class CavCarlaWorld:
    
    #client and world settings
    client = None
    world = None
    worldMap = None
    worldSettings = None
    spectator = None
    bpLibrary = None
    stepTime = 0
    
    #actors
    actors = {}
    
    def __init__(self, mapName, syncStep):
        
        #initialize client
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(30.0)
        
        #load world and get map, spectator, settings
        self.world = self.client.load_world(mapName)
        self.worldMap = self.world.get_map()
        self.spectator = self.world.get_spectator()
        self.worldSettings = self.world.get_settings()
        
        #set sync mode settings
        self.stepTime = syncStep
        self.worldSettings.fixed_delta_seconds = self.stepTime
        
        #get blueprint library
        self.bpLibrary = self.world.get_blueprint_library()
    
    def updateWorldSettings(self):
        self.world.apply_settings(self.worldSettings)
        
    def setSyncMode(self, isSyncMode):
        self.worldSettings.synchronous_mode = isSyncMode
        self.updateWorldSettings
        
    def getActorBP(self, actorType):
        carlaBPID = actorType
        if actorType == "nissanSUV": carlaBPID = "vehicle.nissan.patrol_2021"
        elif actorType == "policecar": carlaBPID = "vehicle.dodge.charger_police"
        elif actorType == "teslaModel3": carlaBPID = "vehicle.tesla.model3"
        
        return self.bpLibrary.filter(carlaBPID)[0]
    
    def setSpectatorToActor(self, actorTransform, xOffset=0, yOffset=0, zOffset=0):
        spectatorTransform = carla.Transform(
            carla.Location(actorTransform.location.x + xOffset, 
                           actorTransform.location.y + yOffset, 
                           actorTransform.location.z + zOffset),
            actorTransform.rotation)
        
        self.spectator.set_transform(spectatorTransform)

    def setSpectatorToEgo(self):
        try:
            self.setSpectatorToActor(self.getActor('ego').actor.get_transform(), xOffset=10, zOffset=5)
        except:
            print('no ego actor in sim!')
            
    def addActorByTransform(self, actorName, actorType="nissanSUV", x=0, y=0, z=0, pitch=0, yaw=0, roll=0, updateStrategy="velocity"):
        actorSpawnPoint = carla.Transform(carla.Location(x, y, z), carla.Rotation(pitch, yaw, roll))
        
        newActor = CavActor(self.world, self.getActorBP(actorType), actorSpawnPoint, updateStrategy)
        
        if actorName=="ego": self.setSpectatorToActor(actorSpawnPoint, xOffset=10, zOffset=5)
        
        self.actors[actorName] = newActor
        
    def addActorByMapSpawnPtIdx(self, actorName, mapSpawnLocIdx=0, actorType="nissanSUV", updateStrategy="velocity", xOffset=0, yOffset=0, zOffset=0):
        actorSpawnPoint = self.worldMap.get_spawn_points()[mapSpawnLocIdx]
        actorSpawnPoint.location.x += xOffset
        actorSpawnPoint.location.y += yOffset
        actorSpawnPoint.location.z += zOffset
        
        if actorName=="ego": self.setSpectatorToActor(actorSpawnPoint, xOffset=10, zOffset=5)
        
        newActor = CavActor(self.world, self.getActorBP(actorType), actorSpawnPoint, updateStrategy)
        
        self.actors[actorName] = newActor
        
    def getActor(self, actorName): 
        return self.actors[actorName]
       
    def initSim(self):
        
        #set world to sync mode
        self.setSyncMode(True)
    
        #spawn all actors
        for actor in self.actors.values(): actor.spawn()
        
    def runSimTimestep(self, currTime):
                
        # Update kinematics of actors in world
        for actor in self.actors.values(): actor.update(currTime)

        #teleport spectator to ego veh
        self.setSpectatorToEgo()
        
        # Update timestep of world
        self.world.tick()
        
    def terminateSim(self):
        
        global worldSensors
            
        #destroy all actors on sim end or sim exception
        for actor in self.actors.values(): 
            actor.destroy()
        
        #set world back to async mode
        self.setSyncMode(False)
        
        #remove any global sensor references
        worldSensors = []
        
    def runMainLoop(self, endTime=-1, printDebug=True):
        
        #set end time to funcionally infinity if endTime paramater is negative
        realEndTime = endTime if endTime > 0 else 10000000
        
        try:
            
            self.initSim()
        
            recordedStartTime = time.time()
            for currTime in np.arange(0, realEndTime, self.stepTime): self.runSimTimestep(currTime)
            recordedEndTime = time.time()
            
            if printDebug: print("Real time,", endTime, "seconds of simtime:", (recordedEndTime - recordedStartTime))
                
        except:
            
            print("FAILURE DURING MAIN RUN LOOP")
            traceback.print_exc()
            
        finally:
            
            self.terminateSim()