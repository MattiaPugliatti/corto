#  python tutorials/S09_Frankenstein_Asteroids.py --start 7800 --end 8800

# Utility script to for lung runs that saturate the RAM

import sys
import os
sys.path.append(os.getcwd())
import cortopy as corto
import time

script_path = "tutorials/S09_Frankenstein_Asteroids.py"
TOTAL = 4000
BATCH = 1300         
START = 0

for s in range(START, TOTAL, BATCH):
    e = min(s + BATCH - 1, START + TOTAL - 1)
    corto.Utils.long_run_override(s, e+1, script_path)
    time.sleep(10)

'''
# To make this work, you need to paste this method in the scenario script you want to run

# --- CLI override for idx range (works with Blender's "--" as well) ---
import sys, argparse
def _override_range_via_cli(default_start, default_end):
    # Blender passes script args after a literal "--".
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = argv[1:]
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--start", type=int, dest="start")
    parser.add_argument("--end",   type=int, dest="end")
    # parse_known_args so we ignore any extra scenario flags you may add later
    ns, _ = parser.parse_known_args(argv)
    s = default_start if ns.start is None else ns.start
    e = default_end   if ns.end   is None else ns.end
    if e < s:
        raise ValueError(f"--end ({e}) must be >= --start ({s})")
    print(f"[S09] render range: idx_start={s}, idx_end={e}")
    return s, e
'''