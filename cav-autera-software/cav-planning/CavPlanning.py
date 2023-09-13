class CavPlanning:
    
    leadVehValidity = 0
    leadVehRelXPos_m = 0
    leadVehRelXVel_mps = 0
    
    accSetSpd_mps = 0
    
    targetVel_mps = 0
    
    def __init__(self):
        pass
    
    def setLeadVehData(self, validity, relDist, relVel): 
        self.leadVehValidity = validity
        self.leadVehRelXPos_m = relDist
        self.leadVehRelXVel_mps = relVel
        
    def setAccSetSpd_mps(self, accSetSpd): self.accSetSpd_mps = accSetSpd 
    
    def getTargetVel_mps(self): return self.targetVel_mps
    
    def determineTargetVelocity(self):
        
        # WRITE AN ALGORITHM THAT USES THE LEAD VEHICLE DATA TO PLAN A TARGET VELOCITY FOR THE EGO VEHICLE TO FOLLOW
        # IMLPEMENT YOUR CODE HERE! 
        
        targetVel_mps = 0 # ego vehicle target velocity (m/s)
        
        self.targetVel_mps = targetVel_mps