#
# Copyright Michael Groys, 2016
#

import subprocess
import time

from bin_utils import *

usage = "Usage: ptime <command>...\n  Determines excution times of command"

if len(sys.argv)>1 and sys.argv[1] in ["-h", "--help"]:
    print usage
    sys.exit()
else:
    files = expandFiles(sys.argv[1:])

args = sys.argv[1:]

start = time.time()
subprocess.call(args)
end = time.time()

print "\nExecution time: %.3fs"% (end-start)
