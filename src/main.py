#!/usr/bin/env python3
import re
import utils as ut


def get_loops(tool, files):
    command = tool + " " + files + " " + "--show-loops"
    pattern = r"(Loop|goto-loop Loop)\s+(?P<loop_name>[^:]+):\s+file\s+(?P<file_path>.*?)\s+line\s+(?P<line_number>\d+)\s*(?:column\s+(?P<column_number>\d+))?\s+function\s+(?P<function_name>\S+)"
    regex = re.compile(pattern)
    loops = {}
    matches = regex.findall(ut.run_command(command))
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


# Example usage:
if __name__ == "__main__":
    tool, files, machine_word_width = ut.parse_arguments()
    result = get_loops(tool, " ".join(files))
    print(result)
    unwindset = {}
    init_bounds(unwindset, result, 5)
    decrement_bound(unwindset, "1", 6)
    print(unwindset)
