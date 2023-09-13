import rtmaps.core as rt
import rtmaps.types
from rtmaps.base_component import BaseComponent  # base class
import rtmaps.reading_policy

from CavPerception import *

# GLOBAL CONSTANTS

class rtmaps_python(BaseComponent):

    cavPerception = None
    
    def __init__(self):
        BaseComponent.__init__(self)  # call base class constructor
        self.force_reading_policy(rtmaps.reading_policy.TRIGGERED)

    def Dynamic(self):
        
        self.add_input("TRIGGER_ms", rtmaps.types.INTEGER64)
        self.add_input("lidarData", rtmaps.types.FLOAT32)
        self.add_input("radarData", rtmaps.types.FLOAT32)
        self.add_input("egoVehXVel_mps", rtmaps.types.FLOAT32)
        
        self.add_output("READY_ms", rtmaps.types.INTEGER64)
        self.add_output("leadVehValidity", rtmaps.types.AUTO)
        self.add_output("leadVehRelXPos_m", rtmaps.types.AUTO)
        self.add_output("leadVehRelXVel_mps", rtmaps.types.AUTO)
        
    def writeData(self, outputName, data, bufferSize=1000000):
        outputData = rtmaps.types.Ioelt() # create ioelt from scratch
        outputData.buffer_size = bufferSize
        outputData.data = data
        self.write(outputName, outputData)
        
    def Birth(self):
        print("CavPerception: Passing through Birth()")
        
        self.cavPerception = CavPerception()

    # TRIGGRED READING POLICY
    def Core(self):
        
        #get inputs from rtmaps
        simTime_ms = self.inputs["TRIGGER_ms"].ioelt.data
        
        rawRadarData = None
        rawLidarData = None
        
        if simTime_ms > 0:
            rawRadarData = self.inputs["radarData"].ioelt.data
            rawLidarData = self.inputs["lidarData"].ioelt.data
            egoVehXVel_mps = self.inputs["egoVehXVel_mps"].ioelt.data
        
            #set radar and lidar data in CavPerception class
            self.cavPerception.processAndSetRadarData(rawRadarData)
            self.cavPerception.processAndSetLidarData(rawLidarData)
            self.cavPerception.setEgoVehXVel(egoVehXVel_mps)
            
            #run perception algorithm
            self.cavPerception.processAndFuseSensorData()
        
        #write outputs to rtmaps
        self.writeData("leadVehValidity", int(self.cavPerception.getLeadVehValidity()), 1)
        self.writeData("leadVehRelXPos_m", float(self.cavPerception.getLeadVehRelXPos_m()), 1)
        self.writeData("leadVehRelXVel_mps", float(self.cavPerception.getLeadVehRelXVel_mps()), 1)
        self.writeData("READY_ms", simTime_ms, 1)

    def Death(self):
        print("CavPerception: Passing through Death()")
        