# 
# Copyright Michael Groys, 2014
#

import sys
import os
from argparse import Action as argparseAction

_isWin32 = (sys.platform == "win32")

def isWin():
    return _isWin32

def reopenFileInBinMode(fileobj):
    if sys.platform == "win32":
        import msvcrt
        msvcrt.setmode(fileobj.fileno(), os.O_BINARY )

def copyTermInStream(inStream, outStream):
    while True:
        line = inStream.readline()
        # exit on Ctrl-D
        if line[0] == '\004':
            break
        outStream.write(line)
        #if doFlush:
        #    outStream.flush()
            
def copyStream(inStream, outStream, bufSize = 128*1024):
    if inStream == sys.stdin or outStream==sys.stdout:
        if inStream == sys.stdin and hasattr(inStream, "isatty") and inStream.isatty():
            copyTermInStream(inStream, outStream)
            return
        bufSize = 16*1024
    try:
        while True:
            buf = inStream.read(bufSize)
            if not buf:
                return
            outStream.write(buf)
    except KeyboardInterrupt:
        pass

def normFile(file):
    if _isWin32:
        return os.path.expanduser(file.replace("/","\\"))
    else:
        return os.path.expanduser(file)

def expandFiles(files):
    """Performs wildcard expansion only on windows since on other platforms it is done automatically by shell"""
    if sys.platform == "win32":
        import glob
        expandedFiles = []
        for file in files:
            file = normFile(file)
            expandedFiles.extend(glob.glob(file))
        return expandedFiles
    else:
        return files

def convertPatternsToRegexp(patterns):
    """Converts multiple file name patterns to single regular expression"""
    import fnmatch
    import re
    if not patterns:
        return None
    fullRe = ""
    for pattern in patterns:
        reStr = fnmatch.translate(pattern)
        if fullRe:
            fullRe += "|"
        fullRe += "(" + reStr + ")"
    return re.compile(fullRe)

def unixPath(path):
    if _isWin32:
        return path.replace("\\", "/")
    else:
        return path

def getTreeFiles(baseDir, includePattern=None, excludePattern=None):
    import fnmatch
    import re
    def walkFunc(arg, dir, names):
        (files, includeRegexp, excludeRegexp) = arg
        for f in names:
            filePath = os.path.join(dir, f)
            if not os.path.isfile(filePath):
                continue
            if includeRegexp and not includeRegexp.match(f):
                continue
            if excludeRegexp and excludeRegexp.match(f):
                continue
            files.append(filePath)
    files = []
    if includePattern:
        try:
            includeRegexp = re.compile(fnmatch.translate(includePattern))
        except:
            print >>sys.stderr, "Invalid include file pattern %s" % includePattern
            sys.exit(1)
    else:
        includeRegexp = None
    if excludePattern:
        try:
            excludeRegexp = re.compile(fnmatch.translate(excludePattern))
        except:
            print >>sys.stderr, "Invalid exclude file pattern %s" % excludePattern
            sys.exit(1)
    else:
        excludeRegexp = None
    os.path.walk(baseDir, walkFunc, (files, includeRegexp, excludeRegexp))
    return files

def replace(src, dst):
    """replace(src, dst): Replaces <dst> with <src>
    Works like rename but deletes <dst> before if necessary
    """
    if _isWin32 and os.path.exists(dst):
        os.remove(dst)
    os.rename(src, dst)

class ExtendAction(argparseAction):
    def __call__(self, parser, namespace, values, option_string=None):
        prev = None
        if hasattr(namespace, self.dest):
            prev = getattr(namespace, self.dest)
        if prev is None:
            prev = []
            setattr(namespace, self.dest, prev)
        if values:
            prev.extend(values)

def exitOnInterrupt():
    import signal
    def handler(signum, frame):
        print >>sys.stderr, "Signal %d occurred" % signum
        sys.exit(2)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    

def readlineGenerator(streamIn):
    def generator():
        while True:
            line = streamIn.readline()
            # exit on Ctrl-D
            if line[0] == '\004':
                break
            yield line
    if hasattr(streamIn, "isatty") and streamIn.isatty():
        return generator()
    else:
        return streamIn
    