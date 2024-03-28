import numpy as np

class camera:
    """
    Camera class
    """
    ### Constructor ###
    ### ----------- ###
    def __init__(self, name:str, properties:dict):
        """
        Camera constructor
        """

        self.name = name
        self.location = np.array([0,0,0])
        self.orientation = np.array([0,0,0,0])

        self.fov = properties['fov']*np.pi/180# [rad]
        self.res_x = properties['res_x'] # [-]
        self.res_y = properties['res_y'] # [-]
        self.res = np.array([self.res_x, self.res_y]) #[-]
        self.t_int = properties['T_int'] # [s]
        self.sensor = properties['sensor'] # (str)
        self.K = properties['K'] # [px]

    ### Methods ###
    ### ------- ###
    
    # Instance methods
    def get_name(self):
        return self.name

    def get_location(self):
        return self.location
    
    def get_orientation(self):
        return self.orientation

    def get_fov(self):
        return self.fov
    
    def get_res(self):
        return self.res

    def get_Tint(self):
        return self.t_int

    def get_K(self):
        return self.K
               
    def get_sensor(self):
        return self.sensor
    
    def set_position(self, location:np.array):
        self.location = location

    def set_orientation(self, orientation:np.array):
        self.location = orientation
    
    # Class methods
