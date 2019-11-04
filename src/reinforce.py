""" Policy Gradient optimizer for the Recovery environment, based on https://gist.github.com/karpathy/a4166c7fe253700972fcbc77e4ea32c5#file-pg-pong-py-L68 """

import gym
import numpy as np

# Model Parameters
hidden_n = 4
input_n = 9
output_n = 2

def sigmoid(x: np.array) -> np.array:
    return 1.0/(1.0 + np.exp(-x))

class ReinforceAgent:

    def __init__(self, *,
                 render: bool = False,
                 batch_size: int = 5,
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
        episode = 0
        batch_counter = 0
        gradient_buffer = { k: np.zeros_like(v) for k,v in self.model }
        rmsprop_cache = { k : np.zeros_like(v) for k,v in self.model }
        recent_reward = 0

        self.toFile("results-%d.txt" % episode)
        
        while True: # Continuously train over batches of 5 episodes
            reward_sum = 0
            obs = env.reset() # np.array of [x = params, y = agents]
            
            drone_count = obs.shape()[0]
            xs = [] # An np array per tick (x = params, y = agents)
            hs = [] # An np array per tick (x = agents, y = neurons)
            dlogps1 = [] # Per tick, the action each agent took
            dlogps2 = []
            drs = []
            
            for tick in range(self.episode_length):
                if self.render: env.render()
                
                actions, hidden = self.act(obs)

                # Record information for backprop
                xs.append(obs)
                hs.append(hidden)
                dlogps1.append([1 - x if x >= 0.5 else -x for x in actions[0,]])
                dlogps2.append([1 - x if x >= 0.5 else -x for x in actions[1,]])

                obs, reward, done, _ = env.step(2*actions - 1)
                recent_reward = reward

                drs.append(reward) # We'll need to copy this for each agent.

            episode += 1
            batch_counter += 1

            discount_rewards = self._discount_reward(drs)
            discount_rewards -= np.mean(discount_rewards)
            discount_rewards /= np.std(discount_rewards)
            
            states = np.stack(xs, axis=2)
            hidden_stack = np.stack(hs, axis=2)
            dlogps1_stack = np.array(dlogps1)
            dlogps2_stack = np.array(dlogps2)

            # Generate a gradient per agent
            for i in range(self.drone_count):
                episode_states = states[:,i,:]
                episode_hidden = hidden_stack[i,:,:]
                episode_dlogp1 = dlogps1_stack[:,i]
                episode_dlogp2 = dlogps2_stack[:,i]

                episode_dlogp1 *= discount_rewards
                episode_dlogp2 *= discount_rewards
                grad1W1, grad1W2 = self._backprop(episode_states, episode_hidden, episode_dlogp1)
                grad2W1, grad2W2 = self._backprop(episode_states, episode_hidden, episode_dlogp2)

                gradient_buffer["w1"] += (grad1W1 + grad2W1)/2
                gradient_buffer["w2"] += (grad1W2 + grad2W2)/2
            
            if batch_counter == self.batch_size:
                for k,v in self.model:
                    rmsprop_cache[k] = self.decay_rate * rmsprop_cache[k] + (1 - self.decay_rate) * gradient_buffer[k]**2
                    self.model[k] += self.learning_rate*gradient_buffer[k] / np.sqrt(rmsprop_cache[k] + 1e-5)
                    gradient_buffer[k] = np.zeros_like(v)
                print("Iteration %d: batch update, most recent reward: %f" % (episode, recent_reward))
                batch_counter = 0

            if episode % 100 == 0:
                print("Writting to file %d..." % episode)
                self.toFile("results-%d.txt" % episode)
                print("Done.")
                
            reward_sum = 0
            obs = env.reset()
                

    def _discount_reward(self, rewards: np.array) -> np.array:
        """ Reduces the magnitude of the reward for the earlier actions. """
        
        discount_rewards = np.zeros_like(rewards)
        summation = 0
        for tick in range(len(rewards), 0, -1):
            summation = summation * self.gamma + rewards[tick]
            discount_rewards[tick] = summation
        return discount_rewards

    def act(self, x: np.array) -> np.array:
        """ @param x: np.array (size x = params, y = agents)
        Returns np.array (size x = agents, y = 2) of how each agent moves and
        an np.array (size x = agents, y = hidden neurons)"""
        
        hidden = np.dot(self.model["w1"], np.transpose(x))
        hidden[hidden < 0] = 0 # Apply lower bound to values (ReLU)
        signal = np.dot(self.model["w2"], hidden)
        return sigmoid(signal), hidden

    def _backprop(self, *,
                        episode_dprob: np.array,
                        episode_stack: np.array,
                        episode_states: np.array) -> np.array:
        """ Returns gradient for weights, ordered dW1, dW2. Does so for one agent. """
        
        dW2 = np.dot(episode_stack.T, episode_dprob).ravel()
        dh = np.outer(episode_dprob, self.model["w2"])
        dh[episode_stack < 0] = 0 # (PreLu)
        dW1 = np.dot(dh.T, episode_states)
        return dW1, dW2

    def toFile(self, name: str):
        f = open(name, "a")
        f.write("w1\n")
        for x in range(input_n):
            for y in range(hidden_n):
                f.write("%d " % self.model["w1"][y,x])
            f.write("\n")

        f.write("w2\n")
        for x in range(hidden_n):
            for y in range(output_n):
                f.write("%d " % self.model["w2"][y,x])
            f.write("\n")

        f.close()
