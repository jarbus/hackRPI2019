import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np

from ..Drone import Drone

class Recovery(gym.Env):
    """ 
    map_size = x,y for size of map. 0,0 is the bottom left corner.
    
    Clusters generated using Poisson distribution. Each cluster must have at least one
    person, so mean = cluster_lambda + 1. If cluster = False, each cluster has 1 person. 

    Drones are randomly placed within a starting area. """
    
    metadata = {"render.modes": ["human"]}

    def __init__(self, *,
                 map_size: np.array,
                 drone_count: int,
                 base_camp: np.array,
                 cluster: bool = False,
                 cluster_count: int = 20,
                 cluster_lambda: int = 0):
        
        self.base_camp_loc = base_camp
        self.bounds = map_size
        
        # A complete network of drones including information about distance to other drones
        self.drones = []   
        self.people = []

        people_x = np.random.random_sample(cluster_count);
        people_y = np.random.random_sample(cluster_count);
        
        for i in range(drone_count):
            self.drones[i] = Drone(base_camp)

        cluster_centers = np.zeros((2, cluster_count))
        for i in range(cluster_count):
            pass

    def step(self, action):
        pass

    def reset(self):
        pass

    def render(self, mode="human"):
        pass

    def close(self):
        pass
