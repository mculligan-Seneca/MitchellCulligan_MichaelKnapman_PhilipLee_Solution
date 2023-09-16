import numpy as np
class CavControls:
    
    targetVel_mps = 0
    egoVehXVel_mps = 0
    
    accelPdl_pct = 0
    decelPdl_pct = 0
    
    def __init__(self):
        self.intergral_err=0.0
        self.prev_err=0.0
    
    def setTargetVel_mps(self, vel): self.targetVel_mps = vel
    def setEgoVehXVel(self, egoVehXVel_mps): self.egoVehXVel_mps = egoVehXVel_mps
    
    def getAccelPdl_pct(self): return self.accelPdl_pct
    def getDecelPdl_pct(self): return self.decelPdl_pct
    
    def executeLongitudinalControl(self):
        MIN_STEP=0.01

        kp=0.5
        ki=23
        kd=-0.1

        pe=self.targetVel_mps-self.egoVehXVel_mps
        self.intergral_err+=MIN_STEP*pe
        de=pe-self.prev_err
        self.prev_err=pe
        v=kp*pe+self.intergral_err*ki+kd*de
        # WRITE AN ALGORITHM THAT USES THE TARGET VELOCITY TO GENERATE AN ACCEL/BRAKE PEDAL POSITION TO CONTROL THE VEHICLE
        # IMLPEMENT YOUR CODE HERE! 
       
        accelPdl_pct = v # accelerator pedal percentage in range [0, 1]
        decelPdl_pct = 1-v # brake pedal percentage in range [0, 1]
        
        self.accelPdl_pct = accelPdl_pct
        self.decelPdl_pct = decelPdl_pct