import gym
from gym import error, spaces, utils
from gym.utils import seeding

import numpy as np
from functools import reduce

from ..Drone import Drone

VISION_RANGE = 5.0
COMM_RANGE = 10.0
DRONE_SPEED = 10.0

class Recovery(gym.Env):
    """ 
    map_size = x,y for size of map. 0,0 is the bottom left corner.
    
    Drones are randomly placed within a starting area. """
    
    metadata = {"render.modes": ["human"]}

    def __init__(self, *,
                 map_size: [int],
                 drone_count: int,
                 base_camp: np.array,
                 num_people: int,
                 debug: bool = False):
        
        self.base_camp_loc = base_camp
        self.bounds = map_size
        self.WIDTH = map_size[0]
        self.HEIGHT = map_size[1]
        self.num_people = num_people
        self.drone_count = drone_count
        
        # A complete network of drones including information about distance to other drones
        self.drones = [Drone(drone_id=id, drone_speed=DRONE_SPEED, comm_range=COMM_RANGE, vision_range=VISION_RANGE, base_camp_loc=base_camp, map_size=map_size) for id in range(1, drone_count)]
        # Base camp drone 0
        self.drones[0].loc = self.base_camp_loc
 
        # initializes 2xnum_people array of people, person i at
        # self.people[i][0], self.people[i][1]
        self.people = np.random.uniform(0, self.WIDTH, 2*num_people)
        np.resize(self.people, (2, self.num_people))

        if(debug):
            print("Initialized Recovery enviroment with", len(self.drones), "drones and", len(self.people), "people")

    '''
    helper functions for step function
    '''
    def get_bin_index(self, loc_x, loc_y, SCALAR):
        return (int(loc_x//SCALAR), int(loc_y//SCALAR))
        
    def neighboring_bins(self, loc_x, loc_y, SCALAR, bins):
        x, y = self.get_bin_index(loc_x, loc_y, SCALAR)
        for dx in range(-1, 2):
            for dx in range(-1, 2):
                bin_x = x + dx
                bin_y = y + dy
                if bin_x < 0 or bin_x >= bins.size() or bin_y < 0 or bin_y >= bins[0].size(): continue
                yield bins[bin_x][bin_y]
        

    # drones are connected if they have a "path" of connection to one another
    # this function returns a list of drone isolated networks,
    # and updates all of the drones in the process
    def get_connected_components(self):
        # set up data structure to handle "collisions" of drones / COMM_RANGE of people
        bins = [[set() for y in range(int(self.HEIGHT//COMM_RANGE))] for x in range(int(self.WIDTH//COMM_RANGE))]
        ppl_bins = [[set() for y in range(int(self.HEIGHT//VISION_RANGE))] for x in range(int(self.WIDTH//VISION_RANGE))]
        
        # place drones in their respective bins
        for d in self.drones:
            x, y = self.get_bin_index(d.loc[0], d.loc[1], COMM_RANGE)
            bins[x][y].add(d)
        
        # place people in the right ppl_bin
        for p in self.people:
            x, y = self.get_bin_index(p[0], p[1], VISION_RANGE)
            ppl_bins[x][y].add(p)
        
        # DFS drones to get connected components
        components = []
        unexplored = set(self.drones)
        while len(unexplored) > 0:
            # find the component of a random unexplored drone
            queue = [unexplored.pop()]
            component = set()
            while len(queue) > 0:
                cur = queue.pop()
                # update cur 
                close_bins = self.neighboring_bins(cur.loc[0], cur.loc[1], VISION_RANGE, ppl_bins)
                potential_people = reduce(lambda x, y: x.union(y), close_bins)
                people = filter(lambda p: d.can_see(p, VISION_RANGE), potential_people)
                cur.update(self.WIDTH, self.HEIGHT, VISION_RANGE, people)
                # explore the neighbors of cur
                component.add(cur)
                # find unexplored neighbors and add them to the queue
                # only check this and surrounding bins
                for b in neighboring_bins(cur.loc[0], cur.loc[1], COMM_RANGE, bins):
                    # check all drones in this bin
                    for d in b:
                        if d != cur and cur.can_communicate(d) and d in unexplored:
                            queue.append(d)
                            unexplored.remove(d)
            # completed component: add to the list of components
            components.append(component)
        return components
    
    # step function: runs every iteration of the simulation
    def step(self, action_n):
        done = False
        for i in range(1, len(self.drones)):
            self.drones[i].do_move(action_n[i][0], action_n[i][1])
        # determine the isolated networks and update the drones
        components = self.get_connected_components()
        
        # consolidate information in each connected components
        for component in components:
            net_people_locs = reduce((lambda x, y: x.union(y)), [d.get_people_locs() for d in component])
            net_explored_locs = reduce((lambda x, y: x.union(y)), [d.get_explored_locs() for d in component])
            for drone in component:
                drone.set_people_locs(net_people_locs)
                drone.set_explored_locs(net_explored_locs)

        # observations
        obs_n = np.zeros((len(self.drones)-1, 9))
        total_ppl_locs = set()
        for i in range(0, len(self.drones)-1):
            drone = self.drones[i+1]
            obs_n[i][0], obs_n[i][1], obs_n[i][2], obs_n[i][3] = drone.calc_quadrant_coverages()
            obs_n[i][4], obs_n[i][5] = drone.loc[0], drone.loc[1]
            obs_n[i][6], obs_n[i][7] = self.WIDTH, self.HEIGHT
            obs_n[i][8] = len(drone.people_locs)
            total_ppl_locs.union(drone.people_locs)

        if total_ppl_locs == self.num_people:
            done = True
        
        return obs_n, total_ppl_locs, done, None

    def reset(self):
        self.drones = [Drone(drone_id=id, drone_speed=DRONE_SPEED, comm_range=COMM_RANGE, vision_range=VISION_RANGE, base_camp_loc=self.base_camp_loc, map_size=self.bounds) for id in range(1, self.drone_count)]
        self.drones[0].loc = self.base_camp_loc

        self.people = np.random.uniform(0, self.WIDTH, 2*self.num_people)
        np.resize(self.people, (2, self.num_people))

        obs, _ ,_ ,_ = self.step(np.zeros((len(self.drones) - 1, 2)))
        return obs
        
    def render(self, mode="human"):
        pass

    def close(self):
        pass
