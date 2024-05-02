class BMCState:
    def __init__(
        self,
        current_depth,
        verification_result,
        verification_time,
        history,
        program_ast,
        cpu_usage,
        memory_usage,
    ):
        self.current_depth = current_depth
        self.verification_result = verification_result
        self.verification_time = verification_time
        self.history = history
        self.program_ast = program_ast
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage

    def __eq__(self, other):
        """Override equality operator to compare states."""
        return (
            isinstance(other, BMCState)
            and self.current_depth == other.current_depth
            and self.verification_result == other.verification_result
            and self.verification_time == other.verification_time
            and self.history == other.history
            and self.program_ast == other.program_ast
            and self.cpu_usage == other.cpu_usage
            and self.memory_usage == other.memory_usage
        )

    def __hash__(self):
        """Override hash method for using states as keys in dictionaries."""
        return hash(
            (
                self.current_depth,
                self.verification_result,
                self.verification_time,
                tuple(self.history),
                self.program_ast,
                self.cpu_usage,
                self.memory_usage,
            )
        )

    def __repr__(self):
        """String representation of the state."""
        return (
            f"State(depth={self.current_depth}, verification={self.verification_result}, "
            f"time={self.verification_time}, history={self.history}, program_ast={self.program_ast}, "
            f"cpu={self.cpu_usage}, memory={self.memory_usage})"
        )


# Example usage
if __name__ == "__main__":
    state1 = BMCState(
        current_depth=5,
        verification_result="failure",
        verification_time=10,
        history=[],
        program_ast=None,
        cpu_usage=50,
        memory_usage=1024,
    )
    state2 = BMCState(
        current_depth=5,
        verification_result="failure",
        verification_time=10,
        history=[],
        program_ast=None,
        cpu_usage=50,
        memory_usage=1024,
    )
    state3 = BMCState(
        current_depth=3,
        verification_result="success",
        verification_time=5,
        history=[],
        program_ast=None,
        cpu_usage=30,
        memory_usage=512,
    )
    print(state1 == state2)
    print(state1 == state3)

    state_dict = {state1: "State 1", state2: "State 2", state3: "State 3"}
    print(state_dict[state1])
    print(state_dict[state2])
    print(state_dict[state3])
    print(state1)
