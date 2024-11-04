
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
    
    def processAndSetRadarData(self, rawRadarData): 
        self.radarData = np.reshape(rawRadarData, (-1, 4))
        
    def processAndSetLidarData(self, rawLidarData): 
        self.lidarData = np.reshape(rawLidarData, (-1, 3))
    
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

'''


import numpy as np
from  scipy.cluster.vq import kmeans,whiten
from sklearn.cluster  import DBSCAN
class CavPerception:
    
    radarData = None #2d numpy array where each row represents a radar point in the form [velocity, azimuthAngle, altitude, depth]
    lidarData = None #2d numpy array where each row represents a point of the point cloud in the form [xPosition, yPosition, zPosition]
    
    leadVehValidity = False
    leadVehRelXPos_m = 0
    leadVehRelXVel_mps = 0
    egoVehXVel_mps = 0
    
    def __init__(self):
        pass
        

    def clusterData(self,data,k):
        clusters=DBSCAN(eps=0.5, min_samples=2).fit_predict(data)
        #Get maximum data onject collected that isnt noise
        filteredClusters=clusters[clusters!=-1]
        if np.size(filteredClusters)==0:
            return None
        
        car_label=np.argmax(np.bincount(filteredClusters))
   
   
    
        car_data= data[np.argwhere(clusters==car_label)[0]]
         #retrieve avg for all points
        leadCar=[np.mean(car_data[:,k]) for k in range(car_data.shape[1])]
    
        return np.array(leadCar)
         #array  of objects found
    
    def processAndSetRadarData(self, rawRadarData): 
        self.radarData = np.reshape(rawRadarData, (-1, 4))
        
    def processAndSetLidarData(self, rawLidarData): 
        self.lidarData = np.reshape(rawLidarData, (-1, 3))
    
    def setEgoVehXVel(self, egoVehXVel_mps): self.egoVehXVel_mps = egoVehXVel_mps
    
    def getLeadVehValidity(self): return self.leadVehValidity 
    def getLeadVehRelXPos_m(self): return self.leadVehRelXPos_m
    def getLeadVehRelXVel_mps(self): return self.leadVehRelXVel_mps
    
  

    def processAndFuseSensorData(self):


        TIME_STEP=0.05
        k=2
        # WRITE AN ALGORITHM THAT USES THE RADAR DATA (AND OPTIONALLY LIDAR DATA) TO DETERMINE THE POSITION AND VELOCITY OF THE LEAD VEHICLE (IF THERE IS ONE IN SENSOR RANGE)
        # IMLPEMENT YOUR CODE HERE! 
        #detected objects
        if self.radarData is not None:
            leadCar=self.clusterData(self.radarData)
            
            if leadCar is not None:
                self.prevRadar=leadCar
                self.leadVehValidity = True# validity flag (is there a lead vehicle in range?)
                self.leadVehRelXPos_m =  leadCar[2]# relative position of the lead vehicle wrt ego vehicle (meters)
                self.leadVehRelXVel_mps = leadCar[0]-self.egoVehXVel_mps # relative velocity of the lead vehicle wrt ego vehicle (meters/sec)
            else:
                self.leadVehValidity = False # validity flag (is there a lead vehicle in range?)
                self.leadVehRelXPos_m = 0 # relative position of the lead vehicle wrt ego vehicle (meters)
                self.leadVehRelXVel_mps = 0 # relative velocity of the lead vehicle wrt ego vehicle (meters/sec)

'''