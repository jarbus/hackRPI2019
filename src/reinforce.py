""" Policy Gradient optimizer for the Recovery environment, based on https://gist.github.com/karpathy/a4166c7fe253700972fcbc77e4ea32c5#file-pg-pong-py-L68 """

import gym
import numpy as np

# Model Parameters
hidden_n = 300
input_n = 16
output_n = 16

def sigmoid(x: np.array) -> np.array:
    return 1.0/(1.0 + np.exp(-x))

class ReinforceAgent:

    def __init__(self, *,
                 render: bool = False,
                 batch_size: int = 10,
                 episode_length: int = 300,
                 learning_rate: float = 1e-4,
                 gamma: float = 0.99,
                 decay_rate: float = 0.99):
        """ 
        Optimization Parameters
        learning_rate
        gamma - Reduced effect of reward on earlier actions
        decay_rate - RMSProp decay factor """

        self.render = render
        self.batch_size = batch_size
        self.episode_length = episode_length
        
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.decay_rate = decay_rate
        
        # Xavier initial weights
        self.model = {
            "w1": np.random.randn(hidden_n, input_n) / np.sqrt(input_n),
            "w2": np.random.randn(output_n, hidden_n) / np.sqrt(hidden_n)
        }

    def train(self, env: gym.Env):
        """ Trains model using passed environment. """
        obs = env.reset()
        while True: # Continuously train over batches of 10 episodes
            if self.render: env.render()

            
            pass

    def _discount_reward(self, rewards: np.array) -> np.array:
        """ Reduces the magnitude of the reward for the earlier actions. """
        
        discount_rewards = np.zeros_like(rewards)
        summation = 0
        for tick in range(len(rewards), 0, -1):
            summation = summation * self.gamma + rewards[tick]
            discount_rewards[tick] = summation
        return discount_rewards

    def act(self, x: np.array) -> np.array:
        """ Returns an array containing the probabilities of actions, and 
        the values of the hidden layers. """
        
        hidden = np.dot(self.model["w1"], x)
        hidden[hidden < 0] = 0 # Apply lower bound to values (ReLU)
        signal = np.dot(self.model["w2"], hidden)
        return sigmoid(signal), hidden

    def _backprop_batch(self, *,
                        dprob_stack: np.array,
                        hidden_stack: np.array,
                        states: np.array) -> np.array:
        """ Returns gradient for weights, ordered dW1, dW2. """
        
        dW2 = np.dot(hidden_stack.T, dprob_stack).ravel()
        dh = np.outer(dprob_stack, self.model["w2"])
        dh[hidden_stack < 0] = 0 # (PreLu)
        dW1 = np.dot(dh.T, states)
        return dW1, dW2
