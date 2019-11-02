import spaces
from gym import spaces

class Drone:
    def __init__(self, base_camp_loc):
        self.base_camp_loc = base_camp_loc
        self.last_seen_drone = base_camp_loc        
        self.loc = base_camp_loc
        
        self.people_locs = set() # floating points
        self.explored_locs = set() # tiles in grid
        
        # up down left right : 0 1 2 3
        self.action_space = spaces.Discrete(4)
        
    '''
    @param vision: the set of people/locations that this drone can see
    '''
    def look(self, vision):
        self.people_locs = self.people_locs.union(vision)
    
    '''
    return a grid representation of the information collected so far
    '''
    def message(self):
        return self.people_locs
    
    def receive(self, ppl):
        look(ppl)
       
    '''
    @param observation is a N x N grid representing the tiles that this drone can see
    @param reward ML?
    @param done for when he simulation is over
    '''
    def act(self, observation, reward, done):
        
        # record visible people
        
        
        # TODO use ML to determine action
        action = self.action_space.sample()
        
        # up down left right
        if action == 0:
            self.loc[1] += 1
        elif action == 1:
            self.loc[1] -= 1
        elif action == 2:
            self.loc[0] -= 1
        elif action == 3:
            self.loc[0] += 1
        
        return action
    
    

        
if __name__ == '__main__':
    print("Drone test")
    