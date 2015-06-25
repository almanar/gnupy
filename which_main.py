#
# Copyright Michael Groys, 2015
#
import sys
from bin_utils import *

usage = "Usage: which  <file>...\n  Prints full path of executables"

exitOnInterrupt()

if len(sys.argv)<=1 or (len(sys.argv)>1 and sys.argv[1] in ["-h", "--help"]):
    print usage
    sys.exit()
else:
    files = sys.argv[1:]

if isWin():
    pathDirsSep = ";"
else:
    pathDirsSep = ":"

pathDirs = os.environ.get("PATH", "").split(pathDirsSep)
pathExt = set(ext.lower() for ext in os.environ.get("PATHEXT", "").split(";"))
#print "Extensions:", pathExt

if isWin():
    pathExt.add(".exe")
    pathExt.add(".bat")
    pathExt.add(".cmd")

def getPath(files):
    for d in pathDirs:
        try:
            pathFiles = os.listdir(d)
        except Exception as e:
            #print str(e)
            continue
        #print "Searching in %s" % d
        for pf in os.listdir(d):
            if isWin():
                pathFile = pf.lower()
            else:
                pathFile = pf
            foundExe = None
            for exe in files:
                if not pathExt or os.path.splitext(exe)[1]:
                    if exe == pathFile:
                        foundExe =exe
                        foundPath = pathFile
                        break
                else:
                    pathFileBase, pathFileExt = os.path.splitext(pathFile)
                    if (pathFileExt in pathExt) and exe==pathFileBase:
                        foundExe = exe
                        foundPath = pathFile
            if foundExe:
                print os.path.join(d, foundPath)
                files.remove(foundExe)
            if not files:
                break
        if not files:
            break
    
getPath(files)