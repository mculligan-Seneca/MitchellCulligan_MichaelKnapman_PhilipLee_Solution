import rtmaps.core as rt
import rtmaps.types
from rtmaps.base_component import BaseComponent  # base class
import rtmaps.reading_policy

from CavCarlaFramework import *

# GLOBAL CONSTANTS
MAP_NAME = 'Town06'
SYNC_TIMESTEP = 0.05 

# CUSTOM DRIVE CYCLES TO CHOOSE FROM!
CONSTANT_SPEED_MPS                  = 5
CONSTANT_SPEED_DRIVE_CYCLE          = CustomDriveCycle([[0, -1*CONSTANT_SPEED_MPS], [10, -1*CONSTANT_SPEED_MPS]])
SLOW_TO_HALF_SPEED_DRIVE_CYCLE      = CustomDriveCycle([[0, -1*CONSTANT_SPEED_MPS], [10, -1*CONSTANT_SPEED_MPS], [20, -1*CONSTANT_SPEED_MPS/2]])
SLOW_TO_STOP_DRIVE_CYCLE            = CustomDriveCycle([[0, -1*CONSTANT_SPEED_MPS], [10, -1*CONSTANT_SPEED_MPS], [20, 0]])
SPEED_UP_FROM_STOP_DRIVE_CYCLE      = CustomDriveCycle([[0, 0], [10, -1*CONSTANT_SPEED_MPS]])

LEAD_VEHICLE_DRIVE_CYCLE = SLOW_TO_HALF_SPEED_DRIVE_CYCLE

class rtmaps_python(BaseComponent):

    carlaFramework = None
    time = 0
    
    def __init__(self):
        BaseComponent.__init__(self)  # call base class constructor
        self.force_reading_policy(rtmaps.reading_policy.TRIGGERED)

    def Dynamic(self):
        self.add_input("TRIGGER_ms", rtmaps.types.ANY)
        self.add_input("xPos_m", rtmaps.types.ANY)
        self.add_input("yPos_m", rtmaps.types.ANY)
        self.add_input("yaw_deg", rtmaps.types.ANY)
        
        self.add_output("READY_ms", rtmaps.types.AUTO)
        self.add_output("lidarData", rtmaps.types.FLOAT32)
        self.add_output("radarData", rtmaps.types.FLOAT32)
        self.add_output("leadVehSpeed_ms", rtmaps.types.FLOAT32)
        self.add_output("leadVehRelXPos_m", rtmaps.types.FLOAT32)
        
    def writeData(self, outputName, data, bufferSize=1000000):
        outputData = rtmaps.types.Ioelt() # create ioelt from scratch
        outputData.buffer_size = bufferSize
        outputData.data = data
        self.write(outputName, outputData)
        
    def Birth(self):
        print("Passing through Birth()")
        
        self.time = 0
        
        self.carlaFramework = CavCarlaWorld(MAP_NAME, SYNC_TIMESTEP)
        
        #spawn ego vehicle and add sensors
        self.carlaFramework.addActorByMapSpawnPtIdx('ego', 0, yOffset=-3.75, updateStrategy="positionByTransform")
        self.carlaFramework.getActor('ego').addSensor("ouster", "lidar", offset_z=3)
        self.carlaFramework.getActor('ego').addSensor("radar1", "radar", offset_z=2)
        #self.carlaFramework.getActor('ego').addSensor("rgbcam1", "rgbcam", offset_x=-10, offset_z=2, pitch=10)
        
        self.carlaFramework.addActorByMapSpawnPtIdx('leadVeh', 0, xOffset=-10, yOffset=-3.75, actorType="teslaModel3", updateStrategy="velocity")
        self.carlaFramework.getActor('leadVeh').setDriveCycle(LEAD_VEHICLE_DRIVE_CYCLE)
        
        self.carlaFramework.initSim()

    # TRIGGRED READING POLICY
    def Core(self):
        
        simTime = self.inputs["TRIGGER_ms"].ioelt.data 
        
        egoX = 0
        egoY = 0
        egoYaw_rad = 0
        
        #check if not the first timestep
        if simTime > 0:

            egoX = self.inputs["xPos_m"].ioelt.data
            egoY = self.inputs["yPos_m"].ioelt.data
            egoYaw_rad = self.inputs["yaw_deg"].ioelt.data
            
            self.time += SYNC_TIMESTEP
        
        #set position of the vehicle in the environment, then run sim for one timestep
        self.carlaFramework.getActor('ego').setTargetTransform(x=-1*egoX, y=egoY, yaw=-1*egoYaw_rad*360/(2*math.pi))
        self.carlaFramework.runSimTimestep(self.time)
        
        #get sensor data from ego's sim sensors
        egoLidarData = self.carlaFramework.getActor('ego').getSensor('ouster').processAndGetData()
        egoLidarData = np.delete(egoLidarData, [i for i in range(len(egoLidarData)) if i % 4 == 3])
        egoRadarData = self.carlaFramework.getActor('ego').getSensor('radar1').processAndGetData()
        #egoCamData = self.carlaFramework.getActor('ego').getSensor('rgbcam1').processAndGetData()
        
        #send outputs to rtmaps if sensor data non-empty
        if len(egoLidarData):
            self.writeData("lidarData", egoLidarData, bufferSize=(1000000 if simTime == 0 else len(egoLidarData)))
        if len(egoRadarData):
            self.writeData("radarData", egoRadarData, bufferSize=(1000000 if simTime == 0 else len(egoRadarData)))
            
        self.writeData("leadVehSpeed_ms", np.single(-1 * self.carlaFramework.getActor('leadVeh').getActorVelocity().x), 1)
        self.writeData("leadVehRelXPos_m", np.single(-1 * self.carlaFramework.getActor('leadVeh').getActorTransform().location.x + self.carlaFramework.getActor('ego').getActorTransform().location.x), 1)
        
        # send back timestep to master scehduler to indicate component is ready for next timestep
        self.outputs["READY_ms"].write(self.inputs["TRIGGER_ms"].ioelt)

    def Death(self):
        print("Passing through Death()")
        
        self.carlaFramework.terminateSim()