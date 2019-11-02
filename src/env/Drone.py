import spaces
from gym import spaces

class Drone:
    def __init__(self):
        # up down left right : 0 1 2 3
        self.loc = (0,0)
        self.history = []
        self.action_space = spaces.Discrete(4)
        
    '''
    @param observation is a N x N grid representing the tiles that this drone can see
    @param reward ML?
    @param done for when he simulation is over
    '''
    def act(self, observation, reward, done):
        
        
        # use ML to determine action
        
        return self.action_space.sample()

if __name__ == '__main__':
    print("Drone test")
    