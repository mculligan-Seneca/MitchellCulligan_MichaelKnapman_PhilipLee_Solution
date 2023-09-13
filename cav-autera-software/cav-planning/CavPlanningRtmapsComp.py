import rtmaps.core as rt
import rtmaps.types
from rtmaps.base_component import BaseComponent  # base class
import rtmaps.reading_policy

from CavPlanning import *

# GLOBAL CONSTANTS

class rtmaps_python(BaseComponent):

    cavPlanning = None
    
    def __init__(self):
        BaseComponent.__init__(self)  # call base class constructor
        self.force_reading_policy(rtmaps.reading_policy.TRIGGERED)

    def Dynamic(self):
        
        self.add_input("TRIGGER_ms", rtmaps.types.INTEGER64)
        self.add_input("leadObjectValidity", rtmaps.types.UINTEGER8)
        self.add_input("leadObjectRelXPos_m", rtmaps.types.FLOAT32)
        self.add_input("leadObjectRelXVel_mps", rtmaps.types.FLOAT32)
        
        self.add_property("accSetSpeed_mps", 20)
        
        self.add_output("READY_ms", rtmaps.types.INTEGER64)
        self.add_output("targetVel_mps", rtmaps.types.AUTO)
        
    def writeData(self, outputName, data, bufferSize=1000000):
        outputData = rtmaps.types.Ioelt() # create ioelt from scratch
        outputData.buffer_size = bufferSize
        outputData.data = data
        self.write(outputName, outputData)
        
    def Birth(self):
        print("CavPlanning: Passing through Birth()")
        
        self.cavPlanning = CavPlanning()

    # TRIGGRED READING POLICY
    def Core(self):
        
        #get inputs/properties from rtmaps
        simTime_ms = self.inputs["TRIGGER_ms"].ioelt.data
        
        if simTime_ms > 0:
            leadObjectValidity = self.inputs["leadObjectValidity"].ioelt.data
            leadObjectRelXPos_m = self.inputs["leadObjectRelXPos_m"].ioelt.data
            leadObjectRelXVel_mps = self.inputs["leadObjectRelXVel_mps"].ioelt.data
            
            accSetSpeed_mps = self.properties["accSetSpeed_mps"].data
            
            #set perception data and acc set speed in CavPlanning class
            self.cavPlanning.setLeadVehData(leadObjectValidity, leadObjectRelXPos_m, leadObjectRelXVel_mps)
            self.cavPlanning.setAccSetSpd_mps(accSetSpeed_mps) 
            
            #run planning algorithm
            self.cavPlanning.determineTargetVelocity()
        
        #write outputs to rtmaps
        self.writeData("targetVel_mps", self.cavPlanning.getTargetVel_mps(), 1)
        self.writeData("READY_ms", simTime_ms, 1)

    def Death(self):
        print("CavPlanning: Passing through Death()")
        