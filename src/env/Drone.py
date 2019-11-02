import spaces
from gym import spaces

class Drone:
    def __init__(self, base_camp_loc):
        # up down left right : 0 1 2 3
        self.base_camp_loc = base_camp_loc
        self.loc = (base_camp_loc[0], base_camp_loc[1])
        
        self.people_locs = set()
        self.action_space = spaces.Discrete(4)
        
    '''
    @param observation is a N x N grid representing the tiles that this drone can see
    @param reward ML?
    @param done for when he simulation is over
    '''
    def act(self, observation, reward, done):

        # update neighbors
        for x in range(7):
            for y in range(7):
                if x == 0 and y == 0: continue
                if type(observation[x][y]) == Drone:
                    observation[x][y].receive(self.people_locs)
        
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
    
    '''
    update this drones knowledge of the location of people
    '''
    def receive(history):
        pass

if __name__ == '__main__':
    print("Drone test")
    