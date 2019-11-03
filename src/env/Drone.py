from gym import spaces
import sys
import random
import utils

class Drone:
    def __init__(self, base_camp_loc):
        self.base_camp_loc = base_camp_loc
        self.loc = base_camp_loc
        # add random noise to starting location
        self.loc[0] += random.random() - 0.5
        self.loc[1] += random.random() - 0.5

        self.people_locs = set() # floating points
        self.explored_locs = set() # tiles in grid
        
        # each between -1 and 1; represents direction of movement
        self.dir_x = 0.0
        self.dir_y = 0.0

    # mark now explored tiles and found people
    # ppl is a list of people visible to this drone
    def update(self, WIDTH, HEIGHT, VISION_RANGE, ppl):
        # add tiles within vision range of this drone
        for dx in range(-int(VISION_RANGE), int(VISION_RANGE)):
            for dy in range(-int(VISION_RANGE), int(VISION_RANGE)):
                grid_x = int(self.loc[x]+dx)
                grid_y = int(self.loc[y]+dy)
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
    def calc_quadrant_coverage(self, x_dir, y_dir, WIDTH, HEIGHT):
        x_comp = lambda loc: loc[0] > self.loc[0] if x_dir else loc[0] < self.loc[0]
        y_comp = lambda loc: loc[1] > self.loc[1] if y_dir else loc[1] < self.loc[1]
        # count => number of explored tiles
        # total => number of tiles in relative quadrant
        count = sum(filter(lambda loc: int(x_comp(loc) and y_comp(loc)), self.explored_locs))
        total = abs(int((WIDTH if x_dir else 0) - self.loc[0]) * int((HEIGHT if y_dir else 0) - self.loc[1]))
        return 1.0 if total == 0 else count / total
    
    '''
    determine the average exploration coverage in the four quadrants relative
    to the location of this drone; returns 100% coverage if at edge of map
    '''
    def calc_quadrant_coverages(self, WIDTH, HEIGHT):
        top_right_avg = self.calc_quadrant_coverage(true, true, WIDTH, HEIGHT)
        top_left_avg = self.calc_quadrant_coverage(false, true, WIDTH, HEIGHT)
        bot_right_avg = self.calc_quadrant_coverage(true, false, WIDTH, HEIGHT)
        bot_left_avg = self.calc_quadrant_coverage(false, false, WIDTH, HEIGHT)
        return top_right_avg, top_left_avg, bot_right_avg, bot_left_avg
        
    # return whether or not the current drone can see the given person (Euclidean distance)
    def can_see(self, p, VISION_RANGE):
        return utils.euclid(self.loc[0], self.loc[1], p[0], p[1]) <= VISION_RANGE
        
    # return whether or not the current drone is in range of another drone 
    def can_communicate(self, d, COMM_RANGE):
        return self.can_see(self, (d.loc[0], d.loc[1]), COMM_RANGE)
        
    # determine movement direction
    def calc_move(self):
        #TODO use ML algorithm to pick movement
        self.dir_x = 0.0
        self.dir_y = 0.0
        
    # move location
    def do_move(self, DRONE_SPEED, WIDTH, HEIGHT):
        dir_len = utils.euclid(dir_x, dir_y)
        if dir_len > sys.float_info.epsilon:
            self.loc[0] += DRONE_SPEED * dir_x/dir_len
            self.loc[1] += DRONE_SPEED * dir_y/dir_len
            # check bounds
            if self.loc[0] < 0.0: self.loc[0] = 0.0
            if self.loc[0] > WIDTH: self.loc[0] = WIDTH
            if self.loc[1] < 0.0: self.loc[0] = 0.0
            if self.loc[1] > HEIGHT: self.loc[0] = HEIGHT
    
            

        
if __name__ == '__main__':
    print("Drone test")
    