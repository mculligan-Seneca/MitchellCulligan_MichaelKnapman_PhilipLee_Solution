import rtmaps.core as rt
import rtmaps.types
from rtmaps.base_component import BaseComponent  # base class
import rtmaps.reading_policy

import numpy as np
from CavControls import *

# GLOBAL CONSTANTS

class rtmaps_python(BaseComponent):

    cavControls = None
    
    def __init__(self):
        BaseComponent.__init__(self)  # call base class constructor
        self.force_reading_policy(rtmaps.reading_policy.TRIGGERED)

    def Dynamic(self):
        
        self.add_input("TRIGGER_ms", rtmaps.types.INTEGER64)
        self.add_input("targetVel_mps", rtmaps.types.FLOAT32)
        self.add_input("egoVehXVel_mps", rtmaps.types.FLOAT32)
        
        self.add_output("READY_ms", rtmaps.types.INTEGER64)
        self.add_output("accelPdl_pct", rtmaps.types.FLOAT32)
        self.add_output("decelPdl_pct", rtmaps.types.FLOAT32)
        self.add_output("steeringCmd_deg", rtmaps.types.FLOAT32)
        
    def writeData(self, outputName, data, bufferSize=1000000):
        outputData = rtmaps.types.Ioelt() # create ioelt from scratch
        outputData.buffer_size = bufferSize
        outputData.data = data
        self.write(outputName, outputData)
        
    def Birth(self):
        print("CavControls: Passing through Birth()")
        
        self.cavControls = CavControls()

    # TRIGGRED READING POLICY
    def Core(self):
        
        #get inputs from rtmaps
        simTime_ms = self.inputs["TRIGGER_ms"].ioelt.data
        
        if simTime_ms > 0:
            targetVel_mps = self.inputs["targetVel_mps"].ioelt.data
            egoVehXVel_mps = self.inputs["egoVehXVel_mps"].ioelt.data
            
            #set target velocity
            self.cavControls.setTargetVel_mps(targetVel_mps)
            self.cavControls.setEgoVehXVel(egoVehXVel_mps)
            
            #run longitudinal control algorithm
            self.cavControls.executeLongitudinalControl()
        
        #write outputs to rtmaps
        self.writeData("accelPdl_pct", np.single(self.cavControls.getAccelPdl_pct()), 1)
        self.writeData("decelPdl_pct", np.single(self.cavControls.getDecelPdl_pct()), 1)
        self.writeData("steeringCmd_deg", np.single(0), 1)
        self.writeData("READY_ms", simTime_ms, 1)

    def Death(self):
        print("CavControls: Passing through Death()")
        