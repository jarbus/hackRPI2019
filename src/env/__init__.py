from gym.envs.registration import register

register(
    id="recovery-v0",
    entry_point="env.recovery:Recovery"
)
