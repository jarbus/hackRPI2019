""" Policy Gradient optimizer for the Recovery environment, based on https://gist.github.com/karpathy/a4166c7fe253700972fcbc77e4ea32c5#file-pg-pong-py-L68 """

import gym
import numpy as np

# Model Parameters
hidden_n = 4
input_n = 9
output_n = 2

class Prune:

    def __init__(self,
                 render: bool = False,
                 environment: gym.Env,
                 episode_length: int = 300,
                 weights=0):
        """ 
        Optimization Parameters
        learning_rate
        gamma - Reduced effect of reward on earlier actions
        decay_rate - RMSProp decay factor """

        self.render = render
        self.batch_size = batch_size
        self.episode_length = episode_length
        
        # 1 bias,  4 calc quads, 2 map size, 2 drone location, 1 num people

        if weights == 0:
            self.weights = np.random.uniform(low=-5.0, high=5, size=(2, 10))
        else:
            self.weights = weights
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.decay_rate = decay_rate
        
        # Xavier initial weights
        self.model = {
            "w1": np.random.randn(hidden_n, input_n) / np.sqrt(input_n),
            "w2": np.random.randn(output_n, hidden_n) / np.sqrt(hidden_n)
        }

    # takes in an observation matrix, outputs an x and y
    def calc(self, obs: np.array, weights: np.array) -> np.array:
        one = np.ones((1,))
        x = np.concatenate(one, obs)
        np.dot(x, weights)


    def train(self, env: gym.Env):
        """ Trains model using passed environment. """
        episode = 0
        while episode < episode_length: # Continuously train over batches of 5 episodes
            obs = env.reset() # np.array of [x = params, y = agents]
            drone_count = obs.shape()[0]
            episode += 1
            
            for tick in range(self.episode_length):
                if self.render:
                    env.render()
                
                actions = self.act(obs)
                env.step(actions)
            episode += 1

    # Record information for backprop
                
    def act(self, x: np.array) -> np.array:
        """ @param x: np.array (size x = params, y = agents)
        Returns np.array (size x = agents, y = 2) of how each agent moves and
        an np.array (size x = agents, y = hidden neurons)"""
        act_n = np.zeros((len(x), 2))
        
        for i in len(act_n):
            act_n[i][0] = self.calc(x[i], self.weights[0])
            act_n[i][1] = self.calc(x[i], self.weights[1])
        return act_n

