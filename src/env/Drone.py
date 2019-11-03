# from gym import spaces
import sys
import random
from . import utils

class Drone:
    def __init__(self, *,
            drone_id: int,
            drone_speed: float,
            comm_range: float,
            vision_range: float,
            base_camp_loc: [int] = [10, 10],
            map_size: [int, int]):
        self.base_camp_loc = base_camp_loc
        self.loc = base_camp_loc
        
        # add random noise to starting location
        self.loc[0] += random.random() - 0.5
        self.loc[1] += random.random() - 0.5

        self.people_locs = set() # floating points
        self.unsent_locs = 0
        self.explored_locs = set() # tiles in grid

        self.drone_speed = drone_speed
        self.comm_range = comm_range
        self.vision_range = vision_range
        self.map_size = map_size

    # mark now explored tiles and found people
    # ppl is a list of people visible to this drone
    def update(self, ppl):
        # add tiles within vision range of this drone
        for dx in range(-int(self.vision_range), int(self.vision_range)):
            for dy in range(-int(self.vision_range), int(self.vision_range)):
                grid_x = int(self.loc[0]+dx)
                grid_y = int(self.loc[1]+dy)
                if self.can_see(grid_x, grid_y):
                    self.explored_locs.add((grid_x, grid_y))
        
        # add people within vision range of this drone
        self.people_locs.union(ppl)

    def set_people_locs(self, people_locs):
        self.people_locs = people_locs

    def get_people_locs(self):
        return self.people_locs
    
    def set_explored_locs(self, explored_locs):
        self.explored_locs = explored_locs
        
    def get_explored_locs(self):
        return self.explored_locs

    # helper for calc_quadrant_coverages
    # x_dir and y_dir are booleans indicating quadrant direction (x_dir = True ~ right)
    def calc_quadrant_coverage(self, x_dir, y_dir):
        x_comp = lambda loc: loc[0] > self.loc[0] if x_dir else loc[0] < self.loc[0]
        y_comp = lambda loc: loc[1] > self.loc[1] if y_dir else loc[1] < self.loc[1]
        # count => number of explored tiles
        # total => number of tiles in relative quadrant
        count = sum(filter(lambda loc: int(x_comp(loc) and y_comp(loc)), self.explored_locs))
        total = abs(int((self.map_size[0] if x_dir else 0) - self.loc[0]) * int((self.map_size[1] if y_dir else 0) - self.loc[1]))
        return 1.0 if total == 0 else count / total
    
    '''
    determine the average exploration coverage in the four quadrants relative
    to the location of this drone; returns 100% coverage if at edge of map
    '''
    def calc_quadrant_coverages(self):
        top_right_avg = self.calc_quadrant_coverage(True, True, self.map_size[0], self.map_size[1])
        top_left_avg = self.calc_quadrant_coverage(False, True, self.map_size[0], self.map_size[1])
        bot_right_avg = self.calc_quadrant_coverage(True, False, self.map_size[0], self.map_size[1])
        bot_left_avg = self.calc_quadrant_coverage(False, False, self.map_size[0], self.map_size[1])
        return top_right_avg, top_left_avg, bot_right_avg, bot_left_avg
        
    # return whether or not the current drone can see the given person (Euclidean distance)
    def can_see(self, p):
        return utils.euclid(self.loc[0], self.loc[1], p[0], p[1]) <= self.vision_range
        
    # return whether or not the current drone is in range of another drone 
    def can_communicate(self, d):
        return self.can_see(self, (d.loc[0], d.loc[1]), self.comm_range)

    # The ML Algorithm should be interating with environment and not the Drone.
    # The Drone should not try to contact the ML algorithm in anyway
    
    # # determine movement direction
    # def calc_move(self):
    #     #TODO use ML algorithm to pick movement
    #     self.dir_x = 0.0
    #     self.dir_y = 0.0
        
    # move location
    def do_move(self,
                dir_x: float,
                dir_y: float):
        dir_len = utils.pythagorean(a = dir_x, b = dir_y)
        if dir_len > sys.float_info.epsilon:
            self.loc[0] += self.drone_speed * dir_x/dir_len
            self.loc[1] += self.drone_speed * dir_y/dir_len
            # check bounds
            if self.loc[0] < 0.0: self.loc[0] = 0.0
            if self.loc[0] > self.map_size[0]: self.loc[0] = self.map_size[0]
            if self.loc[1] < 0.0: self.loc[0] = 0.0
            if self.loc[1] > self.map_size[1]: self.loc[0] = self.map_size[1]
                   
if __name__ == '__main__':
    print("Drone test")
    
