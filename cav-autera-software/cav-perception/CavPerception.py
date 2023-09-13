import numpy as np

class CavPerception:
    
    radarData = None #2d numpy array where each row represents a radar point in the form [velocity, azimuthAngle, altitude, depth]
    lidarData = None #2d numpy array where each row represents a point of the point cloud in the form [xPosition, yPosition, zPosition]
    
    leadVehValidity = False
    leadVehRelXPos_m = 0
    leadVehRelXVel_mps = 0
    egoVehXVel_mps = 0
    
    def __init__(self):
        pass
    
    def processAndSetRadarData(self, rawRadarData): self.radarData = np.reshape(rawRadarData, (-1, 4))
    def processAndSetLidarData(self, rawLidarData): self.lidarData = np.reshape(rawLidarData, (-1, 3))
    def setEgoVehXVel(self, egoVehXVel_mps): self.egoVehXVel_mps = egoVehXVel_mps
    
    def getLeadVehValidity(self): return self.leadVehValidity
    def getLeadVehRelXPos_m(self): return self.leadVehRelXPos_m
    def getLeadVehRelXVel_mps(self): return self.leadVehRelXVel_mps
    
    def processAndFuseSensorData(self):
        
        # WRITE AN ALGORITHM THAT USES THE RADAR DATA (AND OPTIONALLY LIDAR DATA) TO DETERMINE THE POSITION AND VELOCITY OF THE LEAD VEHICLE (IF THERE IS ONE IN SENSOR RANGE)
        # IMLPEMENT YOUR CODE HERE! 
        
        self.leadVehValidity = False # validity flag (is there a lead vehicle in range?)
        self.leadVehRelXPos_m = 0 # relative position of the lead vehicle wrt ego vehicle (meters)
        self.leadVehRelXVel_mps = 0 # relative velocity of the lead vehicle wrt ego vehicle (meters/sec)