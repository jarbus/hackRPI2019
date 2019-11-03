import argparse
import numpy as np
import time
import pickle
from env.recovery.recovery import Recovery

def parse_args():
    parser = argparse.ArgumentParser("Reinforcement Learning experiments for multiagent environments")
    # Environment
    parser.add_argument("--max-time-step", type=int, default=100, help="max number of iterations per experiment")
    parser.add_argument("--num-experiments", type=int, default=60000, help="number of eexperiment runs")
    parser.add_argument("--num-drones", type=int, default=5, help="number of drones")
    parser.add_argument("--num-people", type=int, default=5, help="number of people")
    parser.add_argument("--map-size", type=int, nargs=2, default=[100, 100], help="x and y of map")
    parser.add_argument("--base-camp", type=int, nargs=2, default=0, help="x and y of base camp, default random")
    # Core training parameters
    parser.add_argument("--lr", type=float, default=1e-2, help="learning rate for Adam optimizer")
    parser.add_argument("--gamma", type=float, default=0.95, help="discount factor")
    parser.add_argument("--batch-size", type=int, default=1024, help="number of episodes to optimize at the same time")
    # Checkpointing
    parser.add_argument("--exp-name", type=str, default=None, help="name of the experiment")
    parser.add_argument("--save-dir", type=str, default="/tmp/policy/", help="directory in which training state and model should be saved")
    parser.add_argument("--save-rate", type=int, default=1000, help="save model once every time this many episodes are completed")
    parser.add_argument("--load-dir", type=str, default="", help="directory in which training state and model are loaded")
    # Evaluation
    parser.add_argument("--restore", action="store_true", default=False)
    parser.add_argument("--display", action="store_true", default=False)
    parser.add_argument("--benchmark", action="store_true", default=False)
    return parser.parse_args()

def train(arglist):
    # Create environment
    env = Recovery(map_size=arglist.map_size, drone_count=arglist.num_drones, base_camp=arglist.base_camp, num_people=arglist.num_people, debug=True)
    # Create agent trainers

    # Initialize

    # Load previous results, if necessary
    if arglist.load_dir == "":
        arglist.load_dir = arglist.save_dir
    if arglist.display or arglist.restore or arglist.benchmark:
        print('Loading previous state...')
        U.load_state(arglist.load_dir)

    episode_rewards = [0.0]  # sum of rewards for all agents
    agent_rewards = [[0.0] for _ in range(env.n)]  # individual agent reward
    final_ep_rewards = []  # sum of rewards for training curve
    final_ep_ag_rewards = []  # agent rewards for training curve
    agent_info = [[[]]]  # placeholder for benchmarking info
    saver = tf.train.Saver()
    obs_n = env.reset()
    episode_step = 0
    train_step = 0
    t_start = time.time()

    print('Starting iterations...')
    while True:
        # get action
        # environment step
        new_obs_n, rew_n, done_n, info_n = env.step(action_n)
        episode_step += 1
        done = all(done_n)
        terminal = (episode_step >= arglist.max_episode_len)
        # collect experience
        for i, agent in enumerate(trainers):
            agent.experience(obs_n[i], action_n[i], rew_n[i], new_obs_n[i], done_n[i], terminal)
        obs_n = new_obs_n

        for i, rew in enumerate(rew_n):
            episode_rewards[-1] += rew
            agent_rewards[i][-1] += rew

        if done or terminal:
            obs_n = env.reset()
            episode_step = 0
            episode_rewards.append(0)
            for a in agent_rewards:
                a.append(0)
            agent_info.append([[]])

        # increment global step counter
        train_step += 1

        # for benchmarking learned policies
        if arglist.benchmark:
            for i, info in enumerate(info_n):
                agent_info[-1][i].append(info_n['n'])
            if train_step > arglist.benchmark_iters and (done or terminal):
                file_name = arglist.benchmark_dir + arglist.exp_name + '.pkl'
                print('Finished benchmarking, now saving...')
                with open(file_name, 'wb') as fp:
                    pickle.dump(agent_info[:-1], fp)
                break
            continue

        # for displaying learned policies
        if arglist.display:
            time.sleep(0.1)
            env.render()
            continue

        # update all trainers, if not in display or benchmark mode
        loss = None
        for agent in trainers:
            agent.preupdate()
        for agent in trainers:
            loss = agent.update(trainers, train_step)

        # save model, display training output
        if terminal and (len(episode_rewards) % arglist.save_rate == 0):
            U.save_state(arglist.save_dir, saver=saver)
            # print statement depends on whether or not there are adversaries
            if num_adversaries == 0:
                print("steps: {}, episodes: {}, mean episode reward: {}, time: {}".format(
                    train_step, len(episode_rewards), np.mean(episode_rewards[-arglist.save_rate:]), round(time.time()-t_start, 3)))
            else:
                print("steps: {}, episodes: {}, mean episode reward: {}, agent episode reward: {}, time: {}".format(
                    train_step, len(episode_rewards), np.mean(episode_rewards[-arglist.save_rate:]),
                    [np.mean(rew[-arglist.save_rate:]) for rew in agent_rewards], round(time.time()-t_start, 3)))
            t_start = time.time()
            # Keep track of final episode reward
            final_ep_rewards.append(np.mean(episode_rewards[-arglist.save_rate:]))
            for rew in agent_rewards:
                final_ep_ag_rewards.append(np.mean(rew[-arglist.save_rate:]))

        # saves final episode reward for plotting training curve later
        if len(episode_rewards) > arglist.num_episodes:
            rew_file_name = arglist.plots_dir + arglist.exp_name + '_rewards.pkl'
            with open(rew_file_name, 'wb') as fp:
                pickle.dump(final_ep_rewards, fp)
            agrew_file_name = arglist.plots_dir + arglist.exp_name + '_agrewards.pkl'
            with open(agrew_file_name, 'wb') as fp:
                pickle.dump(final_ep_ag_rewards, fp)
            print('...Finished total of {} episodes.'.format(len(episode_rewards)))
            break

if __name__ == '__main__':
    arglist = parse_args()
    arglist.base_camp = [np.random.random(arglist.map_size[0]), np.random.random(arglist.map_size[1])]
    print(arglist)
    train(arglist)
