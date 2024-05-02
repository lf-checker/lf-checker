import unittest
import argparse
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bmc_environment import BMCEnvironment


class TestBMCEnvironment(unittest.TestCase):
    def test_verification_failure_reward(self):
        # Get the file path from command line arguments
        program_file = self.program_file

        # Create BMC environment with the program file
        environment = BMCEnvironment(program_file)

        # Assume verification fails for depth 10
        reward = environment.step(10)

        # Verify that reward is +5 for verification failure
        self.assertEqual(reward, 5)

    def test_verification_success_reward(self):
        # Get the file path from command line arguments
        program_file = self.program_file

        # Create BMC environment with the program file
        environment = BMCEnvironment(program_file)

        # Assume verification succeeds for depth 20
        reward = environment.step(5)

        # Verify that reward is -5 for successful verification
        self.assertEqual(reward, -5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run BMC environment tests.")
    parser.add_argument("program_file", type=str, help="Path to the program file")
    args = parser.parse_args()

    # Save the program file path as a global variable
    TestBMCEnvironment.program_file = args.program_file

    # Run the tests
    unittest.main(argv=sys.argv[:1] + ["TestBMCEnvironment"])
