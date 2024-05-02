import argparse
import subprocess

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
