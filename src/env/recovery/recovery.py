import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
from functools import reduce

from ..Drone import Drone

class Recovery(gym.Env):
    """ 
    map_size = x,y for size of map. 0,0 is the bottom left corner.
    
    Drones are randomly placed within a starting area. """
    
    metadata = {"render.modes": ["human"]}

    def __init__(self, *,
                 map_size: np.array,
                 drone_count: int,
                 base_camp: np.array,
                 num_people):
        
        self.base_camp_loc = base_camp
        self.bounds = map_size
        self.map_x = map_size[0]
        self.map_y = map_size[1]
        self.num_people = num_people
        
        # A complete network of drones including information about distance to other drones
        self.drones = [Drone(id, base_camp) for id in range(1, drone_count)]
 
        # initializes 2xnum_people array of people, person i at
        # self.people[i][0], self.people[i][1]
        self.people = np.random.uniform(0, self.map_x, 2*num_people)
        np.resize(self.people, (2, self.num_people))


    '''
    helper functions for step function
    '''
    def get_bin(self, d):
        return (int(d.loc[0]//VISION), int(d.loc[1]//VISION))

    # drones are connected if they have a "path" of connection to one another
    # this function returns a list of drone isolated networks
    def get_connected_components(self):
        # set up data structure to handle "collisions" of drones
        bins = [[set() for y in range(int(HEIGHT//VISION))] for x in range(int(WIDTH//VISION))]
        # place drones in their respective bins
        for d in drones:
            x,y = self.get_bin(d)
            bins[x][y].add(d)
        
        # DFS drones to get connected components
        components = []
        unexplored = set(self.drones)
        while unexplored.size() > 0:
            # find the component of a random unexplored drone
            queue = [unexplored.pop()]
            component = set()
            while queue.size() > 0:
                cur = queue.pop()
                # explore the neighbors of cur
                component.add(cur)
                # find unexplored neighbors and add them to the queue
                # only check this and surrounding bins
                for i in range(-1,2):
                    for j in range(-1,2):
                        x, y = self.get_bin(cur)
                        x += i
                        y += j
                        if x < 0 or x >= bins.length() or y < 0 or y >= bins[0].length(): continue
                        # check all drones in this bin
                        bin = bins[x][y]
                        for d in bin:
                            if d != cur and cur.is_in_range(d) and d in unexplored:
                                queue.append(d)
                                unexplored.remove(d)
            # completed component: add to the list of components
            components.append(component)
        return components
    
    # step function: runs every iteration of the simulation
    def step(self, action):
        # determine the isolated networks
        components = self.get_connected_components()
        
        # consolidate information in each connected components
        for component in components:
            net_people_locs = reduce((lambda x,y: x.union(y)), [set()]+[d.get_people() for d in component])
            net_explored_locs = reduce((lambda x,y: x.union(y)), [set()]+[d.get_explored_locs() for d in component])
            for drone in component:
                drone.set_people_locs(net_people_locs)
                drone.set_explored_locs(net_explored_locs)
        
        # tell all of the drones to move
        for d in self.drones:
            d.calc_move()
        for d in self.drones:
            d.move()

    def reset(self):
        self.bounds = (0, 0)
        self.map_x = 0
        self.map_y = 0
        self.num_people = 0
        self.base_camp_loc = 0
        pass

    def render(self, mode="human"):
        pass

    def close(self):
        pass
