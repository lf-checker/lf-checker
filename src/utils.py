import argparse
import subprocess
import re

FAILED = "VERIFICATION FAILED"
SUCCESS = "VERIFICATION SUCCESSFUL"
UNKNOWN = "VERIFICATION UNKNOWN"


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parse arguments for LF-checker execution"
    )
    parser.add_argument(
        "--tool",
        type=str,
        default="cbmc",
        help="Select which BMC tool (esbmc, cbmc, deagle..)",
    )
    parser.add_argument("--files", nargs="+", help="List of input files")
    parser.add_argument(
        "--32", action="store_true", help="Set width of machine word to 32"
    )
    parser.add_argument(
        "--64", action="store_true", help="Set width of machine word to 64"
    )
    parser.add_argument("--version", action="version", version="lf-checker v2.0")

    args = parser.parse_args()
    if getattr(args, "32", True) and getattr(args, "64", True):
        parser.error("--32 and --64 cannot be used together")
    elif getattr(args, "32", True):
        machine_word_width = "32"
    else:
        machine_word_width = "64"

    return args.tool, args.files, machine_word_width


def run_command(command):
    try:
        process = subprocess.Popen(
            f"time -p {command}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        output, error = process.communicate()

        # Capture both stdout and stderr
        combined_output = error + output

        if process.returncode == 0:
            return combined_output
        else:
            return f"Command execution failed with error: {combined_output}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


def get_loops(tool, files):
    command = tool + " " + files + " " + "--show-loops"
    pattern = r"(Loop|goto-loop Loop)\s+(?P<loop_name>[^:]+):\s+file\s+(?P<file_path>.*?)\s+line\s+(?P<line_number>\d+)\s*(?:column\s+(?P<column_number>\d+))?\s+function\s+(?P<function_name>\S+)"
    regex = re.compile(pattern)
    loops = {}
    matches = regex.findall(run_command(command))
    for match in matches:
        loop_name = match[2] if match[0] == "goto-loop" else match[1]
        function_name = match[5]
        loops[function_name] = loop_name
    return loops


def increment_bound(unwindset, loopid, depth):
    if loopid in unwindset:
        unwindset[loopid] += depth


def decrement_bound(unwindset, loopid, depth):
    if loopid in unwindset:
        if unwindset[loopid] - depth > 0:
            unwindset[loopid] -= depth
        else:
            unwindset[loopid] = 1


def set_bound(unwindset, loopid, depth):
    if loopid in unwindset:
        unwindset[loopid] = depth


# init loops unrolling depths
def init_bounds(unwindset, loops, depth):
    unwindset.clear()
    for loop in loops.values():
        unwindset[loop] = depth
