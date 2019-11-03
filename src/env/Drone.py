from gym import spaces
import sys
import random
import utils

DRONE_SPEED = 1.0

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

    '''
    @param vision: the set of people/locations that this drone can see
    '''
    def look(self, vision):
        self.people_locs = self.people_locs.union(vision)

    def set_people_locs(self, people_locs):
        self.people_locs

    def get_people_locs(self):
        return self.people_locs
    
    def set_explored_locs(self, explored_locs):
        self.explored_locs = explored_locs
        
    def get_explored_locs(self):
        return self.explored_locs
    

    '''
    receive an update from the connected network
    '''
    def receive(self, people_locs, explored_locs):
        look(ppl)
        self.explored_locs = self.explored_locs.union(explored_locs)
    
    # return whether or not the current drone is in range of another drone (Euclidean distance)
    def is_in_range(self, d):
        return utils.euclid(self.loc[0], self.loc[1], d.loc[0], d.loc[1]) <= VISION
        
        
    # determine movement direction
    def calc_move(self):
        #TODO use ML algorithm to pick movement
        self.dir_x = 0.0
        self.dir_y = 0.0
        
    # move location
    def move(self):
        dir_len = utils.euclid(dir_x, dir_y)
        if dir_len > sys.float_info.epsilon:
            self.loc[0] += DRONE_SPEED * dir_x/dir_len
            self.loc[1] += DRONE_SPEED * dir_y/dir_len
    
            

        
if __name__ == '__main__':
    print("Drone test")
    