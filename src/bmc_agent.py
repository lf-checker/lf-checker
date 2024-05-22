import utils as ut


class BMCAgent:
    def __init__(self, policy):
        self.policy = policy

    def select_action(self, state, loops):
        """Select an action based on the current state and policy."""
        # return self.policy.select_action(state)
        ut.init_bounds(state.unwindset, loops, 4)
        # ut.increment_bound(state.unwindset, "t1.0", 1)
        return state.unwindset
        return "deagle ../tests/test_main.c --unwind 5"

    def update_policy(self, state, action, reward, next_state):
        """Update the policy based on the observed transition."""
        # Placeholder code for updating the policy
        pass

    def config_bounds(self, state):
        unwindset = ""
        for key, value in state.unwindset.items():
            # print(f'Key: {key}, Value: {value}')
            unwindset += f"--unwindset {key}:{value} "

        return unwindset


# Example usage:
# You need to define your policy class and its methods based on your reinforcement learning approach.
# For example, if you are using a Q-learning approach, you would define a Q-table or a Q-network and update it accordingly.
# Then, pass an instance of your policy class when instantiating the BMCagent.
