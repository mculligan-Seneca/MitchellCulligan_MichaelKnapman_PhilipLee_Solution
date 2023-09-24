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
        
        # Theory/logic for code
        """
        For planning, we have four variables we have at our disposal. The leadVehValidity variable is data passed on by perception to planning to alert whether a lead vehicle exists or not.
        The leadVehRelXPos_m variable is data that signifies the current distance between the lead vehicle and ego vehicle. The leadVehRelXVel_mps variable is the speed of the lead vehicle calculated
        by perception. 
        
        - in the condition that ego vehicle detects no other vehicle in front of it, we pass a default speed(ideally the current speed the car is travelling at when the function is active)
        - in the condition that there is an ego vehicle in front and cruise control is on, we want to ideally maintain a minimum distance between the ego and the lead car
        - we could just set the targetVel_mps variable to be equal to the lead vehicle but this could lead to shaky constant acceleration deceleration of the ego vehicle.
        - as a simple algorithm, we will establish three zones which we will call the cold, hot and just right zone. The hot zone will be some far distance away from the lead vehicle which indicates that we want
          accelerate quickly in order to catch up, the cold zone will still be some distance farther from the ideal zone and the ideal zone is where we want to hover our speed. There is a small buffer distance
          the just right zone has for less jerky acceleration/deceleration
        - we want to have different hot zone/cold zone/just right following distances dependent on the velocity of the lead car. We also do want to consider cases where weather conditions may be worse but this algorithm
          will assume that we have good weather conditions
        """
        
        if self.leadVehValidity == 0: #THIS IS 0 TEMPORARILY FOR TESTING, CHANGE TO 1 LATER
            
            ideal_follow_distance = (1/2) * (self.leadVehRelXVel_mps) * 3
            
            if self.leadVehRelXPos_m > 1.3 * ideal_follow_distance: #Hot Zone
                self.targetVel_mps = self.leadVehRelXVel_mps + (leadVehRelXPos - ideal_follow_distance) / 2
                
            elif self.leadVehRelXpos_m <= 1.3 * ideal_follow_distance: #Cold Zone
                self.targetVel_mps = self.leadVehRelXVel_mps + (leadVehRelXPos - ideal_follow_distance) / 2.5
                
            elif (self.leadVehRelXPos_m <= ideal_follow_distance * 1.05) and (leadVehRelXPos_m > ideal_follow_distance): #this is our just right zone
                self.targetVel_mps = self.leadVehRelXVel_mps
                
            elif self.leadVehRelXPos_m < ideal_follow_distance: #adjust for when the car is inside of the safe follow distance and will come to complete stop if the calculated lead vehicle distance is 0
                self.target_Vel_mps = self.leadVehRelXVel_mps - (self.leadVehRelXPos-ideal_follow_distance)
        else:
            targetVel_mps = 30 #This is just a hardcoded variable since I do not have access to the vehicle's current speed
        
        self.targetVel_mps = targetVel_mps
