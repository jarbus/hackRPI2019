from gym import spaces
import sys

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

    '''
    @param vision: the set of people/locations that this drone can see
    '''
    def look(self, vision):
        self.people_locs = self.people_locs.union(vision)

    '''
    return a grid representation of the information collected so far
    '''
    def message(self):
        return self.people_locs, explored_locs

    '''
    receive an update from the connected network
    '''
    def receive(self, people_locs, explored_locs):
        look(ppl)
        self.explored_locs = self.explored_locs.union(explored_locs)


    def move(self):
        # TODO use ML algorithm to determine direction
        
        # each between -1 and 1
        dir_x = 0.0
        dir_y = 0.0
        
        dir_len = (dir_x**2+dir_y**2)**(0.5)
        
        # actual difference in location
        if dir_len > sys.float_info.epsilon:
            self.loc[0] += DRONE_SPEED * dir_x/dir_len
            self.loc[1] += DRONE_SPEED * dir_y/dir_len
    
            

        
if __name__ == '__main__':
    print("Drone test")
    