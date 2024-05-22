from bmc_state import BMCState
from bmc_agent import BMCAgent
import utils as ut


class BMCEnvironment:
    def __init__(self, initial_state):
        self.current_state = initial_state

    def reset(self, initial_state):
        """Reset the environment to the initial state."""
        self.current_state = initial_state

    def step(self, action):
        """Take a step in the environment based on the given action."""
        # Perform the action and update the environment state
        result = ut.run_command(action)
        if ut.FAILED in result:
            done = True
            self.current_state.verification_result = ut.FAILED
        elif ut.SUCCESS in result:
            action += " --unwinding-assertions"
            if ut.FAILED in ut.run_command(action):
                done = False
                self.current_state.verification_result = ut.FAILED
            else:
                done = True
                self.current_state.verification_result = ut.SUCCESS
        else:
            done = True
            self.current_state.verification_result = ut.UNKNOWN

        next_state = self.current_state
        reward = 0
        return next_state, reward, done


# Example usage:
if __name__ == "__main__":
    initial_state = BMCState(
        current_depth=0,
        unwindset={},
        verification_result=None,
        verification_time=0,
        history=[],
        program_ast=None,
        cpu_usage=0,
        memory_usage=0,
    )
    env = BMCEnvironment(initial_state)
    policy = "policy"
    loops = ut.get_loops("cbmc", "test_main.c")
    agent = BMCAgent(policy)
    unwindset = agent.select_action(initial_state, loops)
    unwindset = agent.config_bounds(initial_state)
    print(unwindset)
    command = "deagle ../tests/test_main.c "
    command += unwindset
    print(command)
    # command = "deagle ../tests/test_main.c --unwind 5"
    next_state, reward, done = env.step(command)
    print(next_state)
